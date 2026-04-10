import { useEffect, useState } from "react";
import { askSKUQuestion } from "../services/api";

const starterQuestions = [
  "Why was this pricing strategy chosen?",
  "How does this SKU compare to competitors?",
  "What is the margin situation here?",
  "What happens if we use the suggested price?",
];

export default function SKUChatbot({ skuId, productName, onDecisionUpdated }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [responseId, setResponseId] = useState(null);

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content: `Ask about ${productName || "this SKU"} and I will answer from the current pricing recommendation, margin, market, inventory, and simulation context.`,
      },
    ]);
    setQuestion("");
    setError("");
    setLoading(false);
    setResponseId(null);
  }, [skuId, productName]);

  async function sendQuestion(nextQuestion) {
    const trimmed = nextQuestion.trim();
    if (!trimmed || loading) {
      return;
    }

    setLoading(true);
    setError("");
    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setQuestion("");

    try {
      const response = await askSKUQuestion(skuId, trimmed, responseId);
      setResponseId(response.response_id ?? null);
      setMessages((current) => [...current, { role: "assistant", content: response.answer }]);
      if (response.decision_update) {
        onDecisionUpdated?.(response.decision_update);
      }
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendQuestion(question);
  }

  return (
    <section className="glass-panel rounded-[1.5rem] p-5">
      <div>
        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">SKU Q&A</p>
        <h3 className="mt-1 text-xl font-semibold text-slate-950">Ask about this SKU</h3>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Use the assistant for recommendation context, market comparison, and margin interpretation.
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <div className="grid w-full gap-2 md:grid-cols-2">
          {starterQuestions.map((starter) => (
            <button
              key={starter}
              type="button"
              onClick={() => sendQuestion(starter)}
              className="theme-card-neutral rounded-[1rem] border px-4 py-3 text-left text-sm text-slate-700 transition hover:bg-white"
            >
              {starter}
            </button>
          ))}
        </div>
      </div>

      <div className="subtle-grid mt-4 space-y-3 rounded-[1.25rem] border border-slate-200 bg-white/70 p-4">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`rounded-[1rem] px-4 py-3 text-sm leading-6 ${
              message.role === "user"
                ? "ml-auto max-w-[34rem] bg-[#16324f] text-white"
                : "max-w-[46rem] border border-slate-200 bg-white text-slate-700"
            }`}
          >
            {message.content}
          </div>
        ))}

        {loading && (
          <div className="max-w-[46rem] rounded-[1rem] border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-500">
            Thinking through this SKU...
          </div>
        )}
      </div>

      {error && <p className="mt-4 text-sm text-rose-700">{error}</p>}

      <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={3}
          placeholder="Ask a question about this SKU..."
          className="w-full rounded-[1rem] border border-slate-300 bg-white/85 px-4 py-3 text-sm outline-none transition focus:border-[#3fa9f5] focus:ring-4 focus:ring-[#3fa9f5]/15"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="theme-button-primary rounded-full px-5 py-2.5 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-400 disabled:shadow-none"
        >
          {loading ? "Answering..." : "Ask chatbot"}
        </button>
      </form>
    </section>
  );
}
