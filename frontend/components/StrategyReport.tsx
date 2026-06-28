import type { StrategyItem } from "@/lib/api";

export function StrategyReport({ strategies }: { strategies: StrategyItem[] }) {
  if (strategies.length === 0) {
    return <p className="muted">생성된 전략이 없습니다.</p>;
  }
  return (
    <div>
      {strategies.map((s) => (
        <div key={s.id} className="provider-card">
          <h3 style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              className="badge"
              style={{ background: "var(--accent)", color: "#fff", border: "none" }}
            >
              우선순위 {s.priority}
            </span>
            {s.title}
          </h3>
          {s.rationale && (
            <p style={{ fontSize: 14, lineHeight: 1.5 }} className="muted">
              {s.rationale}
            </p>
          )}
          <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 14, lineHeight: 1.6 }}>
            {s.action_items.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
