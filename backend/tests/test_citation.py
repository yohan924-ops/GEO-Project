"""Service 3 citation mapping + share tests (no API)."""

from sqlmodel import Session

from app.models import (
    Analysis,
    Brand,
    Citation,
    OwnedMedia,
    Prompt,
    ProviderRun,
)
from app.services.citation import (
    build_registry,
    citation_share,
    first_path_segment,
    match_citation,
    normalize_handle,
)


def test_normalize_handle():
    assert normalize_handle("@BrandAlpha") == "brandalpha"
    assert normalize_handle("/brandbeta/") == "brandbeta"


def test_first_path_segment():
    assert first_path_segment("https://instagram.com/brandalpha/p/123") == "brandalpha"
    assert first_path_segment("https://example.com") == ""


def test_match_web_domain_and_subdomain():
    reg = build_registry([OwnedMedia(brand_id=1, media_type="web", domain_or_handle="example.com")])
    assert match_citation("https://example.com/x", "example.com", reg) == (1, "web")
    # subdomain matches the registrable domain
    assert match_citation("https://blog.example.com/x", "blog.example.com", reg) == (1, "web")
    # unrelated domain does not match
    assert match_citation("https://other.org/x", "other.org", reg) == (None, None)


def test_match_sns_handle():
    reg = build_registry(
        [OwnedMedia(brand_id=7, media_type="instagram", domain_or_handle="@brandalpha")]
    )
    assert match_citation(
        "https://instagram.com/brandalpha/p/9", "instagram.com", reg
    ) == (7, "instagram")
    # wrong handle on the same SNS domain does not match
    assert match_citation(
        "https://instagram.com/someoneelse", "instagram.com", reg
    ) == (None, None)


def test_most_specific_domain_wins():
    reg = build_registry(
        [
            OwnedMedia(brand_id=1, media_type="web", domain_or_handle="example.com"),
            OwnedMedia(brand_id=2, media_type="blog", domain_or_handle="blog.example.com"),
        ]
    )
    # blog.example.com is more specific than example.com -> brand 2
    assert match_citation("https://blog.example.com/p", "blog.example.com", reg) == (
        2,
        "blog",
    )


def _setup_analysis_with_citations(session: Session) -> int:
    brand_a = Brand(name="BrandA")
    brand_b = Brand(name="BrandB")
    session.add(brand_a)
    session.add(brand_b)
    session.flush()
    analysis = Analysis(brand_id=brand_a.id)
    session.add(analysis)
    session.flush()
    prompt = Prompt(analysis_id=analysis.id, type="question", text="q")
    session.add(prompt)
    session.flush()
    run = ProviderRun(prompt_id=prompt.id, provider="openai", model="m", run_index=0)
    session.add(run)
    session.flush()

    # 3 citations: 2 -> BrandA (web + instagram), 1 unmatched.
    session.add(
        Citation(provider_run_id=run.id, url="https://a.com/x", domain="a.com")
    )
    session.add(
        Citation(
            provider_run_id=run.id,
            url="https://instagram.com/branda/p/1",
            domain="instagram.com",
        )
    )
    session.add(
        Citation(provider_run_id=run.id, url="https://unknown.org/x", domain="unknown.org")
    )
    # registry: BrandA owns a.com (web) and @branda (instagram)
    session.add(OwnedMedia(brand_id=brand_a.id, media_type="web", domain_or_handle="a.com"))
    session.add(
        OwnedMedia(brand_id=brand_a.id, media_type="instagram", domain_or_handle="@branda")
    )
    session.commit()
    return analysis.id


def test_citation_share(client):
    from app.db import engine

    with Session(engine) as session:
        analysis_id = _setup_analysis_with_citations(session)
        result = citation_share(analysis_id, session)

    assert result.total_citations == 3
    assert result.matched_citations == 2
    assert len(result.rows) == 1
    row = result.rows[0]
    assert row.brand_name == "BrandA"
    assert row.citation_count == 2
    assert row.share == round(2 / 3, 4)
    assert row.by_media_type == {"web": 1, "instagram": 1}


def test_owned_media_crud_and_share_endpoints(client):
    brand = client.post("/brands", json={"name": "브랜드", "industry": "운동화"}).json()
    # register example.com (mock citations include this domain)
    om = client.post(
        f"/brands/{brand['id']}/owned-media",
        json={"media_type": "web", "domain_or_handle": "example.com"},
    )
    assert om.status_code == 201
    listed = client.get(f"/brands/{brand['id']}/owned-media").json()
    assert len(listed) == 1

    gen = client.post(
        "/analyses/generate-prompts",
        json={"brand_id": brand["id"], "keyword_count": 1, "question_count": 1},
    ).json()
    analysis_id = gen["analysis"]["id"]
    client.post(f"/analyses/{analysis_id}/run", json={"repeats": 2})

    share = client.get(f"/analyses/{analysis_id}/citation-share")
    assert share.status_code == 200
    body = share.json()
    assert body["total_citations"] > 0
    assert body["matched_citations"] > 0
    assert body["rows"][0]["brand_name"] == "브랜드"

    # delete owned media -> remap -> no matches
    del_resp = client.delete(f"/owned-media/{om.json()['id']}")
    assert del_resp.status_code == 204
    body2 = client.get(f"/analyses/{analysis_id}/citation-share").json()
    assert body2["matched_citations"] == 0
