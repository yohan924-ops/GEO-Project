"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RankingRow } from "@/lib/api";
import { CHART_COLORS, CHART_TOOLTIP_STYLE } from "@/lib/chartTheme";

export function RankingChart({ rankings }: { rankings: RankingRow[] }) {
  const data = rankings.slice(0, 10).map((r) => ({
    name: r.brand_or_service,
    rate: Math.round(r.appearance_rate * 1000) / 10, // %
  }));

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 24, right: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis
            type="number"
            domain={[0, 100]}
            unit="%"
            stroke="#7a7a7a"
            fontSize={12}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={110}
            stroke="#7a7a7a"
            fontSize={12}
          />
          <Tooltip
            formatter={(v: number) => [`${v}%`, "노출률"]}
            contentStyle={CHART_TOOLTIP_STYLE}
          />
          <Bar dataKey="rate" radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
