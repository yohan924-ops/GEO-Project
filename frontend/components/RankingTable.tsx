import type { RankingRow } from "@/lib/api";

const PROVIDERS = ["openai", "gemini", "anthropic"] as const;
const PROVIDER_LABEL: Record<string, string> = {
  openai: "ChatGPT",
  gemini: "Gemini",
  anthropic: "Claude",
};

function pct(v: number) {
  return `${(v * 100).toFixed(1)}%`;
}

export function RankingTable({ rankings }: { rankings: RankingRow[] }) {
  return (
    <table
      style={{ width: "100%", borderCollapse: "collapse", marginTop: 12, fontSize: 13 }}
    >
      <thead>
        <tr style={{ textAlign: "left", color: "var(--ink-muted-48)" }}>
          <th style={{ padding: "8px 6px" }}>#</th>
          <th style={{ padding: "8px 6px" }}>브랜드/서비스</th>
          <th style={{ padding: "8px 6px" }}>노출률</th>
          <th style={{ padding: "8px 6px" }}>빈도</th>
          <th style={{ padding: "8px 6px" }}>평균순위</th>
          <th style={{ padding: "8px 6px" }}>안정성</th>
          {PROVIDERS.map((p) => (
            <th key={p} style={{ padding: "8px 6px" }}>
              {PROVIDER_LABEL[p]}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rankings.map((r, i) => (
          <tr key={r.brand_or_service} style={{ borderTop: "1px solid var(--divider-soft)" }}>
            <td style={{ padding: "8px 6px" }}>{i + 1}</td>
            <td style={{ padding: "8px 6px" }}>{r.brand_or_service}</td>
            <td style={{ padding: "8px 6px" }}>{pct(r.appearance_rate)}</td>
            <td style={{ padding: "8px 6px" }}>{r.mention_count}</td>
            <td style={{ padding: "8px 6px" }}>{r.avg_rank.toFixed(2)}</td>
            <td style={{ padding: "8px 6px" }}>{pct(r.stability)}</td>
            {PROVIDERS.map((p) => (
              <td key={p} style={{ padding: "8px 6px" }} className="muted">
                {r.by_provider[p] != null ? pct(r.by_provider[p]) : "—"}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
