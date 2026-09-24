const express = require("express");
const cors = require("cors");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Database location
const databasePath = path.join(__dirname, "..", "shopmate.db");

// Open or create the SQLite database
const db = new sqlite3.Database(databasePath, (error) => {
  if (error) {
    console.error("Database connection failed:", error.message);
  } else {
    console.log("Connected to the ShopMate.ai SQLite database.");
  }
});

// Create the review drafts table
db.run(`
  CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    productName TEXT NOT NULL,
    contentType TEXT NOT NULL,
    tone TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    createdAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
  )
`);

// Health check
app.get("/api/health", (req, res) => {
  res.json({
    status: "ok",
    message: "ShopMate.ai backend is running"
  });
});

// Get all review drafts
app.get("/api/reviews", (req, res) => {
  db.all(
    "SELECT * FROM reviews ORDER BY id DESC",
    [],
    (error, rows) => {
      if (error) {
        return res.status(500).json({
          error: "Could not retrieve review drafts"
        });
      }

      res.json(rows);
    }
  );
});

// Save a new review draft
app.post("/api/reviews", (req, res) => {
  const { productName, contentType, tone, content } = req.body;

  if (!productName || !contentType || !tone || !content) {
    return res.status(400).json({
      error: "productName, contentType, tone, and content are required"
    });
  }

  const sql = `
    INSERT INTO reviews (productName, contentType, tone, content, status)
    VALUES (?, ?, ?, ?, 'Pending')
  `;

  db.run(
    sql,
    [productName, contentType, tone, content],
    function (error) {
      if (error) {
        return res.status(500).json({
          error: "Could not save the review draft"
        });
      }

      db.get(
        "SELECT * FROM reviews WHERE id = ?",
        [this.lastID],
        (selectError, row) => {
          if (selectError) {
            return res.status(500).json({
              error: "Draft was saved, but could not be retrieved"
            });
          }

          res.status(201).json(row);
        }
      );
    }
  );
});

// Update a draft's review status
app.patch("/api/reviews/:id", (req, res) => {
  const { status } = req.body;
  const { id } = req.params;

  const allowedStatuses = ["Pending", "Approved", "Rejected"];

  if (!allowedStatuses.includes(status)) {
    return res.status(400).json({
      error: "Status must be Pending, Approved, or Rejected"
    });
  }

  db.run(
    "UPDATE reviews SET status = ? WHERE id = ?",
    [status, id],
    function (error) {
      if (error) {
        return res.status(500).json({
          error: "Could not update the review status"
        });
      }

      if (this.changes === 0) {
        return res.status(404).json({
          error: "Review draft not found"
        });
      }

      db.get(
        "SELECT * FROM reviews WHERE id = ?",
        [id],
        (selectError, row) => {
          if (selectError) {
            return res.status(500).json({
              error: "Status updated, but could not retrieve the draft"
            });
          }

          res.json(row);
        }
      );
    }
  );
});

// Start the server
app.listen(PORT, () => {
  console.log(`ShopMate.ai backend running at http://localhost:${PORT}`);
});