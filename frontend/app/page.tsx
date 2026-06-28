"use client";

import { useState } from "react";
import {
  createBrand,
  generatePrompts,
  singleSearch,
  type AnalysisWithPrompts,
  type SingleSearchResponse,
} from "@/lib/api";
import { PromptList } from "@/components/PromptList";
import { SearchResult } from "@/components/SearchResult";

export default function Home() {
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisWithPrompts | null>(null);

  const [searchPrompt, setSearchPrompt] = useState("");
  const [searching, setSearching] = useState(false);
  const [search, setSearch] = useState<SingleSearchResponse | null>(null);

  async function onGenerate() {
    setError(null);
    setLoading(true);
    try {
      const brand = await createBrand(name.trim(), industry.trim());
      // Phase 1: keep counts small for fast, free dev runs.
      const res = await generatePrompts(brand.id, 20, 20);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  async function onSearch() {
    setError(null);
    setSearching(true);
    try {
      setSearch(await singleSearch(searchPrompt.trim()));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSearching(false);
    }
  }

  return (
    <main>
      <h1>GEO Analyzer</h1>
      <p className="muted">
        생성형 검색엔진(ChatGPT · Gemini · Claude) 노출·인용 분석 — Phase 1
      </p>

      <section className="panel">
        <h2 style={{ marginTop: 0, fontSize: 18 }}>① 프롬프트 생성</h2>
        <div className="row">
          <div>
            <label>브랜드 / 제품명</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="예: 나이키"
            />
          </div>
          <div>
            <label>분야 (선택)</label>
            <input
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              placeholder="예: 운동화"
            />
          </div>
          <button onClick={onGenerate} disabled={loading || !name.trim()}>
            {loading ? "생성 중…" : "프롬프트 생성"}
          </button>
        </div>
        {result && (
          <div style={{ marginTop: 16 }}>
            <span className="badge">analysis #{result.analysis.id}</span>{" "}
            <span className="badge">status: {result.analysis.status}</span>
            <PromptList prompts={result.prompts} />
          </div>
        )}
      </section>

      <section className="panel">
        <h2 style={{ marginTop: 0, fontSize: 18 }}>② 3사 1회 검색 (어댑터 검증)</h2>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>프롬프트</label>
            <input
              style={{ width: "100%" }}
              value={searchPrompt}
              onChange={(e) => setSearchPrompt(e.target.value)}
              placeholder="예: 운동화 추천해줘"
            />
          </div>
          <button onClick={onSearch} disabled={searching || !searchPrompt.trim()}>
            {searching ? "검색 중…" : "검색"}
          </button>
        </div>
        {search && (
          <div style={{ marginTop: 12 }}>
            {search.test_mode && (
              <span className="badge">테스트 모드 (mock · 무과금)</span>
            )}
            <SearchResult results={search.results} />
          </div>
        )}
      </section>

      {error && <p className="error">⚠ {error}</p>}
    </main>
  );
}
