# ShopMate.ai

### AI Agent-Assisted Product Discovery & Auto-Content Platform

ShopMate.ai is a Semester 5 college project for **Artificial Intelligence of Things (AIOT)**. It is designed to help online sellers organize product information, explore early trend signals, and prepare marketing content with AI assistance.

The project aims to demonstrate practical concepts from Generative AI, Prompt Engineering, and Agentic AI through a simple and understandable web application.

> **Project status:** Frontend prototype with demo functionality. Backend services, real AI model integration, database storage, and publishing are not yet implemented.

---

## 1. Problem Statement

Online sellers need to find suitable products and prepare promotional content for them. Doing this manually can take time and require multiple tools.

ShopMate.ai aims to provide a single workspace where sellers can manage product information, view trend insights, and prepare marketing content for review.

---

## 2. Project Objectives

* Organize product information in one workspace.
* Help filter and shortlist products using relevant criteria.
* Display early trend signals without claiming to predict virality.
* Prepare product captions, reel scripts, and descriptions.
* Provide a user interface for reviewing and editing content.
* Design a workflow that keeps humans involved before publishing.
* Demonstrate AIOT concepts through a practical application.

---

## 3. Current Features

The following features are currently available in the frontend prototype:

### Dashboard

* Displays project workspace metrics using demonstration data.
* Provides navigation to the main workspace sections.

### Products

* Displays sample product information.
* Allows the user to interact with the product workspace.
* Product changes currently use frontend state and are not permanently stored.

### Trend Insights

* Displays illustrative trend information.
* Helps demonstrate how products could be explored using trend signals.
* Does not use verified live trend measurements or predict virality.

### AI Content Studio

* Allows the user to select a product.
* Supports Product Caption, Reel Script, and Product Description content types.
* Supports Friendly, Professional, and Exciting tones.
* Generates content using sample templates.
* Allows the generated text to be edited and copied.
* Clearly identifies the current demo mode.

**Important:** The current content generator uses demonstration templates. It is not connected to a real AI model or LLM yet.

### Review Queue

* A review and approval workflow is planned.
* Human review is intended to take place before content is published.

---

## 4. Proposed Workflow

The planned system workflow is:

1. Collect product information.
2. Filter and shortlist products.
3. Explore early trend signals.
4. Generate marketing content.
5. Preview and edit the generated content.
6. Review and approve the content.
7. Prepare approved content for publishing.
8. Use feedback to improve later content decisions.

The workflow will be implemented gradually as the project develops.

---

## 5. Technology Stack

### Current Frontend

* **React** – building the user interface.
* **Vite** – frontend development and build tooling.
* **CSS** – styling the workspace.

### Planned Technologies

* **Python** – implementation of agent and supporting logic.
* **FastAPI** – backend API.
* **SQLite** – simple database storage.
* **Open-source LLM** – planned for real content generation, subject to practical model and environment requirements.

The planned technologies may be adjusted if needed to keep the project functional and suitable for a Semester 5 college project.

---

## 6. AIOT Concepts

ShopMate.ai is intended to demonstrate concepts from the three AIOT units:

### Unit 1 – Foundations of Generative AI and LLMs

The planned LLM integration will demonstrate text generation and the use of an open model.

### Unit 2 – Prompt Engineering

Structured prompts and templates will guide the generation of product captions, reel scripts, and descriptions.

### Unit 3 – Agentic AI and Autonomous Systems

The planned agent workflow will organize tasks such as product filtering, trend analysis, and content preparation. Human review will remain part of the publishing process.

These are project goals; concepts will be documented as implemented when the corresponding functionality is available.

---

## 7. Responsible AI

The project is designed around the following principles:

* **Transparency:** Clearly distinguish demo data and template-generated content from real AI output.
* **Accuracy:** Avoid unsupported product claims, fake reviews, and guaranteed-profit claims.
* **Trend limitations:** Trend signals should not be presented as reliable predictions of virality.
* **Human control:** Content should be reviewed by a person before publishing.
* **Privacy:** Protect API keys and any user information introduced during development.
* **Safety:** Consider avoiding restricted or unsafe product categories where relevant.

---

## 8. Limitations

The current prototype has the following limitations:

* Product information includes demonstration data.
* Product changes are not yet saved permanently.
* Trend insights are illustrative and are not based on verified live measurements.
* The content generator uses sample templates rather than a real AI model.
* The review and approval workflow is not yet implemented.
* Backend APIs and database integration are not yet available.
* Automatic Instagram publishing is not implemented.

---

## 9. Future Scope

Possible future improvements include:

* Implementing a FastAPI backend.
* Adding SQLite storage for products and content drafts.
* Connecting an appropriate open-source LLM.
* Developing product sourcing and filtering logic.
* Implementing trend-signal calculations using available data.
* Building a review and approval queue.
* Improving content generation and preview functionality.
* Exploring a publishing integration if the required API access and permissions are available.
* Testing the complete workflow and documenting the results.

---

## 10. Running the Frontend

Make sure Node.js and npm are installed.

Open a terminal in the frontend directory:

```powershell
cd frontend
```

Install the project dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Open the local address shown in the terminal to view the application.

---

## 11. Academic Project

**Project:** ShopMate.ai
**Subject:** Artificial Intelligence of Things (AIOT)
**Semester:** 5
**Project Type:** College academic project

The project is being developed as a manageable, demonstrable application. Features and implementation status will be updated in this README as development progresses.
