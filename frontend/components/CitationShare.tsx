"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { CitationShareResponse } from "@/lib/api";

const COLORS = ["#4f86f7", "#56c596", "#f7b955", "#e06c75", "#9a7bdc", "#43b9c7"];

export function CitationShare({ data }: { data: CitationShareResponse }) {
  const chart = data.rows.slice(0, 6).map((r) => ({
    name: r.brand_name,
    value: r.citation_count,
  }));

  return (
    <div>
      <div className="row" style={{ gap: 8 }}>
        <span className="badge">전체 인용 {data.total_citations}</span>
        <span className="badge">매핑됨 {data.matched_citations}</span>
      </div>

      {chart.length > 0 ? (
        <>
          <div style={{ width: "100%", height: 280 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={chart}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(e) => e.name}
                >
                  {chart.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: "#181b22", border: "1px solid #272b34" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              marginTop: 8,
              fontSize: 13,
            }}
          >
            <thead>
              <tr style={{ textAlign: "left", color: "var(--muted)" }}>
                <th style={{ padding: "8px 6px" }}>#</th>
                <th style={{ padding: "8px 6px" }}>브랜드</th>
                <th style={{ padding: "8px 6px" }}>인용 수</th>
                <th style={{ padding: "8px 6px" }}>점유율</th>
                <th style={{ padding: "8px 6px" }}>매체별</th>
              </tr>
            </thead>
            <tbody>
              {data.rows.map((r, i) => (
                <tr key={r.brand_id} style={{ borderTop: "1px solid var(--border)" }}>
                  <td style={{ padding: "8px 6px" }}>{i + 1}</td>
                  <td style={{ padding: "8px 6px" }}>{r.brand_name}</td>
                  <td style={{ padding: "8px 6px" }}>{r.citation_count}</td>
                  <td style={{ padding: "8px 6px" }}>{(r.share * 100).toFixed(1)}%</td>
                  <td style={{ padding: "8px 6px" }} className="muted">
                    {Object.entries(r.by_media_type)
                      .map(([k, v]) => `${k}:${v}`)
                      .join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <p className="muted">매핑된 인용이 없습니다. 온드미디어를 등록하고 분석을 실행하세요.</p>
      )}
    </div>
  );
}
