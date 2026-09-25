# ShopMate.ai

## Smart AI Product Sourcing & Content Workspace

ShopMate.ai is a Semester 5 AIOT project that uses an open-source Large Language Model (LLM) to help users discover products, understand trends, generate marketing content, and review AI-generated content before use.

The project focuses on a real-world problem faced by product sellers and small businesses: finding suitable products and creating promotional content efficiently while keeping a human involved in the final decision.

---

## 🎯 Problem Statement

Product sellers often need to:

- Discover potentially useful products
- Identify products with good trend potential
- Create captions, reel scripts, and descriptions
- Review AI-generated marketing content
- Avoid unsupported, unsafe, biased, or inappropriate content

Doing these tasks manually can take significant time.

ShopMate.ai combines product discovery, trend insights, AI content generation, Responsible AI checks, and human review into one workspace.

---

## 💡 Solution

ShopMate.ai provides an integrated workflow:

```text
Product Sourcing
       ↓
Trend Insights
       ↓
AI Content Studio
       ↓
ShopMate Content Agent
       ↓
Qwen3 1.7B via Ollama
       ↓
Responsible AI Screening
       ↓
Human Review
       ↓
Approval
```

The system does not automatically publish AI-generated content.

A human must review and approve the generated content before it is considered ready for use.

---

# 🤖 AI Agent

The main AI agent is implemented in:

```text
backend/app/agent/content_agent.py
```

The agent is called:

```text
ShopMate Content Agent
```

### Agent workflow

The agent performs the following steps:

1. Task analysis
2. Prompt construction
3. Qwen3 generation
4. Responsible AI screening
5. Revision and regeneration when required
6. Human review

The API route connecting the frontend to the agent is:

```text
backend/app/routes/ai.py
```

The frontend displays the agent information and workflow inside:

```text
frontend/src/AIContentStudio.jsx
```

---

# 🧠 Open-Source AI Model

ShopMate.ai uses:

```text
Model: Qwen3 1.7B
Runtime: Ollama
Processing: Local
```

Ollama runs the model locally and exposes an API used by the FastAPI backend.

The application sends product and content requirements to the ShopMate Content Agent, which constructs a task-specific prompt before calling Qwen3.

---

# ✍️ AI Content Generation

The AI Content Studio supports:

- Product Captions
- Reel Scripts
- Product Descriptions

Users can select:

### Product

- LED Desk Lamp
- Travel Organizer
- Portable Mini Fan

### Content Tone

- Friendly
- Professional
- Exciting

The generated content is displayed in the Content Preview area where the user can review and edit it.

---

# 🛡 Responsible AI

Responsible AI is an important part of the ShopMate.ai workflow.

### 🔒 Privacy

AI generation uses the locally running Ollama/Qwen3 model.

The system includes basic screening for possible personal information such as email addresses and phone numbers.

### 👁 Transparency

The interface clearly displays:

- AI model
- Agent name
- Content type
- Tone
- Number of generation attempts
- Whether revision was performed
- Agent workflow

### 🛡 Safety

The agent prompt instructs the model to avoid:

- Unsupported claims
- Exaggerated guarantees
- Medical claims
- Financial claims
- Unsafe claims
- Invented product specifications

Generated content remains editable and requires human review.

### ⚖ Fairness

Generated content is screened for potentially inappropriate or discriminatory wording.

The screening includes checks for examples of:

- Stereotyping
- Insults
- Degrading language
- Discriminatory wording

The Responsible AI screening is a first-level automated check and is not a guarantee that generated content is completely safe or unbiased.

---

# 👤 Human-in-the-Loop

ShopMate.ai follows a human-in-the-loop approach.

AI-generated content is **not automatically published**.

The workflow is:

```text
AI Generation
     ↓
Responsible AI Check
     ↓
Content Preview
     ↓
Send to Review
     ↓
Human Review
     ↓
Approve / Reject
```

The Review Queue allows the user to review the generated content and approve it before further use.

This helps keep the final decision with a human rather than the AI system.

---

# 🖥️ Application Modules

## Dashboard

Provides an overview of the workspace including:

- Products discovered
- Shortlisted products
- Generated content
- Pending reviews

## Products

Displays product information such as:

- Product name
- Category
- Price
- Supplier
- Trend score

## Trend Insights

Provides trend-oriented information to help identify potentially useful products.

## AI Content Studio

The main AI generation interface.

Users can:

- Select a product
- Select content type
- Select tone
- Generate content
- View the AI agent workflow
- Inspect Responsible AI results
- Edit generated content
- Send content for human review

## Review Queue

Provides a human review stage for AI-generated content.

Content can be reviewed and approved before being considered ready for use.

---

# 🏗️ Technology Stack

## Frontend

- React
- Vite
- JavaScript
- CSS

## Backend

- Python
- FastAPI
- Pydantic
- Requests

## Database

- SQLite

## AI

- Qwen3 1.7B
- Ollama

## Development Tools

- VS Code
- Git
- GitHub
- Node.js
- Python

---

# 📁 Project Structure

```text
shopmate.ai/
│
├── backend/
│   └── app/
│       ├── agent/
│       │   ├── __init__.py
│       │   └── content_agent.py
│       │
│       ├── routes/
│       │   ├── ai.py
│       │   ├── products.py
│       │   └── reviews.py
│       │
│       ├── database.py
│       └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── AIContentStudio.jsx
│   │   ├── App.jsx
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── README.md
└── ...
```

---

# 🔌 API Endpoints

## Health Check

```text
GET /api/health
```

Checks whether the backend is running.

## Products

```text
GET /api/products
```

Returns product information.

## Reviews

```text
GET /api/reviews
POST /api/reviews
PATCH /api/reviews/{review_id}
```

Used for the human review workflow.

## AI Test

```text
POST /api/ai/test
```

Tests direct communication with the local Qwen3/Ollama service.

## AI Content Generation

```text
POST /api/ai/generate
```

Runs the ShopMate Content Agent.

The response includes:

- Generated content
- Model
- Agent
- Workflow
- Generation attempts
- Revision status
- Responsible AI result

---

# ⚙️ Running the Project

## 1. Start Ollama

Make sure Ollama is installed and the Qwen3 model is available.

```powershell
ollama run qwen3:1.7b
```

## 2. Start the FastAPI Backend

Open a terminal:

```powershell
cd "C:\Users\om\OneDrive\Desktop\shopmate.ai\backend"
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload --port 5000
```

Backend:

```text
http://localhost:5000
```

## 3. Start the Frontend

Open another terminal:

```powershell
cd "C:\Users\om\OneDrive\Desktop\shopmate.ai\frontend"
```

Start Vite:

```powershell
npm.cmd run dev
```

Frontend:

```text
http://localhost:5173
```

> On some Windows PowerShell configurations, `npm` may be blocked by the execution policy. `npm.cmd run dev` can be used instead.

---

# 🔄 Complete AI Workflow

```text
                    ┌──────────────────┐
                    │ Select Product   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Select Content   │
                    │ Type + Tone      │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ ShopMate Content │
                    │ Agent            │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Prompt           │
                    │ Construction     │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Qwen3 1.7B       │
                    │ via Ollama       │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Responsible AI   │
                    │ Screening        │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Content Preview  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Human Review     │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Approval         │
                    └──────────────────┘
```

---

# 🧪 Example

### Input

```text
Product:
LED Desk Lamp

Category:
Home & Office

Price:
₹499

Content Type:
Product Caption

Tone:
Friendly
```

### AI Output

The ShopMate Content Agent generates a product caption using Qwen3.

The generated result is then screened by the Responsible AI layer and displayed for human review.

The user can edit the content and send it to the Review Queue.

---

# ⚠️ AI Limitations

AI-generated content may contain:

- Incorrect product claims
- Unsupported specifications
- Exaggerated marketing language
- Inappropriate wording
- Other generation errors

Therefore:

```text
AI output ≠ automatically trusted output
```

Users should verify product details and claims before using generated content in real promotional material.

The Responsible AI checks are designed as a first-level safeguard and do not guarantee perfect safety, fairness, or factual accuracy.

---

# 🔐 Privacy

ShopMate.ai uses a locally running Ollama/Qwen3 model for AI generation.

This project does not require sending product-generation prompts to a cloud-based AI API for the demonstrated workflow.

Users should still avoid entering unnecessary personal or confidential information into the application.

---

# 🎓 Academic Project

**Project:** ShopMate.ai  
**Semester:** 5  
**Project Type:** AIOT / Artificial Intelligence Application  
**LLM:** Qwen3 1.7B  
**Open-Source AI Runtime:** Ollama

The project demonstrates:

```text
Real-world Problem
        ↓
Prompt Engineering
        ↓
Open-Source LLM
        ↓
AI Agent / Workflow
        ↓
AI Output
        ↓
User-Friendly Interface
        ↓
Responsible AI
        ↓
Human Review
```

---

# 🚀 Future Improvements

Possible future improvements include:

- More product sources
- Automated trend-data collection
- Better product ranking
- More advanced Responsible AI classifiers
- Multilingual content generation
- Persistent user accounts
- Additional AI agents
- Social media platform integrations
- Automated content scheduling
- More advanced hallucination detection

---

## 📌 Project Principle

> **AI assists the user; the human makes the final decision.**

ShopMate.ai is designed to make product research and content creation faster while keeping transparency, Responsible AI, and human review at the center of the workflow.
