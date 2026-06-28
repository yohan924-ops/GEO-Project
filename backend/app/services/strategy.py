"""Service 4 — GEO strategy report (gap analysis -> prioritized strategies).

Consumes the service 2 ranking and service 3 citation-share results for an
analysis, computes the target brand's gaps, and produces a prioritized list of
strategies. Template mode is deterministic and API-free; LLM mode uses
Anthropic structured output for richer recommendations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from sqlmodel import Session

from app.config import Settings, get_settings
from app.models import Analysis, Brand
from app.services.citation import CitationShareResult, citation_share
from app.services.ranking import RankingRow, aggregate_rankings


@dataclass
class StrategyItem:
    priority: int
    title: str
    rationale: str
    action_items: list[str]


@dataclass
class GapContext:
    target: str
    target_appearance_rate: float
    target_avg_rank: float
    target_stability: float
    target_citation_share: float
    weakest_provider: str | None
    top_competitors: list[str]


def _build_context(
    target: str, rankings: list[RankingRow], share: CitationShareResult
) -> GapContext:
    tl = target.lower()
    target_row = next((r for r in rankings if r.brand_or_service.lower() == tl), None)
    competitors = [r for r in rankings if r.brand_or_service.lower() != tl]

    weakest_provider: str | None = None
    if target_row and target_row.by_provider:
        weakest_provider = min(target_row.by_provider, key=target_row.by_provider.get)
    elif competitors and competitors[0].by_provider:
        # Where the leading competitor is strongest is the biggest gap to close.
        weakest_provider = max(
            competitors[0].by_provider, key=competitors[0].by_provider.get
        )

    target_share_row = next(
        (r for r in share.rows if r.brand_name.lower() == tl), None
    )

    return GapContext(
        target=target,
        target_appearance_rate=target_row.appearance_rate if target_row else 0.0,
        target_avg_rank=target_row.avg_rank if target_row else 0.0,
        target_stability=target_row.stability if target_row else 0.0,
        target_citation_share=target_share_row.share if target_share_row else 0.0,
        weakest_provider=weakest_provider,
        top_competitors=[r.brand_or_service for r in competitors[:3]],
    )


_PROVIDER_LABEL = {"openai": "ChatGPT", "gemini": "Gemini", "anthropic": "Claude"}


def _template_strategy(ctx: GapContext) -> list[StrategyItem]:
    items: list[StrategyItem] = []
    comp = ", ".join(ctx.top_competitors) if ctx.top_competitors else "경쟁 브랜드"

    # 1) Exposure gap — the core GEO objective.
    if ctx.target_appearance_rate < 0.5:
        items.append(
            StrategyItem(
                priority=1,
                title="생성형 검색 노출 강화",
                rationale=(
                    f"'{ctx.target}'의 답변 노출률이 "
                    f"{ctx.target_appearance_rate * 100:.0f}%로 낮습니다. "
                    f"현재 {comp} 등이 답변을 점유하고 있어 인지도 확보가 시급합니다."
                ),
                action_items=[
                    "제품/브랜드를 명확히 정의한 구조화 콘텐츠(FAQ·비교표·스펙) 발행",
                    "권위 있는 외부 매체·리뷰에 브랜드가 인용되도록 PR/제휴 확대",
                    "핵심 질문 프롬프트에 직접 답하는 페이지를 온드미디어에 구축",
                ],
            )
        )
    else:
        items.append(
            StrategyItem(
                priority=1,
                title="노출 우위 유지 및 평균 순위 개선",
                rationale=(
                    f"'{ctx.target}'는 노출률 {ctx.target_appearance_rate * 100:.0f}%로 "
                    f"이미 등장하나 평균 순위가 {ctx.target_avg_rank:.1f}위입니다. "
                    "상위 언급 빈도를 높이는 데 집중해야 합니다."
                ),
                action_items=[
                    "대표 키워드에서 1순위로 언급되도록 핵심 메시지 표준화",
                    "비교 콘텐츠에서 우위 속성을 명시적으로 강조",
                ],
            )
        )

    # 2) Citation share gap (service 3).
    items.append(
        StrategyItem(
            priority=2,
            title="온드미디어 인용 점유율 확대",
            rationale=(
                f"'{ctx.target}'의 인용 점유율이 "
                f"{ctx.target_citation_share * 100:.0f}%입니다. "
                "AI 답변이 출처로 삼는 인용 URL에 자사 채널이 더 많이 포함되어야 합니다."
            ),
            action_items=[
                "웹·블로그·인스타·페북 등 온드미디어를 레지스트리에 모두 등록·정비",
                "인용되기 쉬운 형식(요약·통계·인용문)으로 콘텐츠 재구성",
                "공식 도메인 권위(피인용·백링크)를 높여 인용 우선순위 확보",
            ],
        )
    )

    # 3) Provider-specific gap.
    if ctx.weakest_provider:
        label = _PROVIDER_LABEL.get(ctx.weakest_provider, ctx.weakest_provider)
        items.append(
            StrategyItem(
                priority=3,
                title=f"{label} 채널 집중 공략",
                rationale=(
                    f"{label}에서의 노출이 상대적으로 약합니다. "
                    "엔진별 인용 소스 특성에 맞춘 최적화가 필요합니다."
                ),
                action_items=[
                    f"{label}가 자주 인용하는 소스 유형 분석 후 해당 채널에 콘텐츠 배치",
                    "엔진별 답변을 정기 모니터링해 노출 변화 추적",
                ],
            )
        )

    # 4) Stability.
    if 0 < ctx.target_stability < 0.7:
        items.append(
            StrategyItem(
                priority=4,
                title="노출 안정성 개선",
                rationale=(
                    f"반복 검색 시 노출 안정성이 "
                    f"{ctx.target_stability * 100:.0f}%로 변동이 큽니다. "
                    "일관된 언급을 위해 신호의 폭과 일관성을 키워야 합니다."
                ),
                action_items=[
                    "동일 주제를 다채널·다형식으로 반복 발행해 신호 강화",
                    "최신성 유지를 위해 콘텐츠를 주기적으로 갱신",
                ],
            )
        )

    return items


_STRATEGY_SCHEMA = {
    "type": "object",
    "properties": {
        "strategies": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "priority": {"type": "integer"},
                    "title": {"type": "string"},
                    "rationale": {"type": "string"},
                    "action_items": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["priority", "title", "rationale", "action_items"],
            },
        }
    },
    "required": ["strategies"],
}


def _context_text(ctx: GapContext, rankings: list[RankingRow]) -> str:
    top = "\n".join(
        f"- {r.brand_or_service}: 노출률 {r.appearance_rate * 100:.0f}%, "
        f"평균순위 {r.avg_rank:.1f}, 안정성 {r.stability * 100:.0f}%"
        for r in rankings[:8]
    )
    return (
        f"분석 대상 브랜드: {ctx.target}\n"
        f"대상 노출률: {ctx.target_appearance_rate * 100:.0f}%\n"
        f"대상 평균순위: {ctx.target_avg_rank:.1f}\n"
        f"대상 인용 점유율: {ctx.target_citation_share * 100:.0f}%\n"
        f"가장 약한 엔진: {ctx.weakest_provider or '미상'}\n"
        f"상위 경쟁 브랜드: {', '.join(ctx.top_competitors) or '없음'}\n\n"
        f"노출 순위 상위:\n{top}"
    )


async def _llm_strategy(
    ctx: GapContext, rankings: list[RankingRow], settings: Settings
) -> list[StrategyItem]:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    resp = await client.messages.create(
        model=settings.gen_model_anthropic,
        max_tokens=4096,
        tools=[
            {
                "name": "emit_strategies",
                "description": "Return prioritized GEO strategies.",
                "input_schema": _STRATEGY_SCHEMA,
            }
        ],
        tool_choice={"type": "tool", "name": "emit_strategies"},
        messages=[
            {
                "role": "user",
                "content": (
                    "다음은 생성형 검색엔진 노출·인용 분석 결과다. 이 브랜드가 GEO "
                    "점유율을 높이기 위한 실행 전략을 우선순위(priority: 1이 최우선) 순으로 "
                    "생성해줘. 각 전략은 근거(rationale)와 구체적 실행 항목(action_items)을 "
                    "포함해야 한다.\n\n" + _context_text(ctx, rankings)
                ),
            }
        ],
    )
    for block in getattr(resp, "content", None) or []:
        if getattr(block, "type", None) == "tool_use":
            data = block.input if isinstance(block.input, dict) else json.loads(block.input)
            return [
                StrategyItem(
                    priority=int(s.get("priority", i + 1)),
                    title=s["title"],
                    rationale=s.get("rationale", ""),
                    action_items=list(s.get("action_items", [])),
                )
                for i, s in enumerate(data.get("strategies", []))
            ]
    return _template_strategy(ctx)


async def generate_strategy(
    analysis_id: int, session: Session, settings: Settings | None = None
) -> list[StrategyItem]:
    settings = settings or get_settings()
    analysis = session.get(Analysis, analysis_id)
    if not analysis:
        raise ValueError(f"analysis {analysis_id} not found")
    brand = session.get(Brand, analysis.brand_id)
    target = brand.name if brand else "브랜드"

    rankings = aggregate_rankings(analysis_id, session)
    share = citation_share(analysis_id, session)
    ctx = _build_context(target, rankings, share)

    if settings.geo_test_mode or not settings.anthropic_api_key:
        return _template_strategy(ctx)
    return await _llm_strategy(ctx, rankings, settings)
