"""Service 1 prompt generation tests (template mode, no API)."""

import pytest

from app.services.prompt_gen import generate_prompts


@pytest.mark.asyncio
async def test_generates_requested_counts():
    result = await generate_prompts(
        "테스트브랜드", "운동화", keyword_count=100, question_count=100
    )
    assert len(result.keywords) == 100
    assert len(result.questions) == 100


@pytest.mark.asyncio
async def test_keywords_unique():
    result = await generate_prompts("브랜드", "가방", keyword_count=100, question_count=10)
    assert len(set(result.keywords)) == len(result.keywords)


@pytest.mark.asyncio
async def test_questions_unique_and_mention_subject():
    result = await generate_prompts("브랜드", None, keyword_count=10, question_count=80)
    assert len(set(result.questions)) == len(result.questions)
    assert all(q.strip() for q in result.questions)


@pytest.mark.asyncio
async def test_small_counts():
    result = await generate_prompts("X", "Y", keyword_count=3, question_count=3)
    assert len(result.keywords) == 3
    assert len(result.questions) == 3
