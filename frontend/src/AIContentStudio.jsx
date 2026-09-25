import { useEffect, useState } from "react";

const sampleProducts = [
  { id: 1, name: "Portable Blender", category: "Kitchen", price: 1299 },
  { id: 2, name: "LED Desk Lamp", category: "Home & Office", price: 899 },
  { id: 3, name: "Travel Organizer", category: "Travel", price: 599 },
  {
    id: 4,
    name: "Mini Bluetooth Speaker",
    category: "Electronics",
    price: 1499,
  },
];

export default function AIContentStudio({
  products = sampleProducts,
  onSendToReview,
}) {
  const availableProducts =
    Array.isArray(products) && products.length > 0 ? products : sampleProducts;

  const [selectedProductId, setSelectedProductId] = useState(
    String(availableProducts[0]?.id ?? availableProducts[0]?.name ?? "")
  );

  const [contentType, setContentType] = useState("Product Caption");
  const [tone, setTone] = useState("Friendly");
  const [generatedContent, setGeneratedContent] = useState("");
  const [message, setMessage] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (availableProducts.length === 0) {
      setSelectedProductId("");
      return;
    }

    const selectedStillExists = availableProducts.some(
      (product) =>
        String(product.id ?? product.name) === selectedProductId
    );

    if (!selectedStillExists) {
      setSelectedProductId(
        String(availableProducts[0]?.id ?? availableProducts[0]?.name ?? "")
      );
    }
  }, [availableProducts, selectedProductId]);

  const selectedProduct =
    availableProducts.find(
      (product) => String(product.id ?? product.name) === selectedProductId
    ) ?? availableProducts[0];

  async function handleGenerate() {
    if (!selectedProduct) {
      setMessage("Please add a product before generating content.");
      return;
    }

    setIsGenerating(true);
    setMessage("");
    setGeneratedContent("");

    try {
      const response = await fetch("http://localhost:5000/api/ai/generate", {
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

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `AI request failed (${response.status}): ${errorText}`
        );
      }

      const data = await response.json();

      setGeneratedContent(data.response ?? "");
      setMessage("AI content generated successfully. Review and edit it before use.");
    } catch (error) {
      console.error("AI generation error:", error);
      setMessage(
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

    onSendToReview({
      productName: selectedProduct?.name ?? "Unknown product",
      contentType,
      tone,
      content: generatedContent,
    });

    setMessage("Draft sent to Review Queue.");
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
        <strong>AI-assisted mode:</strong> Content is generated using the local
        Qwen3 model through the ShopMate.ai backend. Review and edit all content
        before publishing.
      </div>

      <div className="content-studio-grid">
        <div className="studio-panel">
          <h2>Create Content</h2>
          <p className="panel-description">
            Choose a product and customize the content settings.
          </p>

          <label htmlFor="content-product">Select Product</label>
          <select
            id="content-product"
            value={selectedProductId}
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
            {isGenerating ? "Generating..." : "Generate Content"}
          </button>
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
                ? "Generating AI content..."
                : "Your AI-generated content will appear here..."
            }
            value={generatedContent}
            onChange={(event) => setGeneratedContent(event.target.value)}
          />

          <button
            className="primary-button"
            onClick={handleSendToReview}
            disabled={!generatedContent.trim()}
          >
            Send to Review
          </button>

          {message && <p className="studio-message">{message}</p>}

          <p className="output-note">
            AI-generated content may contain errors. Check product details and
            claims before using it in a real promotion.
          </p>
        </div>
      </div>
    </section>
  );
}