// Centralized backend API client (CLAUDE.md §7: all backend calls go through lib/).
// When no backend is reachable (e.g. the Vercel deploy with no API server),
// each call transparently falls back to client-side demo data (see ./demo).
import * as demo from "./demo";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

// fetch() throws a TypeError when the host is unreachable / blocked (no
// backend, mixed content, connection refused) — that's our cue to use demo
// data. HTTP error responses (thrown as "API <status>") are re-thrown.
async function tryReal<T>(real: () => Promise<T>, fallback: () => T): Promise<T> {
  try {
    return await real();
  } catch (e) {
    if (e instanceof TypeError) return fallback();
    throw e;
  }
}

export interface Brand {
  id: number;
  name: string;
  industry: string | null;
}

export interface Prompt {
  id: number;
  type: "keyword" | "question";
  text: string;
}

export interface Analysis {
  id: number;
  brand_id: number;
  status: string;
  progress: number;
  total_calls: number;
  cost_usd: number;
  created_at: string;
}

export interface AnalysisWithPrompts {
  analysis: Analysis;
  prompts: Prompt[];
}

export interface Citation {
  url: string;
  title: string | null;
  snippet: string | null;
  domain: string;
}

export interface ProviderResult {
  provider: string;
  model: string;
  answer_text: string;
  citations: Citation[];
  usage: Record<string, number>;
  cost_usd: number;
  latency_ms: number;
}

export interface SingleSearchResponse {
  prompt: string;
  test_mode: boolean;
  results: ProviderResult[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export function createBrand(name: string, industry: string): Promise<Brand> {
  return tryReal(
    () =>
      request<Brand>("/brands", {
        method: "POST",
        body: JSON.stringify({ name, industry: industry || null }),
      }),
    () => demo.demoCreateBrand(name, industry),
  );
}

export function generatePrompts(
  brandId: number,
  keywordCount?: number,
  questionCount?: number,
): Promise<AnalysisWithPrompts> {
  return tryReal(
    () =>
      request<AnalysisWithPrompts>("/analyses/generate-prompts", {
        method: "POST",
        body: JSON.stringify({
          brand_id: brandId,
          keyword_count: keywordCount,
          question_count: questionCount,
        }),
      }),
    () => demo.demoGeneratePrompts(brandId, keywordCount, questionCount),
  );
}

export function singleSearch(prompt: string): Promise<SingleSearchResponse> {
  return tryReal(
    () =>
      request<SingleSearchResponse>("/search/single", {
        method: "POST",
        body: JSON.stringify({ prompt }),
      }),
    () => demo.demoSingleSearch(prompt),
  );
}

export interface RankingRow {
  brand_or_service: string;
  mention_count: number;
  appearance_rate: number;
  avg_rank: number;
  stability: number;
  by_provider: Record<string, number>;
}

export interface RankingResponse {
  analysis: Analysis;
  total_runs: number;
  rankings: RankingRow[];
}

export function runAnalysis(
  analysisId: number,
  repeats?: number,
): Promise<Analysis> {
  return tryReal(
    () =>
      request<Analysis>(`/analyses/${analysisId}/run`, {
        method: "POST",
        body: JSON.stringify({ repeats }),
      }),
    () => demo.demoRunAnalysis(analysisId, repeats),
  );
}

export function getRankings(analysisId: number): Promise<RankingResponse> {
  return tryReal(
    () => request<RankingResponse>(`/analyses/${analysisId}/rankings`),
    () => demo.demoGetRankings(analysisId),
  );
}

export function getAnalysis(analysisId: number): Promise<Analysis> {
  return tryReal(
    () => request<Analysis>(`/analyses/${analysisId}`),
    () => demo.demoGetAnalysis(analysisId),
  );
}

export type MediaType = "web" | "instagram" | "blog" | "facebook";

export interface OwnedMedia {
  id: number;
  brand_id: number;
  media_type: string;
  domain_or_handle: string;
}

export function listOwnedMedia(brandId: number): Promise<OwnedMedia[]> {
  return tryReal(
    () => request<OwnedMedia[]>(`/brands/${brandId}/owned-media`),
    () => demo.demoListOwnedMedia(brandId),
  );
}

export function createOwnedMedia(
  brandId: number,
  mediaType: MediaType,
  domainOrHandle: string,
): Promise<OwnedMedia> {
  return tryReal(
    () =>
      request<OwnedMedia>(`/brands/${brandId}/owned-media`, {
        method: "POST",
        body: JSON.stringify({ media_type: mediaType, domain_or_handle: domainOrHandle }),
      }),
    () => demo.demoCreateOwnedMedia(brandId, mediaType, domainOrHandle),
  );
}

export function deleteOwnedMedia(id: number): Promise<void> {
  return tryReal(
    async () => {
      const res = await fetch(`${API_BASE}/owned-media/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(`API ${res.status}`);
    },
    () => demo.demoDeleteOwnedMedia(id),
  );
}

export interface CitationShareRow {
  brand_id: number;
  brand_name: string;
  citation_count: number;
  share: number;
  by_media_type: Record<string, number>;
}

export interface CitationShareResponse {
  analysis_id: number;
  total_citations: number;
  matched_citations: number;
  rows: CitationShareRow[];
}

export function getCitationShare(
  analysisId: number,
): Promise<CitationShareResponse> {
  return tryReal(
    () => request<CitationShareResponse>(`/analyses/${analysisId}/citation-share`),
    () => demo.demoGetCitationShare(analysisId),
  );
}

export interface StrategyItem {
  id: number;
  analysis_id: number;
  priority: number;
  title: string;
  rationale: string | null;
  action_items: string[];
}

export interface StrategyResponse {
  analysis_id: number;
  strategies: StrategyItem[];
}

export function generateStrategy(analysisId: number): Promise<StrategyResponse> {
  return tryReal(
    () =>
      request<StrategyResponse>(`/analyses/${analysisId}/strategy`, {
        method: "POST",
      }),
    () => demo.demoGenerateStrategy(analysisId),
  );
}

export function getStrategy(analysisId: number): Promise<StrategyResponse> {
  return tryReal(
    () => request<StrategyResponse>(`/analyses/${analysisId}/strategy`),
    () => demo.demoGenerateStrategy(analysisId),
  );
}
