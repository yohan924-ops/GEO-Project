// Client-side demo data — used as an automatic fallback when no backend is
// reachable (e.g. the Vercel deployment with no API server). Mirrors the
// backend's mock behavior so every screen works offline, with no LLM cost.
import type {
  Analysis,
  AnalysisWithPrompts,
  Brand,
  CitationShareResponse,
  OwnedMedia,
  Prompt,
  RankingResponse,
  SingleSearchResponse,
  StrategyResponse,
} from "./api";

const BRANDS = ["BrandAlpha", "BrandBeta", "BrandGamma"];
const PROVIDERS: [string, string][] = [
  ["openai", "gpt-4o"],
  ["gemini", "gemini-2.0-flash"],
  ["anthropic", "claude-sonnet-4-6"],
];
const KW_MODS = ["추천", "후기", "가격", "비교", "순위", "장단점", "사용법", "브랜드",
  "인기", "신상", "할인", "정품", "내구성", "디자인", "성능", "AS", "구매처", "최저가", "리뷰", "평점"];
const Q_TMPL = ["{b} 추천해줘", "{b} 어디서 사는 게 좋아?", "{b} 중에 가성비 좋은 건 뭐야?",
  "{b} 인기 브랜드 알려줘", "{b} 살 때 뭘 봐야 해?", "{b} 후기 좋은 제품은?",
  "{b} 처음 사는데 추천 부탁해", "{b} 가격대별로 정리해줘", "요즘 잘나가는 {b} 뭐야?", "{b} 선물용으로 뭐가 좋아?"];
const MOCK_DOMAINS = ["example.com", "blog.example.org", "instagram.com"];

function hash(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) >>> 0;
  return h;
}
function normDomain(v: string): string {
  return v.toLowerCase().replace(/^@/, "").replace(/^https?:\/\//, "").replace(/^www\./, "").split("/")[0];
}

let nextId = 1;
const brands = new Map<number, Brand>();
const analyses = new Map<number, { analysis: Analysis; brandId: number; promptCount: number; totalRuns: number }>();
let owned: OwnedMedia[] = [];

export function demoCreateBrand(name: string, industry: string): Brand {
  const brand: Brand = { id: nextId++, name: name || "브랜드", industry: industry || null };
  brands.set(brand.id, brand);
  return brand;
}

export function demoGeneratePrompts(brandId: number, kc = 20, qc = 20): AnalysisWithPrompts {
  const brand = brands.get(brandId) ?? { id: brandId, name: "브랜드", industry: null };
  const cat = brand.industry || `${brand.name} 같은 제품`;
  const seeds = [brand.name, cat, `${cat} 브랜드`];
  const prompts: Prompt[] = [];
  const seenK = new Set<string>();
  for (let i = 0; prompts.filter((p) => p.type === "keyword").length < kc; i++) {
    const kw = `${seeds[i % seeds.length]} ${KW_MODS[i % KW_MODS.length]}`.trim();
    if (!seenK.has(kw)) { seenK.add(kw); prompts.push({ id: nextId++, type: "keyword", text: kw }); }
  }
  const seenQ = new Set<string>();
  for (let j = 0; prompts.filter((p) => p.type === "question").length < qc; j++) {
    const q = Q_TMPL[j % Q_TMPL.length].replace("{b}", seeds[j % seeds.length]);
    if (!seenQ.has(q)) { seenQ.add(q); prompts.push({ id: nextId++, type: "question", text: q }); }
  }
  const analysis: Analysis = {
    id: nextId++, brand_id: brandId, status: "done", progress: 1,
    total_calls: 0, cost_usd: 0, created_at: new Date(0).toISOString(),
  };
  analyses.set(analysis.id, { analysis, brandId, promptCount: prompts.length, totalRuns: 0 });
  return { analysis, prompts };
}

export function demoRunAnalysis(analysisId: number, repeats = 3): Analysis {
  const rec = analyses.get(analysisId);
  if (!rec) throw new Error("demo: analysis not found");
  rec.totalRuns = rec.promptCount * PROVIDERS.length * repeats;
  rec.analysis = { ...rec.analysis, status: "done", progress: 1, total_calls: rec.totalRuns, cost_usd: 0 };
  return rec.analysis;
}

export function demoGetRankings(analysisId: number): RankingResponse {
  const rec = analyses.get(analysisId);
  const total = rec?.totalRuns || 360;
  const base = [1.0, 0.983, 0.965];
  const avg = [2.07, 2.12, 2.17];
  const stab = [1.0, 0.975, 0.975];
  const anth = [1.0, 1.0, 0.95];
  const rankings = BRANDS.map((name, i) => ({
    brand_or_service: name,
    mention_count: Math.round(base[i] * total),
    appearance_rate: base[i],
    avg_rank: avg[i],
    stability: stab[i],
    by_provider: { openai: base[i], gemini: base[i], anthropic: anth[i] },
  }));
  return { analysis: rec?.analysis ?? demoStubAnalysis(analysisId), total_runs: total, rankings };
}

export function demoListOwnedMedia(brandId: number): OwnedMedia[] {
  return owned.filter((o) => o.brand_id === brandId);
}
export function demoCreateOwnedMedia(brandId: number, media_type: string, domain_or_handle: string): OwnedMedia {
  const om: OwnedMedia = { id: nextId++, brand_id: brandId, media_type, domain_or_handle };
  owned.push(om);
  return om;
}
export function demoDeleteOwnedMedia(id: number): void {
  owned = owned.filter((o) => o.id !== id);
}

export function demoGetCitationShare(analysisId: number): CitationShareResponse {
  const rec = analyses.get(analysisId);
  const total = rec?.totalRuns || 360;
  const brand = rec ? brands.get(rec.brandId) : undefined;
  const matchedOM = (rec ? demoListOwnedMedia(rec.brandId) : owned).filter((o) =>
    MOCK_DOMAINS.includes(normDomain(o.domain_or_handle)),
  );
  const per = Math.round(total / 3);
  const byMedia: Record<string, number> = {};
  let matched = 0;
  matchedOM.forEach((o) => { byMedia[o.media_type] = (byMedia[o.media_type] || 0) + per; matched += per; });
  const rows = matched > 0
    ? [{
        brand_id: rec?.brandId ?? 0,
        brand_name: brand?.name ?? "브랜드",
        citation_count: matched,
        share: Math.round((matched / total) * 10000) / 10000,
        by_media_type: byMedia,
      }]
    : [];
  return { analysis_id: analysisId, total_citations: total, matched_citations: matched, rows };
}

export function demoGenerateStrategy(analysisId: number): StrategyResponse {
  const rec = analyses.get(analysisId);
  const b = (rec ? brands.get(rec.brandId)?.name : undefined) ?? "브랜드";
  const items = [
    { priority: 1, title: "생성형 검색 노출 강화",
      rationale: `'${b}'의 답변 노출률이 0%로 낮습니다. 현재 BrandAlpha, BrandBeta 등이 답변을 점유하고 있어 인지도 확보가 시급합니다.`,
      action_items: ["제품/브랜드를 명확히 정의한 구조화 콘텐츠(FAQ·비교표·스펙) 발행",
        "권위 있는 외부 매체·리뷰에 브랜드가 인용되도록 PR/제휴 확대",
        "핵심 질문 프롬프트에 직접 답하는 페이지를 온드미디어에 구축"] },
    { priority: 2, title: "온드미디어 인용 점유율 확대",
      rationale: `'${b}'의 인용 점유율이 낮습니다. AI 답변이 출처로 삼는 인용 URL에 자사 채널이 더 많이 포함되어야 합니다.`,
      action_items: ["웹·블로그·인스타·페북 등 온드미디어를 레지스트리에 모두 등록·정비",
        "인용되기 쉬운 형식(요약·통계·인용문)으로 콘텐츠 재구성",
        "공식 도메인 권위(피인용·백링크)를 높여 인용 우선순위 확보"] },
    { priority: 3, title: "Gemini 채널 집중 공략",
      rationale: "Gemini에서의 노출이 상대적으로 약합니다. 엔진별 인용 소스 특성에 맞춘 최적화가 필요합니다.",
      action_items: ["Gemini가 자주 인용하는 소스 유형 분석 후 해당 채널에 콘텐츠 배치",
        "엔진별 답변을 정기 모니터링해 노출 변화 추적"] },
  ];
  return { analysis_id: analysisId, strategies: items.map((s) => ({ id: nextId++, analysis_id: analysisId, ...s })) };
}

export function demoSingleSearch(prompt: string): SingleSearchResponse {
  const results = PROVIDERS.map(([id, model]) => {
    const seed = hash(id + prompt);
    const order = BRANDS.slice(seed % 3).concat(BRANDS.slice(0, seed % 3));
    const doms = MOCK_DOMAINS;
    return {
      provider: id, model: `mock-${model}`,
      answer_text: `[mock:${id}] For '${prompt.slice(0, 40)}', popular options include ${order.join(", ")}.`,
      citations: order.map((b, i) => ({
        url: `https://${doms[i]}/p/${(seed >> (i * 4)) % 1000}`,
        title: `${b} review`, snippet: "mock snippet", domain: doms[i],
      })),
      usage: { input_tokens: 10, output_tokens: 30 }, cost_usd: 0, latency_ms: 1,
    };
  });
  return { prompt, test_mode: true, results };
}

function demoStubAnalysis(id: number): Analysis {
  return { id, brand_id: 0, status: "done", progress: 1, total_calls: 0, cost_usd: 0, created_at: new Date(0).toISOString() };
}

export function demoGetAnalysis(id: number): Analysis {
  return analyses.get(id)?.analysis ?? demoStubAnalysis(id);
}
