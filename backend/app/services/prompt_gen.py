"""Service 1 — keyword/question prompt generation (CLAUDE.md §2, §6.4).

Two modes:
- Test mode (or no Anthropic key): deterministic template generation. No API
  calls, so development incurs no 3rd-party cost.
- LLM mode: Anthropic structured output for natural, on-domain prompts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from app.config import Settings, get_settings


@dataclass
class GeneratedPrompts:
    keywords: list[str]
    questions: list[str]


# Korean consumer-style templates (the tool targets domestic consumers).
_KEYWORD_MODIFIERS = [
    "추천", "후기", "가격", "비교", "순위", "장단점", "사용법", "브랜드",
    "인기", "신상", "할인", "정품", "내구성", "디자인", "성능", "AS",
    "구매처", "최저가", "리뷰", "평점",
]
_QUESTION_TEMPLATES = [
    "{b} 추천해줘",
    "{b} 어디서 사는 게 좋아?",
    "{b} 중에 가성비 좋은 건 뭐야?",
    "{b} 인기 브랜드 알려줘",
    "{b} 살 때 뭘 봐야 해?",
    "{b} 후기 좋은 제품은?",
    "{b} 처음 사는데 추천 부탁해",
    "{b} 가격대별로 정리해줘",
    "요즘 잘나가는 {b} 뭐야?",
    "{b} 선물용으로 뭐가 좋아?",
]


def _category(brand_name: str, industry: str | None) -> str:
    return industry.strip() if industry else f"{brand_name} 같은 제품"


def _template_generate(
    brand_name: str, industry: str | None, keyword_count: int, question_count: int
) -> GeneratedPrompts:
    base = _category(brand_name, industry)
    seeds = [brand_name, base, f"{base} 브랜드"]

    keywords: list[str] = []
    i = 0
    while len(keywords) < keyword_count:
        seed = seeds[i % len(seeds)]
        mod = _KEYWORD_MODIFIERS[i % len(_KEYWORD_MODIFIERS)]
        cycle = i // (len(seeds) * len(_KEYWORD_MODIFIERS))
        suffix = f" {cycle + 1}" if cycle else ""
        kw = f"{seed} {mod}{suffix}".strip()
        if kw not in keywords:
            keywords.append(kw)
        i += 1

    questions: list[str] = []
    j = 0
    while len(questions) < question_count:
        tmpl = _QUESTION_TEMPLATES[j % len(_QUESTION_TEMPLATES)]
        subject = seeds[j % len(seeds)]
        cycle = j // (len(_QUESTION_TEMPLATES) * len(seeds))
        suffix = f" (관련 {cycle + 1})" if cycle else ""
        q = tmpl.format(b=subject) + suffix
        if q not in questions:
            questions.append(q)
        j += 1

    return GeneratedPrompts(keywords=keywords[:keyword_count], questions=questions[:question_count])


_GEN_SCHEMA = {
    "type": "object",
    "properties": {
        "keywords": {"type": "array", "items": {"type": "string"}},
        "questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["keywords", "questions"],
}


async def _llm_generate(
    brand_name: str,
    industry: str | None,
    keyword_count: int,
    question_count: int,
    settings: Settings,
) -> GeneratedPrompts:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    prompt = (
        f"브랜드/제품: {brand_name}\n분야: {industry or '미지정'}\n\n"
        f"국내 소비자가 생성형 검색엔진(ChatGPT 등)에서 이 브랜드/제품군을 찾을 때 쓸 법한 "
        f"검색 키워드 {keyword_count}개와 질문형 프롬프트 {question_count}개를 생성해줘. "
        f"중복 없이, 실제 소비자 말투로."
    )
    resp = await client.messages.create(
        model=settings.gen_model_anthropic,
        max_tokens=8192,
        tools=[
            {
                "name": "emit_prompts",
                "description": "Return generated keywords and question prompts.",
                "input_schema": _GEN_SCHEMA,
            }
        ],
        tool_choice={"type": "tool", "name": "emit_prompts"},
        messages=[{"role": "user", "content": prompt}],
    )
    data = _extract_tool_input(resp)
    keywords = list(dict.fromkeys(data.get("keywords", [])))[:keyword_count]
    questions = list(dict.fromkeys(data.get("questions", [])))[:question_count]
    # Top up from templates if the model returned too few.
    if len(keywords) < keyword_count or len(questions) < question_count:
        fallback = _template_generate(brand_name, industry, keyword_count, question_count)
        keywords = (keywords + fallback.keywords)[:keyword_count]
        questions = (questions + fallback.questions)[:question_count]
    return GeneratedPrompts(keywords=keywords, questions=questions)


def _extract_tool_input(resp: object) -> dict:
    for block in getattr(resp, "content", None) or []:
        if getattr(block, "type", None) == "tool_use":
            data = block.input
            return data if isinstance(data, dict) else json.loads(data)
    return {}


async def generate_prompts(
    brand_name: str,
    industry: str | None = None,
    *,
    keyword_count: int | None = None,
    question_count: int | None = None,
    settings: Settings | None = None,
) -> GeneratedPrompts:
    """Generate keyword and question prompts for a brand (service 1)."""
    settings = settings or get_settings()
    kc = keyword_count if keyword_count is not None else settings.keyword_count
    qc = question_count if question_count is not None else settings.question_count

    if settings.geo_test_mode or not settings.anthropic_api_key:
        return _template_generate(brand_name, industry, kc, qc)
    return await _llm_generate(brand_name, industry, kc, qc, settings)
