// Product-landing page — implements the Apple-style "Product Landing" design
// template (alternating light/dark/parchment full-bleed tiles + footer).
// Adapted from the Claude Design template; placeholder product copy replaced
// with GEO Analyzer messaging. The global nav comes from app/layout.tsx.
import Link from "next/link";

const PRODUCT_SHADOW = "rgba(0, 0, 0, 0.22) 3px 5px 30px 0";

function CTAs() {
  const base: React.CSSProperties = {
    fontFamily: "var(--font-text)",
    fontSize: 17,
    letterSpacing: "-0.374px",
    borderRadius: 9999,
    padding: "11px 22px",
    textDecoration: "none",
    lineHeight: 1,
    display: "inline-flex",
    alignItems: "center",
  };
  return (
    <div style={{ display: "flex", gap: 20, marginTop: 24, flexWrap: "wrap", justifyContent: "center" }}>
      <Link
        href="/"
        style={{ ...base, background: "var(--primary)", color: "#fff" }}
      >
        분석 시작
      </Link>
      <Link
        href="/"
        style={{
          ...base,
          background: "transparent",
          color: "var(--primary)",
          border: "1px solid var(--primary)",
        }}
      >
        더 알아보기
      </Link>
    </div>
  );
}

const tileBase: React.CSSProperties = {
  padding: "80px 24px",
  textAlign: "center",
};
const innerBase: React.CSSProperties = {
  maxWidth: 1440,
  margin: "0 auto",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
};

export default function LandingPage() {
  return (
    <main style={{ margin: 0, padding: 0, maxWidth: "none" }}>
      {/* Tile 1 — light hero */}
      <section style={{ ...tileBase, background: "var(--canvas)" }}>
        <div style={innerBase}>
          <div
            style={{
              fontFamily: "var(--font-text)",
              fontSize: 14,
              fontWeight: 600,
              letterSpacing: "-0.224px",
              color: "var(--primary)",
              marginBottom: 8,
            }}
          >
            GEO Analyzer
          </div>
          <h1
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 56,
              fontWeight: 600,
              letterSpacing: "-0.28px",
              lineHeight: 1.07,
              color: "var(--ink)",
              margin: 0,
            }}
          >
            AI 검색을 측정하다
          </h1>
          <p
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 28,
              fontWeight: 400,
              letterSpacing: "0.196px",
              lineHeight: 1.14,
              color: "var(--ink)",
              margin: "12px 0 0",
            }}
          >
            ChatGPT·Gemini·Claude가 당신의 브랜드를 어떻게 말하는지.
          </p>
          <CTAs />
          <div
            style={{
              marginTop: 48,
              width: 300,
              height: 420,
              borderRadius: 44,
              background: "linear-gradient(155deg, #454a53 0%, #2c2f36 58%, #1d1f24 100%)",
              boxShadow: PRODUCT_SHADOW,
            }}
          />
        </div>
      </section>

      {/* Tile 2 — dark */}
      <section style={{ ...tileBase, background: "var(--surface-tile-1)" }}>
        <div style={innerBase}>
          <h2
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 40,
              fontWeight: 600,
              lineHeight: 1.1,
              color: "#fff",
              margin: 0,
            }}
          >
            노출 순위 분석
          </h2>
          <p
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 28,
              fontWeight: 400,
              letterSpacing: "0.196px",
              color: "var(--body-muted)",
              margin: "12px 0 0",
            }}
          >
            3사 답변에 등장하는 브랜드를 정량 집계.
          </p>
          <CTAs />
          <div
            style={{
              marginTop: 48,
              width: 300,
              height: 320,
              borderRadius: 64,
              background: "linear-gradient(155deg, #454a53 0%, #2c2f36 58%, #1d1f24 100%)",
              boxShadow: PRODUCT_SHADOW,
            }}
          />
        </div>
      </section>

      {/* Tile 3 — parchment */}
      <section style={{ ...tileBase, background: "var(--canvas-parchment)" }}>
        <div style={innerBase}>
          <h2
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 40,
              fontWeight: 600,
              lineHeight: 1.1,
              color: "var(--ink)",
              margin: 0,
            }}
          >
            인용 점유율 & 전략
          </h2>
          <p
            style={{
              fontFamily: "var(--font-display)",
              fontSize: 28,
              fontWeight: 400,
              letterSpacing: "0.196px",
              color: "var(--ink)",
              margin: "12px 0 0",
            }}
          >
            온드미디어 인용을 매핑하고, 갭을 메우는 전략까지.
          </p>
          <CTAs />
          <div
            style={{
              marginTop: 48,
              width: 280,
              height: 280,
              borderRadius: 120,
              background: "linear-gradient(155deg, #f4f6f8 0%, #dce1e8 52%, #c6cdd8 100%)",
              boxShadow: PRODUCT_SHADOW,
            }}
          />
        </div>
      </section>

      <LandingFooter />
    </main>
  );
}

function LandingFooter() {
  const columns: { title: string; links: string[] }[] = [
    { title: "제품", links: ["프롬프트 생성", "순위 분석", "인용 점유율", "전략 리포트"] },
    { title: "분석 엔진", links: ["ChatGPT", "Gemini", "Claude"] },
    { title: "리소스", links: ["대시보드", "문서", "API"] },
  ];
  return (
    <footer
      style={{
        background: "var(--canvas-parchment)",
        color: "var(--ink-muted-80)",
        padding: "64px 24px",
        borderTop: "1px solid var(--hairline)",
      }}
    >
      <div
        style={{
          maxWidth: 1024,
          margin: "0 auto",
          display: "flex",
          gap: 64,
          flexWrap: "wrap",
        }}
      >
        {columns.map((col) => (
          <div key={col.title}>
            <div
              style={{
                fontFamily: "var(--font-text)",
                fontSize: 14,
                fontWeight: 600,
                letterSpacing: "-0.224px",
                color: "var(--ink)",
                marginBottom: 8,
              }}
            >
              {col.title}
            </div>
            {col.links.map((l) => (
              <div key={l}>
                <Link
                  href="/"
                  style={{
                    fontFamily: "var(--font-text)",
                    fontSize: 14,
                    lineHeight: 2.2,
                    color: "var(--ink-muted-80)",
                    textDecoration: "none",
                  }}
                >
                  {l}
                </Link>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div
        style={{
          maxWidth: 1024,
          margin: "32px auto 0",
          paddingTop: 16,
          borderTop: "1px solid var(--hairline)",
          fontFamily: "var(--font-text)",
          fontSize: 12,
          color: "var(--ink-muted-48)",
        }}
      >
        GEO Analyzer — Generative Engine Optimization 분석 도구. 데모/내부용.
      </div>
    </footer>
  );
}
