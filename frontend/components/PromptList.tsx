import type { Prompt } from "@/lib/api";

export function PromptList({ prompts }: { prompts: Prompt[] }) {
  const keywords = prompts.filter((p) => p.type === "keyword");
  const questions = prompts.filter((p) => p.type === "question");

  return (
    <div>
      <div className="row" style={{ justifyContent: "space-between" }}>
        <span className="badge">키워드 {keywords.length}</span>
        <span className="badge">질문 {questions.length}</span>
      </div>

      <h3 style={{ marginTop: 16 }}>키워드</h3>
      <div className="chips">
        {keywords.map((p) => (
          <span key={p.id} className="chip">
            {p.text}
          </span>
        ))}
      </div>

      <h3 style={{ marginTop: 16 }}>질문 프롬프트</h3>
      <div className="chips">
        {questions.map((p) => (
          <span key={p.id} className="chip">
            {p.text}
          </span>
        ))}
      </div>
    </div>
  );
}
