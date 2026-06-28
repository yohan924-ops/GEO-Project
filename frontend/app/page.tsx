"use client";

import { useState } from "react";
import {
  createBrand,
  generatePrompts,
  getCitationShare,
  getRankings,
  runAnalysis,
  singleSearch,
  type AnalysisWithPrompts,
  type CitationShareResponse,
  type RankingResponse,
  type SingleSearchResponse,
} from "@/lib/api";
import { PromptList } from "@/components/PromptList";
import { SearchResult } from "@/components/SearchResult";
import { RankingChart } from "@/components/RankingChart";
import { RankingTable } from "@/components/RankingTable";
import { OwnedMediaRegistry } from "@/components/OwnedMediaRegistry";
import { CitationShare } from "@/components/CitationShare";

export default function Home() {
  const [name, setName] = useState("");
  const [industry, setIndustry] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisWithPrompts | null>(null);

  const [searchPrompt, setSearchPrompt] = useState("");
  const [searching, setSearching] = useState(false);
  const [search, setSearch] = useState<SingleSearchResponse | null>(null);

  const [running, setRunning] = useState(false);
  const [ranking, setRanking] = useState<RankingResponse | null>(null);

  const [loadingShare, setLoadingShare] = useState(false);
  const [share, setShare] = useState<CitationShareResponse | null>(null);

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

  async function onRun() {
    if (!result) return;
    setError(null);
    setRunning(true);
    setRanking(null);
    try {
      // Phase 2: small repeat count for fast, free dev runs.
      await runAnalysis(result.analysis.id, 3);
      setRanking(await getRankings(result.analysis.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  async function onLoadShare() {
    if (!result) return;
    setError(null);
    setLoadingShare(true);
    try {
      setShare(await getCitationShare(result.analysis.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoadingShare(false);
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
        <h2 style={{ marginTop: 0, fontSize: 18 }}>② 순위 분석 (서비스 2)</h2>
        <p className="muted" style={{ fontSize: 13, marginTop: 0 }}>
          생성된 프롬프트를 3사에 반복 검색해 답변에 등장하는 브랜드/서비스의 노출
          순위·빈도·안정성을 집계합니다.
        </p>
        <button onClick={onRun} disabled={running || !result}>
          {running ? "분석 중…" : result ? "순위 분석 실행" : "먼저 프롬프트를 생성하세요"}
        </button>
        {ranking && (
          <div style={{ marginTop: 16 }}>
            <span className="badge">총 {ranking.total_runs}회 검색</span>{" "}
            <span className="badge">cost ${ranking.analysis.cost_usd.toFixed(4)}</span>
            {ranking.rankings.length > 0 ? (
              <>
                <h3 style={{ marginTop: 16 }}>노출률 상위</h3>
                <RankingChart rankings={ranking.rankings} />
                <RankingTable rankings={ranking.rankings} />
              </>
            ) : (
              <p className="muted">집계된 멘션이 없습니다.</p>
            )}
          </div>
        )}
      </section>

      <section className="panel">
        <h2 style={{ marginTop: 0, fontSize: 18 }}>③ 온드미디어 인용 점유율 (서비스 3)</h2>
        <p className="muted" style={{ fontSize: 13, marginTop: 0 }}>
          브랜드의 온드미디어(웹·블로그·인스타·페북)를 등록하면, 검색 답변의 인용
          URL을 도메인·핸들로 매핑해 브랜드별 인용 점유율을 집계합니다.
        </p>
        {result ? (
          <>
            <OwnedMediaRegistry brandId={result.analysis.brand_id} />
            <div style={{ marginTop: 16 }}>
              <button onClick={onLoadShare} disabled={loadingShare}>
                {loadingShare ? "집계 중…" : "인용 점유율 집계"}
              </button>
              <span className="muted" style={{ fontSize: 12, marginLeft: 10 }}>
                ※ 먼저 ② 순위 분석을 실행해 검색 데이터를 만들어야 합니다.
              </span>
            </div>
            {share && (
              <div style={{ marginTop: 16 }}>
                <CitationShare data={share} />
              </div>
            )}
          </>
        ) : (
          <p className="muted">먼저 프롬프트를 생성하세요.</p>
        )}
      </section>

      <section className="panel">
        <h2 style={{ marginTop: 0, fontSize: 18 }}>④ 3사 1회 검색 (어댑터 검증)</h2>
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
