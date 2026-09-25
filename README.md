# ShopMate.ai

**AI-powered product sourcing, trend insights, content generation, and human review workspace.**

ShopMate.ai is a Semester 5 AIOT project that demonstrates an AI-assisted workflow for discovering products, reviewing product trends, generating promotional content, and keeping a human in the loop before content is used.

---

## Overview

ShopMate.ai combines:

- React + Vite frontend
- FastAPI backend
- SQLite database
- Ollama local AI runtime
- Qwen3 1.7B open-source language model

The main workflow is:

**Product Sourcing → Trend Insights → AI Content → Human Review**

The project is designed as an AI-assisted system rather than a fully autonomous publishing system.

---

## Features

### Product Sourcing

- View available products
- Product name and category
- Product price
- Supplier information
- Trend score
- Product API through FastAPI

### Trend Insights

The dashboard presents product trend information to help users identify products that may be useful for further review.

### AI Content Studio

The AI Content Studio generates content for selected products using the local Qwen3 model.

Supported content types:

- Product Caption
- Reel Script
- Product Description

Supported tones:

- Friendly
- Professional
- Exciting

Users can edit the generated content before sending it for review.

### Human Review

Generated content can be sent to the Review Queue where users can:

- Review generated content
- Edit content before approval
- Approve content
- Reject content
- Store review information in SQLite

This provides a human-in-the-loop workflow for AI-generated content.

---

## System Architecture

```text
┌──────────────────────────────┐
│       React Frontend         │
│          Vite + UI           │
│        Port 5173             │
└──────────────┬───────────────┘
               │
               │ HTTP API
               ▼
┌──────────────────────────────┐
│       FastAPI Backend        │
│        Port 5000             │
└───────────┬─────────┬────────┘
            │         │
            │         │
            ▼         ▼
     ┌──────────┐  ┌──────────────┐
     │ SQLite   │  │    Ollama    │
     │ Database │  │  Port 11434  │
     └──────────┘  └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ Qwen3 1.7B   │
                   │ Local LLM    │
                   └──────────────┘
```

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- Requests

### Database

- SQLite

### AI

- Ollama
- Qwen3 1.7B
- Local LLM inference

### Development Tools

- Git
- GitHub
- PowerShell
- Python virtual environment
- npm

---

## Project Structure

```text
shopmate.ai/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── ai.py
│   │   │   ├── products.py
│   │   │   └── reviews.py
│   │   │
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── venv/
│
├── frontend/
│   ├── src/
│   │   ├── AIContentStudio.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   └── package.json
│
└── README.md
```

---

## API Endpoints

### Health

```text
GET /api/health
```

Checks whether the FastAPI backend is running.

### Products

```text
GET /api/products
```

Returns product information used by the application.

### Reviews

```text
GET /api/reviews
POST /api/reviews
PATCH /api/reviews/{review_id}
```

Provides the human review workflow.

### AI Test

```text
POST /api/ai/test
```

Tests communication between FastAPI and the local Ollama model.

### AI Content Generation

```text
POST /api/ai/generate
```

Generates product content using Qwen3 through Ollama.

Example request:

```json
{
  "product_name": "LED Desk Lamp",
  "category": "Home & Office",
  "price": 499,
  "content_type": "Product Caption",
  "tone": "Friendly"
}
```

The backend creates a structured prompt and sends it to the local Qwen3 model.

---

## AI Generation Workflow

```text
User selects product
        ↓
User selects content type
        ↓
User selects tone
        ↓
React sends request
        ↓
FastAPI receives request
        ↓
FastAPI creates AI prompt
        ↓
Ollama runs Qwen3 1.7B
        ↓
Generated content returned
        ↓
User reviews/edits content
        ↓
Send to Review Queue
        ↓
Human approval/rejection
        ↓
Review stored in SQLite
```

---

## Installation

### Prerequisites

Install:

- Python 3.10+
- Node.js
- npm
- Git
- Ollama

---

## Ollama Setup

Install Ollama and download the Qwen3 model:

```bash
ollama pull qwen3:1.7b
```

Check that the model is installed:

```bash
ollama list
```

The project uses:

```text
qwen3:1.7b
```

Ollama runs locally at:

```text
http://localhost:11434
```

---

## Backend Setup

Open PowerShell and navigate to the backend:

```powershell
cd backend
```

Create the Python virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the FastAPI backend:

```powershell
python -m uvicorn app.main:app --port 5000
```

Backend:

```text
http://localhost:5000
```

---

## Frontend Setup

Open another terminal and navigate to the frontend:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## Running the Project

Run the following components:

### 1. Ollama

Make sure Ollama is running and Qwen3 is installed.

### 2. Backend

From the `backend` directory:

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --port 5000
```

### 3. Frontend

From the `frontend` directory:

```powershell
npm run dev
```

Then open:

```text
http://localhost:5173
```

---

## Example Usage

1. Open the ShopMate.ai dashboard.
2. Navigate to **AI Content Studio**.
3. Select a product.
4. Select a content type.
5. Select a tone.
6. Click **Generate Content**.
7. Wait for Qwen3 to generate the content.
8. Review and edit the generated text.
9. Click **Send to Review**.
10. Open the Review Queue.
11. Review the generated content.
12. Approve or reject the draft.

---

## Responsible AI

ShopMate.ai keeps a human in the loop when using AI-generated content.

The system includes the following safeguards:

- AI output is treated as draft content.
- Users can edit generated content.
- Generated content can be reviewed before approval.
- Users are warned to verify product details and claims.
- The AI model runs locally through Ollama in the project setup.
- The system does not automatically publish AI-generated content to social media.

AI-generated text can contain inaccurate or unsupported information. Users should verify important information before using generated content in real-world promotions.

---

## Project Scope

This project is an academic prototype demonstrating an AI-assisted product workflow.

The implemented system demonstrates:

- Product sourcing workspace
- Product API
- Trend-oriented product information
- Local LLM integration
- Qwen3 AI content generation
- Editable AI output
- Human review workflow
- SQLite persistence
- React and FastAPI integration

The current prototype does not include production integrations such as:

- Live supplier marketplaces
- Automatic social-media publishing
- Production cloud deployment
- Large-scale multi-user infrastructure

---

## Demo Information

The project may use demonstration product data and trend information.

Example products include:

- LED Desk Lamp
- Travel Organizer
- Portable Mini Fan
- Portable Blender
- Mini Bluetooth Speaker

Prices, suppliers, and trend scores shown in the prototype should be treated as demonstration data unless connected to a verified external data source.

---

## Repository

GitHub:

https://github.com/mithilrao0-oss/shopmate.ai.git

---

## Project Status

**Functional Semester 5 AIOT Prototype**

The core ShopMate.ai workflow is implemented:

**Product Data → AI Generation → Human Review → SQLite Storage**

The local Qwen3 model is connected to the FastAPI backend through Ollama, and the generated content is displayed in the React frontend.

---

## Author

**Mithil Rao**

Semester 5 AIOT Project

**ShopMate.ai**
