import type { ProviderResult } from "@/lib/api";

const LABELS: Record<string, string> = {
  openai: "ChatGPT (OpenAI)",
  gemini: "Gemini (Google)",
  anthropic: "Claude (Anthropic)",
};

export function SearchResult({ results }: { results: ProviderResult[] }) {
  return (
    <div>
      {results.map((r) => (
        <div key={r.provider} className="provider-card">
          <h3>
            {LABELS[r.provider] ?? r.provider}{" "}
            <span className="badge">{r.model}</span>{" "}
            <span className="badge">{r.latency_ms}ms</span>{" "}
            <span className="badge">${r.cost_usd.toFixed(4)}</span>
          </h3>
          <p style={{ fontSize: 14, lineHeight: 1.5 }}>{r.answer_text}</p>
          <div className="muted" style={{ fontSize: 13 }}>
            인용 {r.citations.length}건
          </div>
          {r.citations.map((c, i) => (
            <div key={i} className="citation">
              <a href={c.url} target="_blank" rel="noreferrer">
                {c.title ?? c.url}
              </a>{" "}
              <span className="muted">· {c.domain}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
