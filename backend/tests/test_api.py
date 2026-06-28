"""API endpoint tests (test mode; all provider calls mocked)."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["test_mode"] is True


def test_brand_crud(client):
    resp = client.post("/brands", json={"name": "나이키", "industry": "운동화"})
    assert resp.status_code == 201
    brand = resp.json()
    assert brand["name"] == "나이키"

    listed = client.get("/brands").json()
    assert any(b["id"] == brand["id"] for b in listed)

    got = client.get(f"/brands/{brand['id']}").json()
    assert got["industry"] == "운동화"


def test_generate_prompts_flow(client):
    brand = client.post("/brands", json={"name": "브랜드", "industry": "가방"}).json()
    resp = client.post(
        "/analyses/generate-prompts",
        json={"brand_id": brand["id"], "keyword_count": 12, "question_count": 8},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["analysis"]["status"] == "done"
    assert len(body["prompts"]) == 20
    types = {p["type"] for p in body["prompts"]}
    assert types == {"keyword", "question"}

    analysis_id = body["analysis"]["id"]
    prompts = client.get(f"/analyses/{analysis_id}/prompts").json()
    assert len(prompts) == 20


def test_generate_prompts_missing_brand(client):
    resp = client.post(
        "/analyses/generate-prompts", json={"brand_id": 9999}
    )
    assert resp.status_code == 404


def test_single_search_all_providers(client):
    resp = client.post("/search/single", json={"prompt": "운동화 추천해줘"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["test_mode"] is True
    providers = {r["provider"] for r in body["results"]}
    assert providers == {"openai", "gemini", "anthropic"}
    for r in body["results"]:
        assert r["answer_text"]
        assert len(r["citations"]) == 3
        assert all(c["domain"] for c in r["citations"])
