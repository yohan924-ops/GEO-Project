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

const COLORS = ["#4f86f7", "#56c596", "#f7b955", "#e06c75", "#9a7bdc", "#43b9c7"];

export function RankingChart({ rankings }: { rankings: RankingRow[] }) {
  const data = rankings.slice(0, 10).map((r) => ({
    name: r.brand_or_service,
    rate: Math.round(r.appearance_rate * 1000) / 10, // %
  }));

  return (
    <div style={{ width: "100%", height: 320 }}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 24, right: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#272b34" />
          <XAxis
            type="number"
            domain={[0, 100]}
            unit="%"
            stroke="#9aa3b2"
            fontSize={12}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={110}
            stroke="#9aa3b2"
            fontSize={12}
          />
          <Tooltip
            formatter={(v: number) => [`${v}%`, "노출률"]}
            contentStyle={{ background: "#181b22", border: "1px solid #272b34" }}
          />
          <Bar dataKey="rate" radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
