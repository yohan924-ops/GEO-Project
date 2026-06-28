"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { CitationShareResponse } from "@/lib/api";
import { CHART_COLORS, CHART_TOOLTIP_STYLE } from "@/lib/chartTheme";

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
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <table style={{ marginTop: 8 }}>
            <thead>
              <tr>
                <th>#</th>
                <th>브랜드</th>
                <th>인용 수</th>
                <th>점유율</th>
                <th>매체별</th>
              </tr>
            </thead>
            <tbody>
              {data.rows.map((r, i) => (
                <tr key={r.brand_id}>
                  <td>{i + 1}</td>
                  <td>{r.brand_name}</td>
                  <td>{r.citation_count}</td>
                  <td>{(r.share * 100).toFixed(1)}%</td>
                  <td className="muted">
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
