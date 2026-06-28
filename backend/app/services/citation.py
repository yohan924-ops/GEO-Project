"""Service 3 — citation -> domain -> brand mapping and share aggregation (§6.6).

1. Extract the domain from each citation URL (subdomain-aware).
2. Match against the OwnedMedia registry: web/blog by domain, SNS by handle.
3. Set Citation.matched_brand_id / media_type.
4. Aggregate per-brand citation count and share with pandas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse

import pandas as pd
from sqlmodel import Session, select

from app.models import Brand, Citation, OwnedMedia, Prompt, ProviderRun
from app.providers.base import extract_domain

_SNS_DOMAINS = {"instagram": "instagram.com", "facebook": "facebook.com"}


def normalize_handle(value: str) -> str:
    """Normalize an SNS handle: drop @, leading slash, lowercase."""
    return value.strip().lstrip("@").strip("/").lower()


def first_path_segment(url: str) -> str:
    path = urlparse(url if "://" in url else f"//{url}").path
    parts = [p for p in path.split("/") if p]
    return parts[0].lower() if parts else ""


@dataclass
class _Registry:
    # registrable domain -> (brand_id, media_type), longest-match wins
    domains: dict[str, tuple[int, str]] = field(default_factory=dict)
    # (sns_domain, handle) -> (brand_id, media_type)
    handles: dict[tuple[str, str], tuple[int, str]] = field(default_factory=dict)


def build_registry(entries: list[OwnedMedia]) -> _Registry:
    reg = _Registry()
    for e in entries:
        if e.media_type in _SNS_DOMAINS:
            sns_domain = _SNS_DOMAINS[e.media_type]
            reg.handles[(sns_domain, normalize_handle(e.domain_or_handle))] = (
                e.brand_id,
                e.media_type,
            )
        else:
            reg.domains[extract_domain(e.domain_or_handle)] = (e.brand_id, e.media_type)
    return reg


def match_citation(
    url: str, domain: str, reg: _Registry
) -> tuple[int | None, str | None]:
    """Return (brand_id, media_type) for a citation, or (None, None)."""
    domain = domain or extract_domain(url)

    # SNS: domain + handle (first path segment).
    handle = first_path_segment(url)
    if handle:
        hit = reg.handles.get((domain, handle))
        if hit:
            return hit

    # web/blog: exact or subdomain of a registered registrable domain.
    # Prefer the most specific (longest) registered domain.
    best: tuple[int, str] | None = None
    best_len = -1
    for reg_domain, val in reg.domains.items():
        if domain == reg_domain or domain.endswith("." + reg_domain):
            if len(reg_domain) > best_len:
                best = val
                best_len = len(reg_domain)
    if best:
        return best
    return None, None


def _citations_for_analysis(analysis_id: int, session: Session) -> list[Citation]:
    return list(
        session.exec(
            select(Citation)
            .join(ProviderRun, ProviderRun.id == Citation.provider_run_id)
            .join(Prompt, Prompt.id == ProviderRun.prompt_id)
            .where(Prompt.analysis_id == analysis_id)
        ).all()
    )


def map_citations(analysis_id: int, session: Session) -> int:
    """(Re)map all citations of an analysis against the current registry.

    Idempotent: recomputes matched_brand_id/media_type each call. Returns the
    number of citations matched to a brand.
    """
    registry = build_registry(list(session.exec(select(OwnedMedia)).all()))
    citations = _citations_for_analysis(analysis_id, session)
    matched = 0
    for c in citations:
        brand_id, media_type = match_citation(c.url, c.domain, registry)
        c.matched_brand_id = brand_id
        c.media_type = media_type
        session.add(c)
        if brand_id is not None:
            matched += 1
    session.commit()
    return matched


@dataclass
class CitationShareRow:
    brand_id: int
    brand_name: str
    citation_count: int
    share: float  # of all citations in the analysis
    by_media_type: dict[str, int] = field(default_factory=dict)


@dataclass
class CitationShareResult:
    total_citations: int
    matched_citations: int
    rows: list[CitationShareRow]


def citation_share(analysis_id: int, session: Session) -> CitationShareResult:
    """Aggregate per-brand citation share (runs mapping first, idempotent)."""
    map_citations(analysis_id, session)
    citations = _citations_for_analysis(analysis_id, session)
    total = len(citations)
    if total == 0:
        return CitationShareResult(0, 0, [])

    df = pd.DataFrame(
        [
            {
                "brand_id": c.matched_brand_id,
                "media_type": c.media_type,
                "domain": c.domain,
            }
            for c in citations
        ]
    )
    matched_df = df[df["brand_id"].notna()].copy()
    matched_count = len(matched_df)
    if matched_count == 0:
        return CitationShareResult(total, 0, [])

    matched_df["brand_id"] = matched_df["brand_id"].astype(int)
    brand_ids = [int(b) for b in matched_df["brand_id"].unique()]
    names = {
        b.id: b.name
        for b in session.exec(select(Brand).where(Brand.id.in_(brand_ids))).all()
    }

    rows: list[CitationShareRow] = []
    for brand_id, bdf in matched_df.groupby("brand_id"):
        by_media = {
            str(k): int(v) for k, v in bdf["media_type"].value_counts().items()
        }
        rows.append(
            CitationShareRow(
                brand_id=int(brand_id),
                brand_name=names.get(int(brand_id), f"brand#{int(brand_id)}"),
                citation_count=len(bdf),
                share=round(len(bdf) / total, 4),
                by_media_type=by_media,
            )
        )

    rows.sort(key=lambda r: -r.citation_count)
    return CitationShareResult(total, matched_count, rows)
