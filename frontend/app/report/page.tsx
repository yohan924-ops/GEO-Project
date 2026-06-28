// /report — GEO Analyzer "분석 리포트" design mockup, ported from the Claude
// Design bundled template. Static showcase page (example "나이키" data) that
// demonstrates how a finished analysis renders with the Apple design system.
// The global nav comes from app/layout.tsx; this page adds its own sub-nav.
import Link from "next/link";

const RANKING = [
  { name: "나이키", value: 82, lead: true },
  { name: "아디다스", value: 74 },
  { name: "뉴발란스", value: 61 },
  { name: "아식스", value: 43 },
  { name: "호카", value: 38 },
  { name: "살로몬", value: 29 },
];

const PROVIDER_ROWS = [
  { name: "나이키", mentions: 246, avgRank: 1.8, stability: 0.91, seg: [62, 24, 14] },
  { name: "아디다스", mentions: 222, avgRank: 2.1, stability: 0.88, seg: [55, 28, 17] },
  { name: "뉴발란스", mentions: 183, avgRank: 2.9, stability: 0.79, seg: [48, 30, 22] },
  { name: "아식스", mentions: 129, avgRank: 3.6, stability: 0.71, seg: [40, 33, 27] },
];

const CITATION_LEGEND = [
  { name: "나이키", value: 38, color: "#2997ff" },
  { name: "아디다스", value: 27, color: "#8e8e93" },
  { name: "뉴발란스", value: 18, color: "#636366" },
  { name: "아식스", value: 10, color: "#48484a" },
  { name: "기타", value: 7, color: "#3a3a3c" },
];

const STRATEGIES = [
  {
    priority: 1,
    level: "높음",
    title: "인스타그램 인용 격차 해소",
    rationale:
      "경쟁사 대비 Instagram 온드미디어 인용이 낮습니다. 제품 페이지·룩북을 구조화해 인용 가능성을 높이세요.",
  },
  {
    priority: 2,
    level: "높음",
    title: "질문형 프롬프트 커버리지",
    rationale:
      "\"러닝화 추천\" 류 질문형 프롬프트에서 노출이 불안정합니다. FAQ·비교 콘텐츠로 답변 인용을 확보하세요.",
  },
  {
    priority: 3,
    level: "중간",
    title: "Gemini 노출 안정성 보강",
    rationale:
      "Gemini에서 반복 간 변동성이 큽니다. grounding 소스로 채택되는 권위 도메인 확보가 필요합니다.",
  },
  {
    priority: 4,
    level: "낮음",
    title: "블로그 인용 도메인 다양화",
    rationale:
      "인용이 소수 도메인에 집중되어 있습니다. 다양한 블로그·미디어 채널로 인용 출처를 분산하세요.",
  },
];

const LEVEL_BG: Record<string, string> = {
  높음: "#0066cc",
  중간: "#86868b",
  낮음: "#c7c7cc",
};

export default function ReportPage() {
  return (
    <main style={{ maxWidth: "none", margin: 0, padding: 0 }}>
      <SubNav />

      {/* Hero */}
      <section style={{ background: "var(--canvas)", padding: "72px 24px 48px" }}>
        <div style={{ maxWidth: 1024, margin: "0 auto" }}>
          <div className="eyebrow">생성형 검색 노출 리포트</div>
          <h1
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 52,
              fontWeight: 600,
              letterSpacing: "-0.28px",
              lineHeight: 1.08,
              color: "var(--ink)",
              margin: "4px 0 0",
              maxWidth: 760,
            }}
          >
            나이키는 AI 검색에서 1위로 등장합니다.
          </h1>
          <p
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 22,
              fontWeight: 300,
              lineHeight: 1.45,
              color: "var(--ink-muted-48)",
              margin: "16px 0 0",
              maxWidth: 620,
            }}
          >
            ChatGPT·Gemini·Claude 6,000회 검색 시뮬레이션 기준. 노출·인용 점유율과
            우선순위 전략을 한눈에.
          </p>
          <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginTop: 36 }}>
            <span
              style={{
                fontFamily: "var(--font-display)",
                fontSize: 88,
                fontWeight: 600,
                letterSpacing: "-2px",
                lineHeight: 1,
                color: "var(--primary)",
              }}
            >
              82%
            </span>
            <span
              style={{
                fontFamily: "var(--font-text)",
                fontSize: 17,
                color: "var(--ink-muted-48)",
              }}
            >
              노출 점유율 — 분석 대상 6개 브랜드 중 1위
            </span>
          </div>
        </div>
      </section>

      {/* KPI strip */}
      <section style={{ background: "var(--canvas-parchment)", padding: "40px 24px" }}>
        <div
          style={{
            maxWidth: 1024,
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 24,
          }}
        >
          <Kpi value="82%" label="노출 점유율" delta="▲ 6.2%p" />
          <Kpi value="38%" label="인용 점유율" />
          <Kpi value="6,000" label="검색 호출" />
          <Kpi value="$18.42" label="분석 비용" />
        </div>
      </section>

      {/* Ranking */}
      <section style={{ background: "var(--canvas)", padding: "64px 24px" }}>
        <div style={{ maxWidth: 1024, margin: "0 auto" }}>
          <div className="eyebrow">서비스 2 · 순위 분석</div>
          <h2>브랜드 노출 순위</h2>
          <p className="section-copy muted">
            3사 답변에 등장한 브랜드를 정량 집계했습니다. 막대는 노출 점유율입니다.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 8 }}>
            {RANKING.map((r) => (
              <RankBar key={r.name} {...r} />
            ))}
          </div>

          <h3 style={{ marginTop: 40 }}>provider별 상세</h3>
          <table style={{ marginTop: 12 }}>
            <thead>
              <tr>
                <th>브랜드</th>
                <th>언급 수</th>
                <th>평균 순위</th>
                <th>안정성</th>
                <th style={{ width: 200 }}>엔진 분포</th>
              </tr>
            </thead>
            <tbody>
              {PROVIDER_ROWS.map((row) => (
                <ProvRow key={row.name} {...row} />
              ))}
            </tbody>
          </table>
          <p className="muted" style={{ fontSize: 12, marginTop: 12 }}>
            엔진 분포: <Swatch c="#0066cc" /> ChatGPT · <Swatch c="#86868b" /> Gemini ·{" "}
            <Swatch c="#c7c7cc" /> Claude
          </p>
        </div>
      </section>

      {/* Citation share — dark tile */}
      <section style={{ background: "var(--canvas)", padding: "0 24px 64px" }}>
        <div
          style={{
            maxWidth: 1024,
            margin: "0 auto",
            background: "var(--surface-tile-1)",
            borderRadius: "var(--r-lg)",
            padding: "48px",
            display: "grid",
            gridTemplateColumns: "minmax(220px, 280px) 1fr",
            gap: 48,
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", justifyContent: "center" }}>
            <div
              style={{
                width: 220,
                height: 220,
                borderRadius: "50%",
                background:
                  "conic-gradient(#2997ff 0 38%,#8e8e93 38% 65%,#636366 65% 83%,#48484a 83% 93%,#3a3a3c 93% 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div
                style={{
                  width: 132,
                  height: 132,
                  borderRadius: "50%",
                  background: "var(--surface-tile-1)",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <span
                  style={{
                    fontFamily: "var(--font-display)",
                    fontSize: 36,
                    fontWeight: 600,
                    color: "#fff",
                  }}
                >
                  38%
                </span>
                <span style={{ fontSize: 12, color: "var(--body-muted)" }}>나이키 인용</span>
              </div>
            </div>
          </div>
          <div>
            <div
              className="eyebrow"
              style={{ color: "var(--primary-on-dark)" }}
            >
              서비스 3 · 온드미디어 인용 점유율
            </div>
            <h2 style={{ color: "#fff" }}>인용 소스의 38%가 나이키 채널</h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 20 }}>
              {CITATION_LEGEND.map((l) => (
                <LegendRow key={l.name} {...l} />
              ))}
            </div>
            <p style={{ fontSize: 13, color: "var(--body-muted)", marginTop: 20, marginBottom: 0 }}>
              매핑 인용 612 / 1,240 · 49.4% matched
            </p>
          </div>
        </div>
      </section>

      {/* Strategy */}
      <section style={{ background: "var(--canvas-parchment)", padding: "64px 24px" }}>
        <div style={{ maxWidth: 1024, margin: "0 auto" }}>
          <div className="eyebrow">서비스 4 · 전략 리포트</div>
          <h2>우선순위 전략</h2>
          <p className="section-copy muted">
            노출·인용 갭 분석 결과를 바탕으로 한 실행 전략입니다.
          </p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: 20,
              marginTop: 8,
            }}
          >
            {STRATEGIES.map((s) => (
              <StratCard key={s.priority} {...s} />
            ))}
          </div>
          <div style={{ marginTop: 32 }}>
            <button>전략 리포트 내보내기</button>
          </div>
        </div>
      </section>

      <footer
        style={{
          background: "var(--canvas)",
          borderTop: "1px solid var(--hairline)",
          padding: "32px 24px",
          textAlign: "center",
        }}
      >
        <p style={{ fontSize: 12, color: "var(--ink-muted-48)", margin: 0 }}>
          예시 데이터 · 디자인 목업 — 실제 분석 결과 아님
        </p>
      </footer>
    </main>
  );
}

function SubNav() {
  const items = ["순위", "인용", "전략"];
  return (
    <div
      style={{
        position: "sticky",
        top: 44,
        zIndex: 90,
        background: "rgba(245,245,247,0.8)",
        backdropFilter: "saturate(180%) blur(20px)",
        WebkitBackdropFilter: "saturate(180%) blur(20px)",
        borderBottom: "1px solid var(--hairline)",
      }}
    >
      <div
        style={{
          maxWidth: 1024,
          margin: "0 auto",
          padding: "0 24px",
          height: 52,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
          <span
            style={{
              fontFamily: "var(--font-text)",
              fontSize: 18,
              fontWeight: 600,
              letterSpacing: "-0.3px",
              color: "var(--ink)",
            }}
          >
            나이키
          </span>
          <span style={{ fontSize: 13, color: "var(--ink-muted-48)" }}>
            운동화 · 스포츠웨어
          </span>
        </div>
        <nav style={{ display: "flex", alignItems: "center", gap: 24 }}>
          {items.map((it) => (
            <span
              key={it}
              style={{
                fontFamily: "var(--font-text)",
                fontSize: 14,
                letterSpacing: "-0.224px",
                color: "var(--ink-muted-80)",
              }}
            >
              {it}
            </span>
          ))}
          <Link
            href="/"
            style={{
              background: "var(--primary)",
              color: "#fff",
              borderRadius: 9999,
              padding: "7px 16px",
              fontFamily: "var(--font-text)",
              fontSize: 14,
              letterSpacing: "-0.224px",
              textDecoration: "none",
            }}
          >
            새 분석
          </Link>
        </nav>
      </div>
    </div>
  );
}

function Kpi({ value, label, delta }: { value: string; label: string; delta?: string }) {
  return (
    <div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
        <span
          style={{
            fontFamily: "var(--font-display)",
            fontSize: 40,
            fontWeight: 600,
            letterSpacing: "-0.5px",
            color: "var(--ink)",
          }}
        >
          {value}
        </span>
        {delta && (
          <span style={{ fontSize: 14, fontWeight: 600, color: "var(--primary)" }}>{delta}</span>
        )}
      </div>
      <div style={{ fontSize: 14, color: "var(--ink-muted-48)", marginTop: 4 }}>{label}</div>
    </div>
  );
}

function RankBar({ name, value, lead }: { name: string; value: number; lead?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
      <span
        style={{
          width: 80,
          fontFamily: "var(--font-text)",
          fontSize: 15,
          fontWeight: lead ? 600 : 400,
          color: "var(--ink)",
          textAlign: "right",
        }}
      >
        {name}
      </span>
      <div style={{ flex: 1, height: 28, background: "var(--divider-soft)", borderRadius: 6 }}>
        <div
          style={{
            width: `${value}%`,
            height: "100%",
            background: lead ? "var(--primary)" : "#d2d2d7",
            borderRadius: 6,
          }}
        />
      </div>
      <span
        style={{
          width: 48,
          fontFamily: "var(--font-text)",
          fontSize: 15,
          fontWeight: lead ? 600 : 400,
          color: lead ? "var(--primary)" : "var(--ink-muted-48)",
        }}
      >
        {value}%
      </span>
    </div>
  );
}

function ProvRow({
  name,
  mentions,
  avgRank,
  stability,
  seg,
}: {
  name: string;
  mentions: number;
  avgRank: number;
  stability: number;
  seg: number[];
}) {
  const colors = ["#0066cc", "#86868b", "#c7c7cc"];
  return (
    <tr>
      <td style={{ fontWeight: 600 }}>{name}</td>
      <td>{mentions}</td>
      <td>{avgRank.toFixed(1)}</td>
      <td>{stability.toFixed(2)}</td>
      <td>
        <div style={{ display: "flex", height: 10, borderRadius: 5, overflow: "hidden" }}>
          {seg.map((s, i) => (
            <div key={i} style={{ width: `${s}%`, background: colors[i] }} />
          ))}
        </div>
      </td>
    </tr>
  );
}

function Swatch({ c }: { c: string }) {
  return (
    <span
      style={{
        display: "inline-block",
        width: 9,
        height: 9,
        borderRadius: 2,
        background: c,
        marginRight: 2,
      }}
    />
  );
}

function LegendRow({ name, value, color }: { name: string; value: number; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <span
        style={{ width: 12, height: 12, borderRadius: 3, background: color, flexShrink: 0 }}
      />
      <span style={{ flex: 1, fontSize: 15, color: "#fff" }}>{name}</span>
      <span style={{ fontSize: 15, color: "var(--body-muted)" }}>{value}%</span>
    </div>
  );
}

function StratCard({
  priority,
  level,
  title,
  rationale,
}: {
  priority: number;
  level: string;
  title: string;
  rationale: string;
}) {
  return (
    <div
      style={{
        background: "var(--canvas)",
        border: "1px solid var(--hairline)",
        borderRadius: "var(--r-lg)",
        padding: 24,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: 13, color: "var(--ink-muted-48)" }}>우선순위 {priority}</span>
        <span
          style={{
            fontSize: 12,
            fontWeight: 400,
            letterSpacing: "-0.12px",
            padding: "4px 10px",
            borderRadius: 9999,
            background: LEVEL_BG[level],
            color: "#fff",
          }}
        >
          {level}
        </span>
      </div>
      <h3 style={{ fontSize: 18, margin: "12px 0 8px", letterSpacing: "-0.3px" }}>{title}</h3>
      <p style={{ fontSize: 14, lineHeight: 1.5, color: "var(--ink-muted-80)", margin: 0 }}>
        {rationale}
      </p>
    </div>
  );
}
