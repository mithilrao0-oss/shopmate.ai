import { useState } from "react";
import "./App.css";

const products = [
  {
    name: "Portable Blender",
    category: "Kitchen",
    cost: "₹650",
    sellingPrice: "₹1,299",
    margin: "49.9%",
    rating: "4.5",
    status: "Shortlisted",
  },
  {
    name: "LED Desk Lamp",
    category: "Home & Office",
    cost: "₹420",
    sellingPrice: "₹899",
    margin: "53.3%",
    rating: "4.3",
    status: "Under Review",
  },
  {
    name: "Travel Organizer",
    category: "Travel",
    cost: "₹280",
    sellingPrice: "₹599",
    margin: "53.3%",
    rating: "4.6",
    status: "Shortlisted",
  },
  {
    name: "Mini Bluetooth Speaker",
    category: "Electronics",
    cost: "₹800",
    sellingPrice: "₹1,499",
    margin: "46.6%",
    rating: "4.2",
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

function App() {
  const [activePage, setActivePage] = useState("Dashboard");

  function renderPlaceholderPage() {
    let description = "";

    switch (activePage) {
      case "Products":
        description =
          "View and manage discovered products. Product management features will be added here.";
        break;

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

  return (
    <div className="app">
      {/* Sidebar */}
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
              className={`nav-item ${
                activePage === page ? "active" : ""
              }`}
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

      {/* Main Content */}
      <main className="main-content">
        {/* Topbar */}
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className="demo-label">DEMO DATA</span>
            <div className="avatar">M</div>
          </div>
        </header>

        {/* Dashboard Page */}
        {activePage === "Dashboard" ? (
          <>
            <section className="page-heading">
              <div>
                <p className="eyebrow">OVERVIEW</p>
                <h1>Dashboard</h1>
                <p className="subtitle">
                  Discover products, explore trends, and create marketing
                  content.
                </p>
              </div>

              <button
                className="primary-button"
                onClick={() =>
                  setActivePage("Products")
                }
              >
                <span>＋</span> Discover Products
              </button>
            </section>

            {/* Overview Cards */}
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

            {/* Main Dashboard Content */}
            <section className="content-grid">
              {/* Recent Products */}
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
                      {products.map((product) => (
                        <tr key={product.name}>
                          <td>
                            <div className="product-name">
                              <div className="product-placeholder">
                                {product.name.charAt(0)}
                              </div>

                              <strong>{product.name}</strong>
                            </div>
                          </td>

                          <td>{product.category}</td>
                          <td>{product.cost}</td>
                          <td>{product.sellingPrice}</td>
                          <td className="margin">{product.margin}</td>
                          <td>★ {product.rating}</td>

                          <td>
                            <span
                              className={`status status-${product.status
                                .toLowerCase()
                                .replace(" ", "-")}`}
                            >
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

              {/* Workflow */}
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
                    AI-generated content must be reviewed and approved before
                    it can be published.
                  </p>
                </div>
              </article>
            </section>

            {/* Bottom Cards */}
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

            {/* Footer */}
            <footer className="footer">
              <span>ShopMate.ai</span>
              <span>
                AI-assisted product discovery · Human-reviewed content
              </span>
            </footer>
          </>
        ) : (
          /* Placeholder Pages */
          renderPlaceholderPage()
        )}
      </main>
    </div>
  );
}

export default App;