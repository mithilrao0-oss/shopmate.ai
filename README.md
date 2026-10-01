# ShopMate.ai

## Smart AI Product Sourcing & Content Workspace

ShopMate.ai is an AI-powered workspace for e-commerce sellers to discover products, analyze trends, and generate marketing content (captions, descriptions, and Instagram reel scripts) with human review at every stage.

The project showcases:
- A **human-in-the-loop workflow**: AI drafts content, and a person reviews it before use.
- **Responsible AI screening** at multiple stages (generation, editing, submission).
- **Structured reel scripts** (JSON) that are validated before reaching a person.
- **Local AI inference** using Ollama and the small Qwen3 1.7B model, so no data leaves your machine.

**Status:** Core features complete. Next: video rendering and Instagram publishing (planned).

---

## 🎯 Problem Statement

Manual content creation for product listings is time-consuming. AI can help draft ideas faster, but AI output needs verification—it often invents product details, misses key facts, or makes unsupported claims.

**Solution:** A workspace where AI drafts content, rules reject obvious mistakes, and humans always make the final call before anything goes public.

---

## 💡 How It Works

### 1. Product Discovery
Users browse or add products (name, category, price, highlights).

### 2. AI Content Generation
Pick a product, choose a content type (caption, description, or reel script), and tone. The AI agent generates a draft.

For **reel scripts**, the output is structured JSON: 4 scenes, each with a voiceover (≤20 words) and on-screen text (≤7 words), plus a caption and hashtags. This structure prepares the script for video rendering and Instagram publishing.

### 3. Validation & Screening
- **Reel scripts:** Code checks for stage directions, invented testimonials, unsupported claims, emoji in voiceover, missing product name, and rule violations.
- **Text content:** Responsible AI screening for biased wording, privacy leaks, and risky claims.

If the first attempt fails, the agent is told why and regenerates once.

### 4. Human Review
The user edits and refines the draft, then sends it to the Review Queue.

### 5. Review Queue
Approved drafts are marked for use. Rejected drafts loop back.

---

## 🤖 AI Agent

**Model:** Qwen3 1.7B (via Ollama)

**Workflow:**
1. Task analysis
2. Prompt construction
3. Qwen3 structured JSON generation (for reels) or text generation (for captions)
4. Validation (reel scripts) or Responsible AI screening (text)
5. Retry once if flagged, with detailed feedback
6. Human review

**Product Facts:** The AI can only mention facts listed in a product's `highlights`. The demo highlights are minimal; real sellers should replace them with verified product facts (e.g., "waterproof", "battery life 8 hours", "weighs 200g").

---

## ✍️ AI Content Types

### Product Caption
A short, punchy description for e-commerce listings. Plain text, single paragraph.

### Product Description
A longer, detailed product description. Plain text.

### Reel Script
A structured 4-scene Instagram Reel script (JSON):
- **Scene 1 - Hook:** Attention-grabbing opening (≤20 words).
- **Scene 2 - Product:** Introduce the product by its exact name (≤20 words).
- **Scene 3 - Benefit:** One key benefit (≤20 words).
- **Scene 4 - Call to action:** Invite viewers to check it out (≤20 words).
- **Instagram caption:** 1-2 sentences.
- **Hashtags:** 3 to 5 relevant tags.

The script validates and rejects:
- Stage directions, brackets, markdown, or emoji in voiceover
- Invented customer opinions, testimonials, quotes, or fake ratings
- Numbers not provided (only the product price is allowed)
- Unsupported claims (discounts, guarantees, specifications, superlatives)
- Missing product name or violated line lengths
- Biased wording, privacy risks, or risky claims (from Responsible AI check)

---

## 🛡️ Responsible AI

Every draft is screened for:

- **Privacy:** No email addresses, phone numbers, or personal info.
- **Fairness:** No stereotypes, insults, or discriminatory language.
- **Safety:** No unsupported medical, financial, or performance claims ("guaranteed", "cures", "risk-free").

For reel scripts, this screening also validates structure and the specific content rules above.

Screening happens:
1. When the content is generated
2. When the user edits it (live, debounced)
3. When the draft is submitted to the Review Queue (server-side gate)

A failed check blocks submission until the user fixes the flagged wording.

---

## 👤 Human-in-the-Loop

AI is a **draft tool**, not a publisher. Every step is:
1. **Generate:** AI drafts content.
2. **Screen:** Rules flag obvious mistakes.
3. **Edit:** User reviews and refines.
4. **Submit:** User sends to Review Queue.
5. **Approve:** User marks it ready for use or rejects it.

The workflow ensures that AI output never goes public without a person reading it.

---

## 🏗️ Technology Stack

### Frontend
- **React 18** (Vite)
- **CSS3** (no frameworks, design tokens)
- Responsive UI for desktop and mobile

### Backend
- **FastAPI** (Python)
- **SQLite** (products, reviews, highlights)
- **Ollama** (local Qwen3 1.7B inference)

### Database
- **SQLite** (`shopmate.db`)
  - `products`: name, category, cost, price, rating, status, supplier, highlights, image_path
  - `reviews`: productName, contentType, tone, content, status, payload (for reel scripts)

### AI & NLP
- **Ollama** (local inference engine)
- **Qwen3 1.7B** (LLM, lightweight for CPU-only machines)
- **Rule-based validation** (no external APIs)

---

## 📁 Project Structure

```text
shopmate.ai/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── content_agent.py       # Main AI workflow
│   │   │   └── reel_script.py         # Reel validation & rendering
│   │   ├── routes/
│   │   │   ├── ai.py                  # /api/ai/* endpoints
│   │   │   ├── products.py            # /api/products/* endpoints
│   │   │   └── reviews.py             # /api/reviews/* endpoints
│   │   ├── config.py                  # Config from .env
│   │   ├── database.py                # SQLite setup
│   │   ├── responsible_ai.py          # Screening rules
│   │   └── main.py                    # FastAPI app
│   ├── tests/
│   │   ├── test_reel_script.py        # Reel validation tests
│   │   └── test_api.py                # API tests
│   ├── media/                         # Product images (generated)
│   ├── .env.example                   # Config template
│   ├── pytest.ini                     # Test config
│   ├── requirements.txt               # Python deps
│   ├── requirements-dev.txt           # Dev deps (pytest)
│   └── venv/                          # Virtual environment (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── AIContentStudio.jsx        # Main content editor
│   │   ├── App.jsx                    # Router & layout
│   │   ├── ReelEditor.jsx             # Scene-by-scene reel editor
│   │   ├── ReelEditor.css             # Reel editor styles
│   │   ├── config.js                  # API config
│   │   ├── App.css                    # Global styles
│   │   └── ...other components
│   ├── .env.example                   # API URL override (optional)
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── .gitignore
├── README.md
└── ...
```

---

## 🔌 API Endpoints

### Health
```
GET /api/health
```
Confirms the backend is running.

### Products
```
GET /api/products
GET /api/products/{id}
POST /api/products
POST /api/products/{id}/image
DELETE /api/products/{id}/image
```
- `GET /api/products` returns all products (seeds demo data on first call).
- `POST /api/products` creates a new product.
- `POST /api/products/{id}/image` uploads a product image (JPEG, PNG, WebP, ≤5MB).
- `DELETE /api/products/{id}/image` removes a product's image.

### Reviews
```
GET /api/reviews
POST /api/reviews
PATCH /api/reviews/{id}
```
- `GET /api/reviews` lists all drafts (most recent first).
- `POST /api/reviews` validates and stores a draft (returns 422 if flagged).
- `PATCH /api/reviews/{id}` updates the status (Pending, Approved, Rejected).

For reel scripts, the POST body includes:
```json
{
  "productName": "LED Desk Lamp",
  "contentType": "Reel Script",
  "tone": "Friendly",
  "payload": { "scenes": [...], "caption": "...", "hashtags": [...] },
  "price": 899
}
```

### AI Endpoints
```
POST /api/ai/generate
POST /api/ai/check
POST /api/ai/check-reel
POST /api/ai/test
```
- `POST /api/ai/generate` runs the content agent (text or reel).
  - Request: `{ product_name, category, price, content_type, tone, highlights }`
  - Response: `{ response, structured (for reels), estimated_seconds, model, agent, workflow, attempts, revision_performed, responsible_ai }`
  
- `POST /api/ai/check` screens plain text (used when editing).
  - Request: `{ content }`
  - Response: `{ passed, issues, matches, estimated_seconds (for reels) }`

- `POST /api/ai/check-reel` validates a structured reel script.
  - Request: `{ product_name, price, payload }`
  - Response: `{ passed, issues, matches, estimated_seconds, text }`

- `POST /api/ai/test` tests direct communication with Ollama.

---

## ⚙️ Running the Project

### Prerequisites
- **Python 3.13+**
- **Node.js 18+** (for npm)
- **Ollama** with Qwen3 1.7B model installed
  ```powershell
  ollama pull qwen3:1.7b
  ```

### 1. Start Ollama

```powershell
ollama run qwen3:1.7b
```

Leave this window open. Ollama listens on `http://localhost:11434`.

### 2. Start the FastAPI Backend

First time only, create and set up the virtual environment:

```powershell
cd backend
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

Start the server (no activation needed):

```powershell
venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 5000
```

Backend runs at `http://localhost:5000`.

To run tests:
```powershell
venv\Scripts\python.exe -m pip install -r requirements-dev.txt
venv\Scripts\python.exe -m pytest
```

### 3. Start the Frontend

Open another terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend runs at `http://localhost:5173`.

Optional: If the backend is not at `http://localhost:5000`, copy `.env.example` to `.env` and set `VITE_API_URL`.

---

## 🧪 Example Workflow

1. **Open the app** at `http://localhost:5173`.
2. **Go to AI Content**.
3. **Select "LED Desk Lamp"**, set Content Type to **Reel Script**, Tone to **Friendly**.
4. **Click Generate Content**.
   - Ollama runs on your CPU (expect 5–10 minutes on a Pentium).
   - The reel script appears as 4 editable scenes.
5. **Check the Responsible AI** box below the script.
   - If ✓ "No obvious issues", proceed to step 6.
   - If ⚠️ "Review required", the check lists what failed. Edit the scenes to fix it.
6. **Click Send to Review** to save the draft to the Review Queue.
7. **Go to Review Queue**.
   - The draft appears as a "Pending" item.
   - Click **Approve** or **Reject**.

---

## 📊 Current Features

✅ Product browsing and dashboard  
✅ Trend Insights (sample data)  
✅ AI text content generation (captions, descriptions)  
✅ **Structured reel script generation** (Step 2)  
✅ **Reel validation & rule-based screening** (Step 2)  
✅ **Scene-by-scene reel editor** (Step 2)  
✅ **Product database with image upload** (Step 2.5)  
✅ Human review workflow  
✅ Responsible AI screening at multiple stages  
✅ Backend tests (26 passing)  

---

## 🎬 Planned: Video Rendering & Instagram Publishing

Next steps (not yet implemented):

### Step 3: Video Renderer
- Read a reel script (structured JSON).
- Use product image + voiceover text to render a 720×1280 or 1080×1920 video.
- **Tools:** FFmpeg, text-to-speech (Piper or edge-tts), MoviePy.
- Output: MP4 file ready for preview or upload.

### Step 4: Instagram Publishing Agent
- Once a video is approved, an agent posts it via the **Instagram Graph API**.
- Requires: Meta developer account, Business/Creator Instagram account, app approval.
- Stores the posted video's IG link and status in the database.

These steps are designed to extend the human-in-the-loop model: the video is still reviewed before posting.

---

## ⚠️ AI Limitations

This project uses a **small, lightweight model (Qwen3 1.7B)** for local inference on CPU-only machines. This means:

- **Hallucination:** The model may invent product features, customer reviews, or specifications not mentioned in highlights.
- **Errors:** Grammar, capitalization, and tone inconsistencies are common.
- **Brevity:** Long, detailed content is difficult.
- **Specificity:** The model struggles with very niche products or unusual requests.

**Mitigation:** The validation rules and Responsible AI screening catch some mistakes (invented testimonials, unsupported claims, privacy risks). However, **human review is always required**. Do not rely on the AI alone.

---

## 🔐 Privacy & Security

- **Data:** All inference happens locally via Ollama. No data is sent to external APIs or cloud services.
- **Credentials:** API keys and tokens (when added for Instagram) are stored in `.env` only, never committed to git.
- **Images:** Product images are stored in `backend/media/`, which is gitignored.

---

## 🧑‍💼 Workflow Best Practices

1. **Product Highlights:** Keep highlights accurate and concise. AI can only work with the facts you provide.
2. **Tone:** Choose a tone that matches your brand.
3. **Content Type:** Captions are quick; reels take longer but generate a complete social media script.
4. **Review Every Draft:** Even if the check passes, read the output before using it.
5. **Edit Fearlessly:** If the AI missed something, edit and re-check before sending to the queue.
6. **Approve Thoughtfully:** Only approve drafts you'd actually post.

---

## 🎓 Academic Project

This project was built for a semester coursework on AI and software engineering. It demonstrates:

- Local AI inference (no cloud APIs).
- Rule-based validation and screening.
- Human-in-the-loop design.
- A real full-stack web app (React + FastAPI + SQLite).
- Structured AI outputs (JSON reel scripts) that can be consumed by downstream tools.

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 🚀 Next Developer Tasks

If continuing this project:

1. **Implement video rendering** (Step 3):
   - Text-to-speech for voiceovers.
   - Image composition with captions and effects.
   - FFmpeg command orchestration.
   - Output: MP4 preview.

2. **Implement Instagram publishing** (Step 4):
   - OAuth flow for Instagram Business Account.
   - Reel upload via Graph API.
   - Status tracking in database.

3. **Improve the AI model:**
   - Try Qwen3 7B or another slightly larger model if hardware allows.
   - Fine-tune the prompt for better product fact recognition.
   - Expand the validation rules based on real-world failures.

4. **Polish the UI:**
   - Add a proper product management page (create, edit, delete, upload images).
   - Add a video preview player.
   - Add bulk content generation.

5. **Tests:** Expand test coverage for the frontend.

---

**Questions?** See the README for setup details, or check the code comments in `backend/app/agent/reel_script.py` and `backend/app/agent/content_agent.py` for the AI logic.
