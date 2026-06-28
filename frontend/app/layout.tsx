import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// SF Pro is proprietary; Inter is the documented open-source substitute.
const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "600", "700"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "GEO Analyzer",
  description: "Generative Engine Optimization analysis tool",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className={inter.variable}>
      <body>
        <header className="global-nav">
          <div className="global-nav-inner">
            <span className="brand">GEO Analyzer</span>
            <span className="nav-meta">ChatGPT · Gemini · Claude</span>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
