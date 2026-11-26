import AIContentStudio from "./AIContentStudio";
import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { API_BASE, getErrorMessage } from "./config";

const initialTrends = [
  {
    id: 1,
    name: "Portable Blender",
    category: "Kitchen",
    searchInterest: 82,
    engagement: 76,
    competitorActivity: 61,
    signal: "Rising",
    explanation:
      "Search interest and engagement are relatively strong in this sample. Review supplier quality and pricing before shortlisting.",
  },
  {
    id: 2,
    name: "LED Desk Lamp",
    category: "Home & Office",
    searchInterest: 58,
    engagement: 52,
    competitorActivity: 72,
    signal: "Watch",
    explanation:
      "Competitor activity is comparatively high. Check how your product and offer would differ from existing listings.",
  },
  {
    id: 3,
    name: "Travel Organizer",
    category: "Travel",
    searchInterest: 69,
    engagement: 64,
    competitorActivity: 48,
    signal: "Steady",
    explanation:
      "The sample indicators are moderately consistent. Check customer reviews, demand, and supplier reliability.",
  },
  {
    id: 4,
    name: "Mini Bluetooth Speaker",
    category: "Electronics",
    searchInterest: 45,
    engagement: 39,
    competitorActivity: 55,
    signal: "Watch",
    explanation:
      "The sample indicators are lower than those of some other products. Gather more evidence before making a decision.",
  },
];

const navigation = [
  { name: "Dashboard", icon: "▦" },
  { name: "Products", icon: "□" },
  { name: "Trend Insights", icon: "↗" },
  { name: "AI Content", icon: "✦" },
  { name: "Review Queue", icon: "✓" },
];

function formatCurrency(value) {
  return `₹${Number(value).toLocaleString("en-IN")}`;
}

function getMargin(cost, price) {
  if (!price || price <= 0) return 0;
  return ((price - cost) / price) * 100;
}

function StatCard({ label, value, note, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <span>{label}</span>
        <span className="stat-icon">{icon}</span>
      </div>
      <h2>{value}</h2>
      <p>{note}</p>
    </div>
  );
}

function StatusBadge({ status }) {
  const className = status.toLowerCase().replace(/\s+/g, "-");

  return <span className={`status-badge ${className}`}>{status}</span>;
}

function Dashboard({ products, setPage, pendingReviewCount }) {
  const shortlisted = products.filter(
    (product) => product.status === "Shortlisted"
  ).length;

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">OVERVIEW</p>
          <h1>Dashboard</h1>
          <p className="page-description">
            Monitor product discovery, trend signals, and content activity.
          </p>
        </div>
        <button className="primary-button" onClick={() => setPage("Products")}>
          + Manage Products
        </button>
      </div>

      <div className="demo-notice">
        <strong>Demo mode:</strong> The dashboard currently uses sample data.
        Values are illustrative and are not live supplier or social-media data.
      </div>

      <div className="stats-grid">
        <StatCard
          label="Products Discovered"
          value="128"
          note="Illustrative sample metric"
          icon="□"
        />
        <StatCard
          label="Shortlisted Products"
          value={shortlisted + 29}
          note="Illustrative sample metric"
          icon="✓"
        />
        <StatCard
          label="Content Generated"
          value="18"
          note="Illustrative sample metric"
          icon="✦"
        />
        <StatCard
          label="Pending Reviews"
          value={pendingReviewCount}
          note="Drafts awaiting review"
          icon="◷"
        />
      </div>

      <div className="content-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Recent Products</h2>
              <p>Products currently in your workspace.</p>
            </div>
            <button className="text-button" onClick={() => setPage("Products")}>
              View all →
            </button>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Selling Price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {products.slice(0, 4).map((product) => (
                  <tr key={product.id}>
                    <td>{product.name}</td>
                    <td>{product.category}</td>
                    <td>{formatCurrency(product.price)}</td>
                    <td>
                      <StatusBadge status={product.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel workflow-panel">
          <div className="panel-heading">
            <div>
              <h2>Project Workflow</h2>
              <p>ShopMate.ai development pipeline.</p>
            </div>
          </div>

          <div className="workflow-list">
            <div className="workflow-item">
              <span className="workflow-number">1</span>
              <div>
                <h3>Product Sourcing</h3>
                <p>Collect and filter product information.</p>
              </div>
            </div>

            <div className="workflow-item">
              <span className="workflow-number">2</span>
              <div>
                <h3>Trend Insights</h3>
                <p>Review signals and compare products.</p>
              </div>
            </div>

            <div className="workflow-item">
              <span className="workflow-number">3</span>
              <div>
                <h3>AI Content</h3>
                <p>Prepare product marketing content.</p>
              </div>
            </div>

            <div className="workflow-item">
              <span className="workflow-number">4</span>
              <div>
                <h3>Human Review</h3>
                <p>Check content before any publishing.</p>
              </div>
            </div>
          </div>

          <button
            className="secondary-button full-width"
            onClick={() => setPage("Trend Insights")}
          >
            Explore Trend Insights
          </button>
        </section>
      </div>
    </>
  );
}

function ProductsPage({ products, setProducts }) {
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    category: "",
    cost: "",
    price: "",
    rating: "",
    status: "Pending",
  });
  const [error, setError] = useState("");

  const categories = [
    "All",
    ...new Set(products.map((product) => product.category)),
  ];

  const filteredProducts = products.filter((product) => {
    const matchesSearch = product.name
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesCategory =
      categoryFilter === "All" || product.category === categoryFilter;

    const matchesStatus =
      statusFilter === "All" || product.status === statusFilter;

    return matchesSearch && matchesCategory && matchesStatus;
  });

  function updateForm(event) {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  function addProduct(event) {
    event.preventDefault();
    setError("");

    const cost = Number(form.cost);
    const price = Number(form.price);
    const rating = Number(form.rating);

    if (!form.name.trim() || !form.category.trim()) {
      setError("Please enter a product name and category.");
      return;
    }

    if (
      form.cost === "" ||
      form.price === "" ||
      !Number.isFinite(cost) ||
      !Number.isFinite(price) ||
      cost < 0 ||
      price <= 0
    ) {
      setError("Enter a valid cost and selling price.");
      return;
    }

    if (
      form.rating !== "" &&
      (!Number.isFinite(rating) || rating < 0 || rating > 5)
    ) {
      setError("Rating must be between 0 and 5.");
      return;
    }

    const newProduct = {
      id: Date.now(),
      name: form.name.trim(),
      category: form.category.trim(),
      cost,
      price,
      rating: form.rating === "" ? 0 : rating,
      status: form.status,
    };

    setProducts((previous) => [newProduct, ...previous]);

    setForm({
      name: "",
      category: "",
      cost: "",
      price: "",
      rating: "",
      status: "Pending",
    });

    setShowForm(false);
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">PRODUCT DISCOVERY</p>
          <h1>Products</h1>
          <p className="page-description">
            Add, search, and review products in your workspace.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => setShowForm((previous) => !previous)}
        >
          {showForm ? "Close Form" : "+ Add Product"}
        </button>
      </div>

      <div className="demo-notice">
        <strong>Demo mode:</strong> Products added here are stored in React
        state. They will reset when the page is refreshed.
      </div>

      {showForm && (
        <section className="panel form-panel">
          <div className="panel-heading">
            <div>
              <h2>Add a Product</h2>
              <p>Enter product details below.</p>
            </div>
          </div>

          <form onSubmit={addProduct}>
            <div className="form-grid">
              <label>
                Product Name *
                <input
                  name="name"
                  value={form.name}
                  onChange={updateForm}
                  placeholder="e.g. Wireless Headphones"
                />
              </label>

              <label>
                Category *
                <input
                  name="category"
                  value={form.category}
                  onChange={updateForm}
                  placeholder="e.g. Electronics"
                />
              </label>

              <label>
                Supplier Cost (₹) *
                <input
                  name="cost"
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.cost}
                  onChange={updateForm}
                  placeholder="e.g. 1200"
                />
              </label>

              <label>
                Selling Price (₹) *
                <input
                  name="price"
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={form.price}
                  onChange={updateForm}
                  placeholder="e.g. 1999"
                />
              </label>

              <label>
                Rating (0–5)
                <input
                  name="rating"
                  type="number"
                  min="0"
                  max="5"
                  step="0.1"
                  value={form.rating}
                  onChange={updateForm}
                  placeholder="e.g. 4.5"
                />
              </label>

              <label>
                Status
                <select
                  name="status"
                  value={form.status}
                  onChange={updateForm}
                >
                  <option>Pending</option>
                  <option>Under Review</option>
                  <option>Shortlisted</option>
                </select>
              </label>
            </div>

            {error && <p className="form-error">{error}</p>}

            <div className="form-actions">
              <button type="submit" className="primary-button">
                Save Product
              </button>

              <button
                type="button"
                className="secondary-button"
                onClick={() => {
                  setShowForm(false);
                  setError("");
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Product List</h2>
            <p>
              Showing {filteredProducts.length} of {products.length} products.
            </p>
          </div>
        </div>

        <div className="filter-row">
          <input
            className="search-input"
            type="search"
            placeholder="Search products..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select
            value={categoryFilter}
            onChange={(event) => setCategoryFilter(event.target.value)}
            aria-label="Filter by category"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category === "All" ? "All Categories" : category}
              </option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            aria-label="Filter by status"
          >
            <option value="All">All Statuses</option>
            <option value="Pending">Pending</option>
            <option value="Under Review">Under Review</option>
            <option value="Shortlisted">Shortlisted</option>
          </select>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Cost</th>
                <th>Selling Price</th>
                <th>Margin</th>
                <th>Rating</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {filteredProducts.map((product) => (
                <tr key={product.id}>
                  <td>{product.name}</td>
                  <td>{product.category}</td>
                  <td>{formatCurrency(product.cost)}</td>
                  <td>{formatCurrency(product.price)}</td>
                  <td>
                    {getMargin(product.cost, product.price).toFixed(1)}%
                  </td>
                  <td>{Number(product.rating || 0).toFixed(1)} / 5</td>
                  <td>
                    <StatusBadge status={product.status} />
                  </td>
                </tr>
              ))}

              {filteredProducts.length === 0 && (
                <tr>
                  <td colSpan="7" className="empty-state">
                    No products match your search or filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function SignalScore({ label, score }) {
  return (
    <div className="signal-score">
      <div className="signal-score-track">
        <div
          className="signal-score-fill"
          style={{ width: `${Math.max(0, Math.min(100, score))}%` }}
        />
      </div>

      <span>
        {label}: <strong>{score}/100</strong>
      </span>
    </div>
  );
}

function TrendInsightsPage() {
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [signalFilter, setSignalFilter] = useState("All");

  const categories = [
    "All",
    ...new Set(initialTrends.map((item) => item.category)),
  ];

  const filteredTrends = useMemo(() => {
    return initialTrends.filter((item) => {
      const matchesSearch = item.name
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchesCategory =
        categoryFilter === "All" || item.category === categoryFilter;

      const matchesSignal =
        signalFilter === "All" || item.signal === signalFilter;

      return matchesSearch && matchesCategory && matchesSignal;
    });
  }, [search, categoryFilter, signalFilter]);

  const risingCount = initialTrends.filter(
    (item) => item.signal === "Rising"
  ).length;

  const steadyCount = initialTrends.filter(
    (item) => item.signal === "Steady"
  ).length;

  const watchCount = initialTrends.filter(
    (item) => item.signal === "Watch"
  ).length;

  function clearFilters() {
    setSearch("");
    setCategoryFilter("All");
    setSignalFilter("All");
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <p className="eyebrow">PRODUCT ANALYSIS</p>
          <h1>Trend Insights</h1>
          <p className="page-description">
            Compare illustrative indicators to help review products.
          </p>
        </div>
      </div>

      <div className="demo-notice trend-demo-notice">
        <strong>Sample data only:</strong> These scores are illustrative values
        for the project interface. They are not live search, engagement, or
        competitor measurements, and they do not predict virality.
      </div>

      <div className="stats-grid trend-overview-grid">
        <StatCard
          label="Products Analyzed"
          value={initialTrends.length}
          note="Sample product records"
          icon="▦"
        />

        <StatCard
          label="Rising Signals"
          value={risingCount}
          note="Sample classification"
          icon="↗"
        />

        <StatCard
          label="Steady Signals"
          value={steadyCount}
          note="Sample classification"
          icon="→"
        />

        <StatCard
          label="Needs Monitoring"
          value={watchCount}
          note="Sample classification"
          icon="◷"
        />
      </div>

      <section className="panel trend-panel">
        <div className="panel-heading">
          <div>
            <h2>Product Trend Signals</h2>
            <p>Search and filter the sample product indicators.</p>
          </div>
        </div>

        <div className="filter-row trend-filters">
          <input
            className="search-input"
            type="search"
            placeholder="Search products..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select
            value={categoryFilter}
            onChange={(event) => setCategoryFilter(event.target.value)}
            aria-label="Filter trends by category"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category === "All" ? "All Categories" : category}
              </option>
            ))}
          </select>

          <select
            value={signalFilter}
            onChange={(event) => setSignalFilter(event.target.value)}
            aria-label="Filter trends by signal"
          >
            <option value="All">All Signals</option>
            <option value="Rising">Rising</option>
            <option value="Steady">Steady</option>
            <option value="Watch">Watch</option>
          </select>

          <button className="secondary-button" onClick={clearFilters}>
            Clear Filters
          </button>
        </div>

        <p className="results-count">
          Showing {filteredTrends.length} of {initialTrends.length} products.
        </p>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Category</th>
                <th>Search Interest</th>
                <th>Engagement</th>
                <th>Competitor Activity</th>
                <th>Signal</th>
              </tr>
            </thead>

            <tbody>
              {filteredTrends.map((item) => (
                <tr key={item.id}>
                  <td>{item.name}</td>
                  <td>{item.category}</td>

                  <td>
                    <SignalScore
                      label="Search"
                      score={item.searchInterest}
                    />
                  </td>

                  <td>
                    <SignalScore
                      label="Engagement"
                      score={item.engagement}
                    />
                  </td>

                  <td>
                    <SignalScore
                      label="Competitors"
                      score={item.competitorActivity}
                    />
                  </td>

                  <td>
                    <StatusBadge status={item.signal} />
                  </td>
                </tr>
              ))}

              {filteredTrends.length === 0 && (
                <tr>
                  <td colSpan="6" className="empty-state">
                    No trend records match your search or filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel trend-explanation-panel">
        <div className="panel-heading">
          <div>
            <h2>Signal Explanations</h2>
            <p>Review the sample reasoning for each product.</p>
          </div>
        </div>

        <div className="trend-explanation-grid">
          {filteredTrends.map((item) => (
            <article className="trend-explanation-card" key={item.id}>
              <div className="trend-explanation-top">
                <h3>{item.name}</h3>
                <StatusBadge status={item.signal} />
              </div>

              <p>{item.explanation}</p>
            </article>
          ))}

          {filteredTrends.length === 0 && (
            <p className="empty-state">
              No explanations to show for the current filters.
            </p>
          )}
        </div>

        <div className="demo-notice trend-method-note">
          <strong>How to read the scores:</strong> Each indicator is shown on a
          0–100 scale for demonstration. In a connected version, these values
          would need to come from verified data sources and a documented
          scoring method. A high score alone does not establish that a product
          will sell well.
        </div>
      </section>
    </>
  );
}

/* Review Queue page */

function ReviewQueuePage({
  reviewItems,
  onUpdateStatus,
  busyId,
  products = [],
}) {
  const pendingItems = reviewItems.filter(
    (item) => item.status === "Pending"
  );

  const [workflow, setWorkflow] = useState({});
  const [publishMode, setPublishMode] = useState("checking");
  const [actionId, setActionId] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadMode() {
      try {
        const response = await fetch(`${API_BASE}/api/posts/mode`);
        if (!response.ok) throw new Error("Could not load publishing mode.");
        const data = await response.json();
        if (!cancelled) setPublishMode(data.mode || "unknown");
      } catch {
        if (!cancelled) setPublishMode("unknown");
      }
    }

    loadMode();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadExistingWorkflow() {
      const approvedReels = reviewItems.filter(
        (item) =>
          item.status === "Approved" &&
          item.contentType === "Reel Script"
      );

      for (const item of approvedReels) {
        if (cancelled) return;

        try {
          const [videoResponse, postsResponse] = await Promise.all([
            fetch(`${API_BASE}/api/videos/${item.id}`),
            fetch(`${API_BASE}/api/posts?review_id=${item.id}`),
          ]);

          let videoPath = null;
          let posts = [];

          if (videoResponse.ok) {
            const videoData = await videoResponse.json();
            videoPath = videoData.video_path || null;
          }

          if (postsResponse.ok) {
            const postsData = await postsResponse.json();
            posts = Array.isArray(postsData)
              ? postsData
              : postsData.posts || [];
          }

          if (!cancelled) {
            setWorkflow((current) => ({
              ...current,
              [item.id]: {
                ...current[item.id],
                checked: true,
                videoPath: current[item.id]?.videoPath || videoPath,
                post:
                  posts.find((post) =>
                    ["Queued", "Publishing", "Posted"].includes(post.status)
                  ) || current[item.id]?.post || null,
              },
            }));
          }
        } catch {
          // The workflow buttons will report a useful error if an API call fails.
        }
      }
    }

    if (reviewItems.length > 0) loadExistingWorkflow();

    return () => {
      cancelled = true;
    };
  }, [reviewItems]);

  function updateWorkflow(id, changes) {
    setWorkflow((current) => ({
      ...current,
      [id]: {
        ...current[id],
        ...changes,
      },
    }));
  }

  async function createReel(item, product) {
    if (!product?.image_path) {
      updateWorkflow(item.id, {
        error: "This product does not have an uploaded image.",
      });
      return;
    }

    try {
      setActionId(item.id);
      updateWorkflow(item.id, {
        error: "",
        message: "Rendering final Reel video...",
      });

      const existingResponse = await fetch(
        `${API_BASE}/api/posts?review_id=${item.id}`
      );

      if (existingResponse.ok) {
        const existingData = await existingResponse.json();
        const existingPosts = Array.isArray(existingData)
          ? existingData
          : existingData.posts || [];
        const activePost = existingPosts.find((post) =>
          ["Queued", "Publishing", "Posted"].includes(post.status)
        );

        if (activePost) {
          updateWorkflow(item.id, {
            post: activePost,
            message: "A post already exists for this review. Duplicate publishing is blocked.",
            error: "",
          });
          return;
        }
      }

      const response = await fetch(`${API_BASE}/api/videos/render`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          review_id: item.id,
          product_image_path: product.image_path,
          quality: "final",
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(
          getErrorMessage(data, "Could not render the Reel video.")
        );
      }

      updateWorkflow(item.id, {
        videoPath: data.video_path,
        message: `Final video created successfully (${data.duration_seconds}s).`,
        error: "",
        post: null,
      });
    } catch (error) {
      updateWorkflow(item.id, {
        error: error.message || "Video rendering failed.",
        message: "",
      });
    } finally {
      setActionId(null);
    }
  }

  async function publishReel(item) {
    const current = workflow[item.id];

    if (!current?.videoPath) {
      updateWorkflow(item.id, {
        error: "Create the final Reel video before continuing.",
      });
      return;
    }

    if (
      current.post &&
      ["Queued", "Publishing", "Posted"].includes(current.post.status)
    ) {
      updateWorkflow(item.id, {
        error: "A post already exists. Duplicate publishing is blocked.",
      });
      return;
    }

    const isLive = publishMode === "live";
    const confirmed = window.confirm(
      isLive
        ? "This will publish the Reel publicly to Instagram. Continue?"
        : "This is DRY-RUN mode. The workflow will be tested, but nothing will be posted publicly. Continue?"
    );

    if (!confirmed) return;

    try {
      setActionId(item.id);
      updateWorkflow(item.id, {
        error: "",
        message: "Adding Reel to publishing queue...",
      });

      const queueResponse = await fetch(`${API_BASE}/api/posts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          review_id: item.id,
          platforms: ["instagram"],
        }),
      });

      const queueData = await queueResponse.json();
      if (!queueResponse.ok) {
        throw new Error(
          getErrorMessage(queueData, "Could not queue the Reel.")
        );
      }

      const queuedPost = Array.isArray(queueData.posts)
        ? queueData.posts[0]
        : queueData.post || queueData;

      if (!queuedPost?.id) {
        throw new Error("The queue response did not contain a post ID.");
      }

      updateWorkflow(item.id, {
        post: queuedPost,
        message: "Reel queued. Running publishing step...",
      });

      const publishResponse = await fetch(
        `${API_BASE}/api/posts/${queuedPost.id}/publish`,
        { method: "POST" }
      );

      const publishData = await publishResponse.json();
      if (!publishResponse.ok) {
        throw new Error(
          getErrorMessage(publishData, "Publishing action failed.")
        );
      }

      updateWorkflow(item.id, {
        post: publishData,
        message:
          publishData.mode === "dry-run"
            ? "Dry-run completed. Nothing was posted publicly."
            : "Instagram publishing completed.",
        error: "",
      });
    } catch (error) {
      updateWorkflow(item.id, {
        error: error.message || "Publishing workflow failed.",
        message: "",
      });
    } finally {
      setActionId(null);
    }
  }

  function getCaption(item) {
    let payload = item.payload || {};

    if (typeof payload === "string") {
      try {
        payload = JSON.parse(payload);
      } catch {
        payload = {};
      }
    }

    const caption = payload.caption || "";
    const hashtags = Array.isArray(payload.hashtags)
      ? payload.hashtags.join(" ")
      : "";

    return [caption, hashtags].filter(Boolean).join("\n\n");
  }

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">CONTENT WORKSPACE</p>
          <h1>Review Queue</h1>
          <p className="page-description">
            Check generated drafts and approve or reject them before use.
          </p>
        </div>
      </div>

      <div className="demo-notice">
        <strong>Instagram publishing mode:</strong>{" "}
        {publishMode === "dry-run"
          ? "Dry-run — no public posts will be created."
          : publishMode === "live"
          ? "Live — publishing can create public Instagram posts."
          : "Checking publishing mode..."}
      </div>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Pending Reviews ({pendingItems.length})</h2>
            <p>Review each draft before deciding whether to approve it.</p>
          </div>
        </div>

        {reviewItems.length === 0 ? (
          <p>
            No drafts to review yet. Generate content in AI Content Studio and
            select “Send to Review”.
          </p>
        ) : (
          <div className="review-list">
            {reviewItems.map((item) => {
              const product = products.find(
                (p) =>
                  p.name?.trim().toLowerCase() ===
                  item.productName?.trim().toLowerCase()
              );
              const current = workflow[item.id] || {};
              const isReel =
                item.contentType === "Reel Script" &&
                item.status === "Approved";
              const alreadyPosted = ["Queued", "Publishing", "Posted"].includes(
                current.post?.status
              );

              return (
                <article className="review-card" key={item.id}>
                  <div className="review-card-heading">
                    <div>
                      <h3>{item.productName}</h3>
                      <p>
                        {item.contentType} · {item.tone} tone
                      </p>
                    </div>

                    <span
                      className={`review-status ${item.status.toLowerCase()}`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <p className="review-content">{item.content}</p>

                  {item.status === "Pending" && (
                    <div className="review-actions">
                      <button
                        className="primary-button"
                        disabled={busyId === item.id}
                        onClick={() => onUpdateStatus(item.id, "Approved")}
                      >
                        {busyId === item.id ? "Saving..." : "Approve"}
                      </button>

                      <button
                        className="secondary-button"
                        disabled={busyId === item.id}
                        onClick={() => onUpdateStatus(item.id, "Rejected")}
                      >
                        {busyId === item.id ? "Saving..." : "Reject"}
                      </button>
                    </div>
                  )}

                  {isReel && (
                    <div className="publish-workflow">
                      <h4>Instagram Reel Workflow</h4>
                      <p className="workflow-product">
                        Product image: {product?.image_path ? "Available" : "Not uploaded — add a product image first."}
                      </p>

                      {!current.videoPath && (
                        <button
                          className="primary-button"
                          disabled={
                            actionId === item.id ||
                            !product?.image_path ||
                            alreadyPosted
                          }
                          onClick={() => createReel(item, product)}
                        >
                          {actionId === item.id ? "Please wait..." : "Create Reel Video"}
                        </button>
                      )}

                      {current.videoPath && (
                        <div className="reel-video-preview">
                          <h4>Final Reel Preview</h4>
                          <video
                            controls
                            preload="metadata"
                            src={`${API_BASE}/api/videos/${item.id}/file`}
                          >
                            Your browser does not support video playback.
                          </video>

                          <h4>Instagram Caption</h4>
                          <p className="reel-caption">
                            {getCaption(item) || "No caption available."}
                          </p>

                          {current.post ? (
                            <div className="publish-result">
                              <strong>Post status: {current.post.status}</strong>
                              {current.post.mode === "dry-run" && (
                                <p>Dry-run completed. Nothing was posted publicly.</p>
                              )}
                              {current.post.external_url && (
                                <p>
                                  <a
                                    href={current.post.external_url}
                                    target="_blank"
                                    rel="noreferrer"
                                  >
                                    View Instagram Reel
                                  </a>
                                </p>
                              )}
                            </div>
                          ) : (
                            <button
                              className="primary-button"
                              disabled={
                                actionId === item.id ||
                                publishMode === "checking" ||
                                publishMode === "unknown"
                              }
                              onClick={() => publishReel(item)}
                            >
                              {actionId === item.id
                                ? "Processing..."
                                : publishMode === "dry-run"
                                ? "Confirm Dry-run Test"
                                : "Confirm & Publish to Instagram"}
                            </button>
                          )}
                        </div>
                      )}

                      {current.message && (
                        <p className="workflow-message">{current.message}</p>
                      )}
                      {current.error && (
                        <p className="workflow-error">{current.error}</p>
                      )}
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}
      </section>
    </section>
  );
}

function PlaceholderPage({ page }) {
  const details = {
    "AI Content": {
      heading: "AI Content Studio",
      description:
        "Create and manage product descriptions, captions, and marketing ideas.",
      message:
        "The content-generation form will be added in the next development step.",
    },

    "Review Queue": {
      heading: "Review Queue",
      description:
        "Review generated content before it can be approved for publishing.",
      message:
        "The review and approval workflow will be added in a later step.",
    },
  };

  const current = details[page] || {
    heading: page,
    description: "This section is part of the ShopMate.ai workspace.",
    message: "This page is not implemented yet.",
  };

  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">SHOPMATE.AI WORKSPACE</p>
        <h1>{current.heading}</h1>
        <p className="page-description">{current.description}</p>
      </div>

      <section className="panel placeholder-panel">
        <div className="placeholder-icon">✦</div>
        <h2>Coming in the next step</h2>
        <p>{current.message}</p>
      </section>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("Dashboard");

  // Products are now loaded from the FastAPI backend.
  const [products, setProducts] = useState([]);

  const [reviewItems, setReviewItems] = useState([]);
  const [apiError, setApiError] = useState("");
  const [busyId, setBusyId] = useState(null);

  useEffect(() => {
    async function loadProducts() {
      try {
        const response = await fetch(`${API_BASE}/api/products`);

        if (!response.ok) {
          throw new Error("Could not load products.");
        }

        const data = await response.json();

        // Add frontend-only fields that the current Products page expects.
        const formattedProducts = data.map((product) => ({
          ...product,
          cost:
            product.cost !== undefined
              ? Number(product.cost)
              : Number(product.price || 0),
          price: Number(product.price || 0),
          rating:
            product.rating !== undefined ? Number(product.rating) : 0,
          status: product.status || "Pending",
        }));

        setProducts(formattedProducts);
        setApiError("");
      } catch {
        setApiError(
          `Cannot connect to the backend. Make sure it is running at ${API_BASE}.`
        );
      }
    }

    loadProducts();
  }, []);

  useEffect(() => {
    async function loadReviews() {
      try {
        const response = await fetch(`${API_BASE}/api/reviews`);

        if (!response.ok) {
          throw new Error("Could not load saved drafts.");
        }

        const data = await response.json();
        setReviewItems(data);
        setApiError("");
      } catch {
        setApiError(
          `Cannot connect to the backend. Make sure it is running at ${API_BASE}.`
        );
      }
    }

    loadReviews();
  }, []);

  const pendingReviewCount = reviewItems.filter(
    (item) => item.status === "Pending"
  ).length;

  async function sendDraftToReview(draft) {
    try {
      setApiError("");

      const response = await fetch(`${API_BASE}/api/reviews`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(draft),
      });

      const savedDraft = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(savedDraft, "Could not save draft.")
        );
      }

      setReviewItems((items) => [savedDraft, ...items]);
      setPage("Review Queue");
    } catch (error) {
      setApiError(error.message || "Could not save the draft.");
    }
  }

  async function updateReviewStatus(id, status) {
    try {
      setBusyId(id);
      setApiError("");

      const response = await fetch(
        `${API_BASE}/api/reviews/${id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status }),
        }
      );

      const updatedDraft = await response.json();

      if (!response.ok) {
        throw new Error(
          getErrorMessage(updatedDraft, "Could not update draft.")
        );
      }

      setReviewItems((items) =>
        items.map((item) =>
          item.id === updatedDraft.id ? updatedDraft : item
        )
      );
    } catch (error) {
      setApiError(
        error.message || "Could not update the draft status."
      );
    } finally {
      setBusyId(null);
    }
  }

  function renderPage() {
    if (page === "Dashboard") {
      return (
        <Dashboard
          products={products}
          setPage={setPage}
          pendingReviewCount={pendingReviewCount}
        />
      );
    }

    if (page === "Products") {
      return (
        <ProductsPage
          products={products}
          setProducts={setProducts}
        />
      );
    }

    if (page === "Trend Insights") {
      return <TrendInsightsPage />;
    }

    if (page === "AI Content") {
      return (
        <AIContentStudio
          products={products}
          onSendToReview={sendDraftToReview}
        />
      );
    }

    if (page === "Review Queue") {
      return (
        <ReviewQueuePage
          reviewItems={reviewItems}
          onUpdateStatus={updateReviewStatus}
          busyId={busyId}
          products={products}
        />
      );
    }

    return <PlaceholderPage page={page} />;
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>

          <div>
            <h2>ShopMate.ai</h2>
            <p>Smart product workspace</p>
          </div>
        </div>

        <p className="sidebar-label">WORKSPACE</p>

        <nav className="sidebar-nav">
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-link ${
                page === item.name ? "active" : ""
              }`}
              onClick={() => setPage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.name}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-avatar">M</div>

          <div>
            <strong>Project Workspace</strong>
            <p>Semester 5 · AIOT</p>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{page}</strong>
          </div>

          <div className="demo-label">
            <span className="demo-dot" />
            Workspace
          </div>
        </header>

        <div className="page-content">
          {apiError && (
            <div className="demo-notice">
              <strong>Backend:</strong> {apiError}
            </div>
          )}

          {renderPage()}
        </div>
      </main>
    </div>
  );
}