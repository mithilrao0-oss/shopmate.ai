import AIContentStudio from "./AIContentStudio";
import { useMemo, useState } from "react";
import "./App.css";

const initialProducts = [
  {
    id: 1,
    name: "Portable Blender",
    category: "Kitchen",
    cost: 650,
    price: 1299,
    rating: 4.5,
    status: "Shortlisted",
  },
  {
    id: 2,
    name: "LED Desk Lamp",
    category: "Home & Office",
    cost: 420,
    price: 899,
    rating: 4.3,
    status: "Under Review",
  },
  {
    id: 3,
    name: "Travel Organizer",
    category: "Travel",
    cost: 280,
    price: 599,
    rating: 4.6,
    status: "Shortlisted",
  },
  {
    id: 4,
    name: "Mini Bluetooth Speaker",
    category: "Electronics",
    cost: 800,
    price: 1499,
    rating: 4.2,
    status: "Pending",
  },
];

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

function Dashboard({ products, setPage }) {
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
          value="5"
          note="Illustrative sample metric"
          icon="◷"
        />
      </div>

      <div className="content-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Recent Products</h2>
              <p>Products currently in your demo workspace.</p>
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
                <select name="status" value={form.status} onChange={updateForm}>
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
                  <td>{getMargin(product.cost, product.price).toFixed(1)}%</td>
                  <td>{product.rating.toFixed(1)} / 5</td>
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

  const categories = ["All", ...new Set(initialTrends.map((item) => item.category))];

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
                    <SignalScore label="Search" score={item.searchInterest} />
                  </td>
                  <td>
                    <SignalScore label="Engagement" score={item.engagement} />
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
  const [products, setProducts] = useState(initialProducts);

function renderPage() {
  if (page === "Dashboard") {
    return <Dashboard products={products} setPage={setPage} />;
  }

  if (page === "Products") {
    return <ProductsPage products={products} setProducts={setProducts} />;
  }

  if (page === "Trend Insights") {
    return <TrendInsightsPage />;
  }

  if (page === "AI Content") {
    return <AIContentStudio products={products} />;
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
              className={`nav-link ${page === item.name ? "active" : ""}`}
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
            Demo Workspace
          </div>
        </header>

        <div className="page-content">{renderPage()}</div>
      </main>
    </div>
  );
}