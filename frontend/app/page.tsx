"use client";

import { useState } from "react";
import {
  createBrand,
  generatePrompts,
  generateStrategy,
  getCitationShare,
  getRankings,
  runAnalysis,
  singleSearch,
  type AnalysisWithPrompts,
  type CitationShareResponse,
  type RankingResponse,
  type SingleSearchResponse,
  type StrategyResponse,
} from "@/lib/api";
import { PromptList } from "@/components/PromptList";
import { SearchResult } from "@/components/SearchResult";
import { RankingChart } from "@/components/RankingChart";
import { RankingTable } from "@/components/RankingTable";
import { OwnedMediaRegistry } from "@/components/OwnedMediaRegistry";
import { CitationShare } from "@/components/CitationShare";
import { StrategyReport } from "@/components/StrategyReport";

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

  const [loadingStrategy, setLoadingStrategy] = useState(false);
  const [strategy, setStrategy] = useState<StrategyResponse | null>(null);

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

  async function onGenerateStrategy() {
    if (!result) return;
    setError(null);
    setLoadingStrategy(true);
    try {
      setStrategy(await generateStrategy(result.analysis.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoadingStrategy(false);
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
      <section className="hero">
        <h1>GEO Analyzer</h1>
        <p>
          생성형 검색엔진이 당신의 브랜드를 어떻게 말하는지 측정하고, 점유율을 높일
          전략을 제시합니다.
        </p>
      </section>

      <section className="panel">
        <p className="eyebrow">단계 01</p>
        <h2>프롬프트 생성</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          브랜드/제품명으로 국내 소비자가 검색할 키워드와 질문 프롬프트를 생성합니다.
        </p>
        <div className="row" style={{ marginTop: 20 }}>
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
        <p className="eyebrow">단계 02 · 서비스 2</p>
        <h2>순위 분석</h2>
        <p className="muted" style={{ marginTop: 0, marginBottom: 20 }}>
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
        <p className="eyebrow">단계 03 · 서비스 3</p>
        <h2>온드미디어 인용 점유율</h2>
        <p className="muted" style={{ marginTop: 0, marginBottom: 20 }}>
          브랜드의 온드미디어(웹·블로그·인스타·페북)를 등록하면, 검색 답변의 인용
          URL을 도메인·핸들로 매핑해 브랜드별 인용 점유율을 집계합니다.
        </p>
        {result ? (
          <>
            <OwnedMediaRegistry brandId={result.analysis.brand_id} />
            <div style={{ marginTop: 16 }}>
              <button className="btn-ghost" onClick={onLoadShare} disabled={loadingShare}>
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
        <p className="eyebrow">단계 04 · 서비스 4</p>
        <h2>GEO 전략 리포트</h2>
        <p className="muted" style={{ marginTop: 0, marginBottom: 20 }}>
          02·03 분석 결과를 바탕으로 갭을 분석해 GEO 점유율을 높이기 위한 우선순위
          전략을 생성합니다.
        </p>
        {result ? (
          <>
            <button onClick={onGenerateStrategy} disabled={loadingStrategy}>
              {loadingStrategy ? "생성 중…" : "전략 리포트 생성"}
            </button>
            {strategy && (
              <div style={{ marginTop: 16 }}>
                <StrategyReport strategies={strategy.strategies} />
              </div>
            )}
          </>
        ) : (
          <p className="muted">먼저 프롬프트를 생성하세요.</p>
        )}
      </section>

      <section className="panel">
        <p className="eyebrow">검증</p>
        <h2>3사 1회 검색</h2>
        <p className="muted" style={{ marginTop: 0, marginBottom: 20 }}>
          단일 프롬프트를 ChatGPT·Gemini·Claude에 한 번씩 호출해 답변과 인용 파싱을
          확인합니다.
        </p>
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
