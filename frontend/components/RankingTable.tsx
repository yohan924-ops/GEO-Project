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
    <table style={{ marginTop: 12 }}>
      <thead>
        <tr>
          <th>#</th>
          <th>브랜드/서비스</th>
          <th>노출률</th>
          <th>빈도</th>
          <th>평균순위</th>
          <th>안정성</th>
          {PROVIDERS.map((p) => (
            <th key={p}>{PROVIDER_LABEL[p]}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rankings.map((r, i) => (
          <tr key={r.brand_or_service}>
            <td>{i + 1}</td>
            <td>{r.brand_or_service}</td>
            <td>{pct(r.appearance_rate)}</td>
            <td>{r.mention_count}</td>
            <td>{r.avg_rank.toFixed(2)}</td>
            <td>{pct(r.stability)}</td>
            {PROVIDERS.map((p) => (
              <td key={p} className="muted">
                {r.by_provider[p] != null ? pct(r.by_provider[p]) : "—"}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
