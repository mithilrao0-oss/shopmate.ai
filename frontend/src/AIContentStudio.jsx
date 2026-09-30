import { useEffect, useState } from "react";
import { API_BASE, getErrorMessage } from "./config";

export default function AIContentStudio({ products = [], onSendToReview }) {
  const availableProducts = Array.isArray(products) ? products : [];

  const [selectedProductId, setSelectedProductId] = useState("");

  const [contentType, setContentType] = useState("Product Caption");
  const [tone, setTone] = useState("Friendly");
  const [generatedContent, setGeneratedContent] = useState("");
  const [message, setMessage] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  // Agent information returned by FastAPI.
  const [agentInfo, setAgentInfo] = useState(null);

  // Falls back to the first product when nothing valid is selected, so no
  // effect is needed to keep the selection in sync with the loaded products.
  const selectedProduct =
    availableProducts.find(
      (product) => String(product.id ?? product.name) === selectedProductId
    ) ?? availableProducts[0];

  const effectiveProductId = String(
    selectedProduct?.id ?? selectedProduct?.name ?? ""
  );

  // Responsible AI result from the backend (single source of truth).
  // It re-runs whenever the text changes, so edits are checked too.
  const [responsibleAIResult, setResponsibleAIResult] = useState(null);

  useEffect(() => {
    if (!generatedContent.trim()) {
      return undefined;
    }

    const controller = new AbortController();

    const timer = setTimeout(async () => {
      try {
        const response = await fetch(`${API_BASE}/api/ai/check`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: generatedContent }),
          signal: controller.signal,
        });

        if (response.ok) {
          setResponsibleAIResult({
            text: generatedContent,
            ...(await response.json()),
          });
        }
      } catch {
        // Ignore aborted or failed checks; the server re-checks on save.
      }
    }, 500);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [generatedContent]);

  // Only trust a result that belongs to the text currently in the box.
  const activeResult =
    responsibleAIResult?.text === generatedContent ? responsibleAIResult : null;
  const contentFlagged = activeResult?.passed === false;
  const canSendToReview = activeResult?.passed === true;

  async function handleGenerate() {
    if (!selectedProduct) {
      setMessage("Please add a product before generating content.");
      return;
    }

    setIsGenerating(true);
    setMessage("");
    setGeneratedContent("");
    setAgentInfo(null);

    try {
      const response = await fetch(`${API_BASE}/api/ai/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product_name: selectedProduct.name,
          category: selectedProduct.category ?? null,
          price: selectedProduct.price ?? null,
          content_type: contentType,
          tone,
        }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, `AI request failed (${response.status}).`)
        );
      }

      setGeneratedContent(data.response ?? "");

      // Store the actual agent workflow returned by FastAPI.
      setAgentInfo({
        agent: data.agent ?? "ShopMate Content Agent",
        model: data.model ?? "Qwen3 1.7B",
        workflow: Array.isArray(data.workflow) ? data.workflow : [],
        attempts: data.attempts ?? 1,
        revisionPerformed: Boolean(data.revision_performed),
        responsibleAI: data.responsible_ai ?? null,
      });

      setMessage(
        "AI content generated successfully. Review and edit it before use."
      );
    } catch (error) {
      console.error("AI generation error:", error);

      setMessage(
        error.message ||
          "Could not generate content. Make sure the FastAPI backend and Ollama are running."
      );
    } finally {
      setIsGenerating(false);
    }
  }

  function handleSendToReview() {
    if (!generatedContent.trim()) {
      setMessage("Generate content before sending it for review.");
      return;
    }

    if (!onSendToReview) {
      setMessage("The review queue is not connected.");
      return;
    }

    if (!canSendToReview) {
      setMessage(
        contentFlagged
          ? "Responsible AI check found wording that needs human review. Please edit the content before sending it."
          : "The Responsible AI check has not finished yet. Please wait a moment."
      );
      return;
    }

    onSendToReview({
      productName: selectedProduct?.name ?? "Unknown product",
      contentType,
      tone,
      content: generatedContent,
    });

    setMessage("Draft passed the Responsible AI check and was sent to Review Queue.");
  }

  async function handleCopy() {
    if (!generatedContent) {
      setMessage("Generate some content before copying.");
      return;
    }

    try {
      await navigator.clipboard.writeText(generatedContent);
      setMessage("Content copied to clipboard.");
    } catch {
      setMessage("Copy was unavailable. Select the text and copy it manually.");
    }
  }

  return (
    <section className="content-studio">
      <div className="page-heading">
        <div>
          <p className="eyebrow">CONTENT WORKSPACE</p>

          <h1>AI Content Studio</h1>

          <p className="page-description">
            Generate product captions, reel scripts, and descriptions with AI.
          </p>
        </div>
      </div>

      <div className="demo-notice">
        <strong>AI-assisted mode:</strong> Content is generated by the
        ShopMate Content Agent using the local Qwen3 1.7B model through Ollama.
        Review and edit all content before publishing.
      </div>

      <div className="content-studio-grid">
        <div className="studio-panel">
          <h2>Create Content</h2>

          <p className="panel-description">
            Choose a product and customize the content settings.
          </p>

          {availableProducts.length === 0 && (
            <p className="studio-message">
              No products loaded yet. Start the backend so products can load.
            </p>
          )}

          <label htmlFor="content-product">Select Product</label>

          <select
            id="content-product"
            value={effectiveProductId}
            onChange={(event) => setSelectedProductId(event.target.value)}
          >
            {availableProducts.map((product, index) => {
              const value = String(product.id ?? product.name ?? index);

              return (
                <option key={value} value={value}>
                  {product.name}
                </option>
              );
            })}
          </select>

          <label htmlFor="content-type">Content Type</label>

          <select
            id="content-type"
            value={contentType}
            onChange={(event) => setContentType(event.target.value)}
          >
            <option>Product Caption</option>
            <option>Reel Script</option>
            <option>Product Description</option>
          </select>

          <label htmlFor="content-tone">Content Tone</label>

          <select
            id="content-tone"
            value={tone}
            onChange={(event) => setTone(event.target.value)}
          >
            <option>Friendly</option>
            <option>Professional</option>
            <option>Exciting</option>
          </select>

          <button
            className="primary-button"
            onClick={handleGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? "Agent Working..." : "Generate Content"}
          </button>

          <div className="responsible-ai-panel">
            <h3>Responsible AI</h3>

            <div className="responsible-ai-item">
              <strong>🔒 Privacy</strong>
              <span>
                AI generation uses the locally running Ollama/Qwen3 model.
              </span>
            </div>

            <div className="responsible-ai-item">
              <strong>👁 Transparency</strong>
              <span>
                The interface identifies the AI model and generation settings.
              </span>
            </div>

            <div className="responsible-ai-item">
              <strong>🛡 Safety</strong>
              <span>
                AI output remains editable and requires human review.
              </span>
            </div>

            <div className="responsible-ai-item">
              <strong>⚖ Fairness</strong>
              <span>
                Generated text is screened for potentially inappropriate or
                biased wording.
              </span>
            </div>
          </div>
        </div>

        <div className="studio-panel">
          <div className="output-heading">
            <div>
              <h2>Content Preview</h2>

              <p className="panel-description">
                Review and edit your AI-generated content below.
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={handleCopy}
              disabled={!generatedContent}
            >
              Copy
            </button>
          </div>

          <textarea
            className="content-output"
            aria-label="Generated content"
            placeholder={
              isGenerating
                ? "ShopMate Content Agent is working..."
                : "Your AI-generated content will appear here..."
            }
            value={generatedContent}
            onChange={(event) => setGeneratedContent(event.target.value)}
          />

          {agentInfo && (
            <div className="ai-transparency-card">
              <h3>🤖 ShopMate Content Agent</h3>

              <p>
                <strong>Model:</strong> {agentInfo.model}
              </p>

              <p>
                <strong>Agent:</strong> {agentInfo.agent}
              </p>

              <p>
                <strong>Attempts:</strong> {agentInfo.attempts}
              </p>

              <p>
                <strong>Revision performed:</strong>{" "}
                {agentInfo.revisionPerformed ? "Yes" : "No"}
              </p>

              <div>
                <strong>Agent Workflow:</strong>

                <ol>
                  {agentInfo.workflow.map((step, index) => (
                    <li key={`${step}-${index}`}>{step}</li>
                  ))}
                </ol>
              </div>
            </div>
          )}

          {generatedContent && activeResult && (
            <div
              className={`fairness-check ${
                contentFlagged ? "fairness-warning" : "fairness-safe"
              }`}
            >
              <strong>Responsible AI Check</strong>

              <p>
                {contentFlagged
                  ? "\u26a0\ufe0f Review required. The check flagged: " +
                    activeResult.issues.join(", ") +
                    "."
                  : "\u2713 No obvious issues detected. Human review is still required."}
              </p>

              {contentFlagged && (
                <p>
                  Flagged wording:{" "}
                  {Object.values(activeResult.matches ?? {})
                    .flat()
                    .join(", ")}
                </p>
              )}
            </div>
          )}

          <button
            className="primary-button"
            onClick={handleSendToReview}
            disabled={!canSendToReview}
          >
            Send to Review
          </button>

          {message && <p className="studio-message">{message}</p>}

          <p className="output-note">
            AI-generated content may contain errors or inappropriate wording.
            Check product details, claims, and language before using it in a
            real promotion.
          </p>
        </div>
      </div>
    </section>
  );
}