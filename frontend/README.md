# ShopMate.ai

### AI-Powered Product Discovery & Auto-Content Dropshipping Platform

ShopMate.ai is a Semester 5 AIOT college project that demonstrates how AI agents can support product discovery and marketing content creation for a dropshipping workflow.

The project is designed as a smart workspace where users can explore products, view trend insights, generate marketing content, and review drafts before using them.

## Project Objectives

* Collect and organize product information.
* Filter products using defined criteria.
* Surface potential trends using available engagement signals.
* Generate marketing content for selected products.
* Allow users to review and approve or reject generated drafts.
* Demonstrate how AI agents can assist a dropshipping workflow.

> ShopMate.ai surfaces trend signals; it does not claim to predict virality or guarantee product success.

## Current Features

### 1. Dashboard

A workspace overview for navigating the application's main sections.

### 2. Products

A product workspace for viewing product information. Current product information is prototype/demo data.

### 3. Trend Insights

A section for displaying product trend information. Trend data and scoring are part of the prototype and should not be treated as guaranteed predictions.

### 4. AI Content

A content studio for generating draft marketing content, including product headlines, descriptions, and calls to action. The current generator uses templates and is not yet connected to a real LLM.

### 5. Review Queue

Generated drafts can be sent to the review queue. Users can approve or reject drafts.

Drafts and review statuses are stored in a local SQLite database through the backend API. Refreshing the page does not remove saved drafts.

**Instagram publishing is not implemented.** Drafts must be reviewed, and nothing is automatically published to Instagram.

## Technology Stack

* **Frontend:** React, Vite
* **Backend:** Node.js, Express
* **Database:** SQLite
* **Version Control:** Git and GitHub

Python-based product sourcing and trend-agent components are also included in the project structure and can be developed further.

## Project Structure

```text
shopmate.ai/
├── agents/
│   ├── product_sourcing_agent/
│   ├── shared/
│   └── trend_agent/
├── backend/
│   └── src/
├── content-pipeline/
├── frontend/
│   └── src/
├── .env.example
├── .gitignore
├── README.md
└── scaffold.ps1
```

## Running the Project Locally

### Requirements

* Node.js and npm
* Git

### 1. Start the Backend

Open a terminal and run:

```powershell
cd "C:\Users\Admin\Desktop\sem5 pro\shopmate.ai\backend"
npm.cmd install
npm.cmd run dev
```

The backend runs at:

```text
http://localhost:5000
```

Health-check endpoint:

```text
http://localhost:5000/api/health
```

### 2. Start the Frontend

Open a **second terminal** and run:

```powershell
cd "C:\Users\Admin\Desktop\sem5 pro\shopmate.ai\frontend"
npm.cmd install
npm.cmd run dev
```

Open the local Vite address shown in the terminal, usually:

```text
http://localhost:5173/
```

Keep both terminals running while using the application.

## Backend API

| Method | Endpoint           | Purpose                              |
| ------ | ------------------ | ------------------------------------ |
| GET    | `/api/health`      | Check whether the backend is running |
| GET    | `/api/reviews`     | Retrieve saved review drafts         |
| POST   | `/api/reviews`     | Save a new draft in the review queue |
| PATCH  | `/api/reviews/:id` | Update a draft's review status       |

Supported review statuses are **Pending**, **Approved**, and **Rejected**.

## Current Limitations

* Product and trend information is prototype/demo data.
* The current content generator uses templates rather than a connected LLM.
* Instagram publishing and fully autonomous posting are not implemented.
* Supplier reliability, delivery, cash-on-delivery logistics, and returns are outside the current prototype's automated workflow.
* Trend signals do not guarantee sales or product success.

## Future Scope

* Connect an open-source LLM for content generation.
* Develop and integrate product sourcing and trend-analysis agents.
* Connect reliable supplier and product data sources.
* Add a human approval workflow for any future social-media publishing integration.
* Expand testing, error handling, and data management.

## Responsible AI

ShopMate.ai is intended to assist users rather than make guaranteed business predictions. Users should review generated content before use, verify product and supplier information, and consider privacy, fairness, and accuracy when integrating AI services.

## Academic Context

**Project:** ShopMate.ai
**Semester:** 5
**Subject:** AIOT
