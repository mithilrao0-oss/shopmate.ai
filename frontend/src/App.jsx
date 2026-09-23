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

function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <div>
            <h2>ShopMate<span>.ai</span></h2>
            <p>AI Commerce Assistant</p>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav className="navigation">
          <a className="nav-item active" href="#dashboard">
            <span>▦</span> Dashboard
          </a>
          <a className="nav-item" href="#products">
            <span>□</span> Products
          </a>
          <a className="nav-item" href="#trends">
            <span>↗</span> Trend Insights
          </a>
          <a className="nav-item" href="#content">
            <span>✎</span> AI Content
          </a>
          <a className="nav-item" href="#reviews">
            <span>✓</span> Review Queue
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="demo-badge">
            <span className="status-dot"></span>
            Demo Mode
          </div>
          <p>ShopMate.ai · Semester 5 Project</p>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>Dashboard</strong>
          </div>

          <div className="topbar-right">
            <span className="demo-label">DEMO DATA</span>
            <div className="avatar">M</div>
          </div>
        </header>

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
            onClick={() => alert("Product discovery will be connected in a later step.")}
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
          <article className="panel products-panel" id="products">
            <div className="panel-heading">
              <div>
                <h2>Recent Products</h2>
                <p>Example products for the dashboard preview</p>
              </div>
              <button
                className="text-button"
                onClick={() => alert("The complete product list will be added later.")}
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
              These are illustrative sample products, not live supplier listings.
            </div>
          </article>

          <article className="panel activity-panel" id="reviews">
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
                  <h3>Filter & Trend Analysis</h3>
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
          <article className="mini-panel" id="trends">
            <div className="mini-icon trend-icon">↗</div>
            <div>
              <h3>Trend Insights</h3>
              <p>Explore product signals and momentum.</p>
            </div>
            <span className="coming-soon">Coming next</span>
          </article>

          <article className="mini-panel" id="content">
            <div className="mini-icon content-icon">✎</div>
            <div>
              <h3>AI Content Studio</h3>
              <p>Prepare product scripts and captions.</p>
            </div>
            <span className="coming-soon">Coming next</span>
          </article>
        </section>

        <footer className="footer">
          <span>ShopMate.ai</span>
          <span>AI-assisted product discovery · Human-reviewed content</span>
        </footer>
      </main>
    </div>
  );
}

export default App;