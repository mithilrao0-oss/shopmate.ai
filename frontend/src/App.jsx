import { useState } from "react";
import "./App.css";

// Sample products for demonstration.
// These are not live supplier listings.
const initialProducts = [
  {
    id: 1,
    name: "Portable Blender",
    category: "Kitchen",
    cost: 650,
    sellingPrice: 1299,
    rating: 4.5,
    status: "Shortlisted",
  },
  {
    id: 2,
    name: "LED Desk Lamp",
    category: "Home & Office",
    cost: 420,
    sellingPrice: 899,
    rating: 4.3,
    status: "Under Review",
  },
  {
    id: 3,
    name: "Travel Organizer",
    category: "Travel",
    cost: 280,
    sellingPrice: 599,
    rating: 4.6,
    status: "Shortlisted",
  },
  {
    id: 4,
    name: "Mini Bluetooth Speaker",
    category: "Electronics",
    cost: 800,
    sellingPrice: 1499,
    rating: 4.2,
    status: "Pending",
  },
];

const overview = [
  {
    label: "Products Discovered",
    value: "128",
    note: "Sample dashboard data",
    icon: "▦",
  },
  {
    label: "Shortlisted Products",
    value: "32",
    note: "Passed initial filters",
    icon: "✓",
  },
  {
    label: "Content Generated",
    value: "18",
    note: "Scripts and captions",
    icon: "✎",
  },
  {
    label: "Pending Reviews",
    value: "5",
    note: "Awaiting human approval",
    icon: "◷",
  },
];

const pages = [
  "Dashboard",
  "Products",
  "Trend Insights",
  "AI Content",
  "Review Queue",
];

function getPageIcon(page) {
  switch (page) {
    case "Dashboard":
      return "▦";
    case "Products":
      return "□";
    case "Trend Insights":
      return "↗";
    case "AI Content":
      return "✎";
    case "Review Queue":
      return "✓";
    default:
      return "•";
  }
}

function formatPrice(price) {
  return `₹${Number(price).toLocaleString("en-IN")}`;
}

function calculateMargin(product) {
  if (!product.sellingPrice || product.sellingPrice <= 0) {
    return "0.0%";
  }

  const margin =
    ((product.sellingPrice - product.cost) / product.sellingPrice) * 100;

  return `${margin.toFixed(1)}%`;
}

function getStatusClass(status) {
  return `status status-${status.toLowerCase().replaceAll(" ", "-")}`;
}

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  // Product list can be updated through the Add Product form.
  const [products, setProducts] = useState(initialProducts);

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [selectedStatus, setSelectedStatus] = useState("All Statuses");

  const [showAddForm, setShowAddForm] = useState(false);

  const [newProduct, setNewProduct] = useState({
    name: "",
    category: "Kitchen",
    cost: "",
    sellingPrice: "",
    rating: "",
    status: "Pending",
  });

  const categories = [
    "All Categories",
    ...new Set(products.map((product) => product.category)),
  ];

  const statuses = [
    "All Statuses",
    "Shortlisted",
    "Under Review",
    "Pending",
  ];

  const filteredProducts = products.filter((product) => {
    const matchesSearch = product.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    const matchesCategory =
      selectedCategory === "All Categories" ||
      product.category === selectedCategory;

    const matchesStatus =
      selectedStatus === "All Statuses" ||
      product.status === selectedStatus;

    return matchesSearch && matchesCategory && matchesStatus;
  });

  function handleInputChange(event) {
    const { name, value } = event.target;

    setNewProduct((previousProduct) => ({
      ...previousProduct,
      [name]: value,
    }));
  }

  function handleAddProduct(event) {
    event.preventDefault();

    const cost = Number(newProduct.cost);
    const sellingPrice = Number(newProduct.sellingPrice);
    const rating = Number(newProduct.rating);

    if (
      !newProduct.name.trim() ||
      !newProduct.category ||
      newProduct.cost === "" ||
      newProduct.sellingPrice === "" ||
      newProduct.rating === ""
    ) {
      alert("Please fill in all product details.");
      return;
    }

    if (
      !Number.isFinite(cost) ||
      !Number.isFinite(sellingPrice) ||
      cost < 0 ||
      sellingPrice <= 0
    ) {
      alert("Please enter valid cost and selling prices.");
      return;
    }

    if (!Number.isFinite(rating) || rating < 0 || rating > 5) {
      alert("Please enter a rating between 0 and 5.");
      return;
    }

    const productToAdd = {
      id: Date.now(),
      name: newProduct.name.trim(),
      category: newProduct.category,
      cost,
      sellingPrice,
      rating,
      status: newProduct.status,
    };

    setProducts((previousProducts) => [
      productToAdd,
      ...previousProducts,
    ]);

    setNewProduct({
      name: "",
      category: "Kitchen",
      cost: "",
      sellingPrice: "",
      rating: "",
      status: "Pending",
    });

    setShowAddForm(false);
    setSearchTerm("");
    setSelectedCategory("All Categories");
    setSelectedStatus("All Statuses");
  }

  function renderProductsPage() {
    return (
      <>
        <section className="page-heading">
          <div>
            <p className="eyebrow">PRODUCT MANAGEMENT</p>
            <h1>Products</h1>
            <p className="subtitle">
              Search, filter, and manage your discovered products.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={() => setShowAddForm(!showAddForm)}
          >
            <span>＋</span> {showAddForm ? "Cancel" : "Add Product"}
          </button>
        </section>

        {showAddForm && (
          <section className="panel add-product-panel">
            <div className="panel-heading">
              <div>
                <h2>Add a Product</h2>
                <p>Enter product details to add it to this demo list.</p>
              </div>
            </div>

            <form onSubmit={handleAddProduct} className="product-form">
              <div className="form-grid">
                <label className="form-field">
                  <span>Product Name</span>
                  <input
                    type="text"
                    name="name"
                    placeholder="e.g. Wireless Earbuds"
                    value={newProduct.name}
                    onChange={handleInputChange}
                    required
                  />
                </label>

                <label className="form-field">
                  <span>Category</span>
                  <select
                    name="category"
                    value={newProduct.category}
                    onChange={handleInputChange}
                  >
                    <option>Kitchen</option>
                    <option>Home & Office</option>
                    <option>Travel</option>
                    <option>Electronics</option>
                    <option>Fashion</option>
                    <option>Beauty</option>
                    <option>Other</option>
                  </select>
                </label>

                <label className="form-field">
                  <span>Cost Price (₹)</span>
                  <input
                    type="number"
                    name="cost"
                    min="0"
                    step="0.01"
                    placeholder="e.g. 500"
                    value={newProduct.cost}
                    onChange={handleInputChange}
                    required
                  />
                </label>

                <label className="form-field">
                  <span>Selling Price (₹)</span>
                  <input
                    type="number"
                    name="sellingPrice"
                    min="0.01"
                    step="0.01"
                    placeholder="e.g. 999"
                    value={newProduct.sellingPrice}
                    onChange={handleInputChange}
                    required
                  />
                </label>

                <label className="form-field">
                  <span>Rating (0–5)</span>
                  <input
                    type="number"
                    name="rating"
                    min="0"
                    max="5"
                    step="0.1"
                    placeholder="e.g. 4.2"
                    value={newProduct.rating}
                    onChange={handleInputChange}
                    required
                  />
                </label>

                <label className="form-field">
                  <span>Status</span>
                  <select
                    name="status"
                    value={newProduct.status}
                    onChange={handleInputChange}
                  >
                    <option>Pending</option>
                    <option>Under Review</option>
                    <option>Shortlisted</option>
                  </select>
                </label>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowAddForm(false)}
                >
                  Cancel
                </button>

                <button type="submit" className="primary-button">
                  Save Product
                </button>
              </div>
            </form>
          </section>
        )}

        <section className="panel products-panel">
          <div className="panel-heading">
            <div>
              <h2>Product List</h2>
              <p>
                Showing {filteredProducts.length} of {products.length} products
              </p>
            </div>
            <span className="demo-label">DEMO DATA</span>
          </div>

          <div className="product-filters">
            <label className="filter-field">
              <span>Search products</span>
              <input
                type="search"
                placeholder="Search by product name..."
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
              />
            </label>

            <label className="filter-field">
              <span>Category</span>
              <select
                value={selectedCategory}
                onChange={(event) => setSelectedCategory(event.target.value)}
              >
                {categories.map((category) => (
                  <option key={category}>{category}</option>
                ))}
              </select>
            </label>

            <label className="filter-field">
              <span>Status</span>
              <select
                value={selectedStatus}
                onChange={(event) => setSelectedStatus(event.target.value)}
              >
                {statuses.map((status) => (
                  <option key={status}>{status}</option>
                ))}
              </select>
            </label>

            <button
              className="secondary-button clear-filters-button"
              onClick={() => {
                setSearchTerm("");
                setSelectedCategory("All Categories");
                setSelectedStatus("All Statuses");
              }}
            >
              Clear Filters
            </button>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>PRODUCT</th>
                  <th>CATEGORY</th>
                  <th>COST</th>
                  <th>SELLING PRICE</th>
                  <th>MARGIN</th>
                  <th>RATING</th>
                  <th>STATUS</th>
                </tr>
              </thead>

              <tbody>
                {filteredProducts.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <div className="product-name">
                        <div className="product-placeholder">
                          {product.name.charAt(0).toUpperCase()}
                        </div>
                        <strong>{product.name}</strong>
                      </div>
                    </td>

                    <td>{product.category}</td>
                    <td>{formatPrice(product.cost)}</td>
                    <td>{formatPrice(product.sellingPrice)}</td>
                    <td className="margin">{calculateMargin(product)}</td>
                    <td>★ {Number(product.rating).toFixed(1)}</td>

                    <td>
                      <span className={getStatusClass(product.status)}>
                        {product.status}
                      </span>
                    </td>
                  </tr>
                ))}

                {filteredProducts.length === 0 && (
                  <tr>
                    <td colSpan="7" className="empty-table-message">
                      No products match your search or filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="demo-notice">
            <span>ⓘ</span>
            Products are stored in the page's temporary React state. They are
            sample data and will reset when the page is reloaded.
          </div>
        </section>
      </>
    );
  }

  function renderPlaceholderPage() {
    let description = "";

    switch (activePage) {
      case "Trend Insights":
        description =
          "Explore product trends and available signals. Trend analysis features will be added here.";
        break;

      case "AI Content":
        description =
          "Prepare marketing content for your products. AI content generation will be added here.";
        break;

      case "Review Queue":
        description =
          "Review AI-generated content before publication. Review and approval controls will be added here.";
        break;

      default:
        description = "Explore the ShopMate.ai workspace.";
    }

    return (
      <section className="page-heading">
        <div>
          <p className="eyebrow">WORKSPACE</p>
          <h1>{activePage}</h1>
          <p className="subtitle">{description}</p>
        </div>
      </section>
    );
  }

  function renderDashboard() {
    return (
      <>
        <section className="page-heading">
          <div>
            <p className="eyebrow">OVERVIEW</p>
            <h1>Dashboard</h1>
            <p className="subtitle">
              Discover products, explore trends, and create marketing content.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={() => setActivePage("Products")}
          >
            <span>＋</span> Discover Products
          </button>
        </section>

        <section className="overview-grid">
          {overview.map((item) => (
            <article className="overview-card" key={item.label}>
              <div className="card-top">
                <span className="card-label">{item.label}</span>
                <span className="card-icon">{item.icon}</span>
              </div>

              <h2>{item.value}</h2>
              <p>{item.note}</p>
            </article>
          ))}
        </section>

        <section className="content-grid">
          <article className="panel products-panel">
            <div className="panel-heading">
              <div>
                <h2>Recent Products</h2>
                <p>Example products for the dashboard preview</p>
              </div>

              <button
                className="text-button"
                onClick={() => setActivePage("Products")}
              >
                View all <span>→</span>
              </button>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>PRODUCT</th>
                    <th>CATEGORY</th>
                    <th>COST</th>
                    <th>SELLING PRICE</th>
                    <th>MARGIN</th>
                    <th>RATING</th>
                    <th>STATUS</th>
                  </tr>
                </thead>

                <tbody>
                  {products.slice(0, 4).map((product) => (
                    <tr key={product.id}>
                      <td>
                        <div className="product-name">
                          <div className="product-placeholder">
                            {product.name.charAt(0).toUpperCase()}
                          </div>
                          <strong>{product.name}</strong>
                        </div>
                      </td>

                      <td>{product.category}</td>
                      <td>{formatPrice(product.cost)}</td>
                      <td>{formatPrice(product.sellingPrice)}</td>
                      <td className="margin">{calculateMargin(product)}</td>
                      <td>★ {Number(product.rating).toFixed(1)}</td>

                      <td>
                        <span className={getStatusClass(product.status)}>
                          {product.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="demo-notice">
              <span>ⓘ</span>
              These are illustrative sample products, not live supplier
              listings.
            </div>
          </article>

          <article className="panel activity-panel">
            <div className="panel-heading">
              <div>
                <h2>Workflow</h2>
                <p>Your AI-assisted process</p>
              </div>
            </div>

            <div className="workflow">
              <div className="workflow-step">
                <div className="workflow-icon completed">✓</div>
                <div>
                  <h3>Product Discovery</h3>
                  <p>Collect product information</p>
                </div>
                <span className="step-tag">1</span>
              </div>

              <div className="workflow-line"></div>

              <div className="workflow-step">
                <div className="workflow-icon completed">✓</div>
                <div>
                  <h3>Filter &amp; Trend Analysis</h3>
                  <p>Apply rules and inspect signals</p>
                </div>
                <span className="step-tag">2</span>
              </div>

              <div className="workflow-line"></div>

              <div className="workflow-step">
                <div className="workflow-icon">✎</div>
                <div>
                  <h3>Generate Content</h3>
                  <p>Create scripts and captions</p>
                </div>
                <span className="step-tag">3</span>
              </div>

              <div className="workflow-line"></div>

              <div className="workflow-step">
                <div className="workflow-icon">✓</div>
                <div>
                  <h3>Human Review</h3>
                  <p>Review before publishing</p>
                </div>
                <span className="step-tag">4</span>
              </div>
            </div>

            <div className="approval-note">
              <strong>Human approval required</strong>
              <p>
                AI-generated content must be reviewed and approved before it
                can be published.
              </p>
            </div>
          </article>
        </section>

        <section className="bottom-grid">
          <article className="mini-panel">
            <div className="mini-icon trend-icon">↗</div>

            <div>
              <h3>Trend Insights</h3>
              <p>Explore product signals and momentum.</p>
            </div>

            <button
              className="coming-soon"
              onClick={() => setActivePage("Trend Insights")}
            >
              Explore →
            </button>
          </article>

          <article className="mini-panel">
            <div className="mini-icon content-icon">✎</div>

            <div>
              <h3>AI Content Studio</h3>
              <p>Prepare product scripts and captions.</p>
            </div>

            <button
              className="coming-soon"
              onClick={() => setActivePage("AI Content")}
            >
              Explore →
            </button>
          </article>
        </section>

        <footer className="footer">
          <span>ShopMate.ai</span>
          <span>
            AI-assisted product discovery · Human-reviewed content
          </span>
        </footer>
      </>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>

          <div>
            <h2>
              ShopMate<span>.ai</span>
            </h2>
            <p>AI Commerce Assistant</p>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav className="navigation">
          {pages.map((page) => (
            <a
              key={page}
              href={`#${page.toLowerCase().replaceAll(" ", "-")}`}
              className={`nav-item ${activePage === page ? "active" : ""}`}
              onClick={(event) => {
                event.preventDefault();
                setActivePage(page);
              }}
            >
              <span>{getPageIcon(page)}</span>
              {page}
            </a>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="demo-badge">
            <span className="status-dot"></span>
            Demo Mode
          </div>

          <p>ShopMate.ai · Semester 5 Project</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className="demo-label">DEMO DATA</span>
            <div className="avatar">M</div>
          </div>
        </header>

        {activePage === "Dashboard" && renderDashboard()}
        {activePage === "Products" && renderProductsPage()}
        {activePage !== "Dashboard" &&
          activePage !== "Products" &&
          renderPlaceholderPage()}
      </main>
    </div>
  );
}

export default App;