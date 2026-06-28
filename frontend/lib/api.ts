// Centralized backend API client (CLAUDE.md §7: all backend calls go through lib/).

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

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
  return request<Brand>("/brands", {
    method: "POST",
    body: JSON.stringify({ name, industry: industry || null }),
  });
}

export function generatePrompts(
  brandId: number,
  keywordCount?: number,
  questionCount?: number,
): Promise<AnalysisWithPrompts> {
  return request<AnalysisWithPrompts>("/analyses/generate-prompts", {
    method: "POST",
    body: JSON.stringify({
      brand_id: brandId,
      keyword_count: keywordCount,
      question_count: questionCount,
    }),
  });
}

export function singleSearch(prompt: string): Promise<SingleSearchResponse> {
  return request<SingleSearchResponse>("/search/single", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
}
