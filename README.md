# ShopMate.ai

## Smart AI Product Sourcing & Content Workspace

ShopMate.ai is an AI-powered workspace for e-commerce sellers to discover products, analyze trends, and generate marketing content (captions, descriptions, and Instagram reel scripts) with human review at every stage.

The project showcases:
- A **human-in-the-loop workflow**: AI drafts content, and a person reviews it before use.
- **Responsible AI screening** at multiple stages (generation, editing, submission).
- **Structured reel scripts** (JSON) that are validated before reaching a person.
- **Local AI inference** using Ollama and the small Qwen3 1.7B model: scripts, voice and video are all made on your own machine.
- **A safe publish queue**: only approved reels with a rendered video can be queued, and posting defaults to a harmless dry-run mode.

**Status:** Script generation, human review, video rendering and a publish queue (dry-run) are working and tested. **Current goal: real Instagram Reels publishing.** YouTube Shorts and customer tracking come later.

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

### 6. Video Rendering
An approved reel script plus a product image becomes a vertical MP4 on your own machine: a synthetic voice reads each scene, the image slowly zooms or pans, and captions are burned in. Ollama only writes the script text; it does not generate any video.

### 7. Publish Queue
An approved reel with a saved final video can be queued for Instagram (and later YouTube Shorts), then published. In the default dry-run mode a post is only recorded, so the whole flow can be tested without contacting any platform.

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
  - `reviews`: productName, contentType, tone, content, status, payload (for reel scripts), video_path
  - `posts`: review_id, platform, status, title, caption, video_path, mode, external_id, external_url, error, postedAt

### AI & NLP
- **Ollama** (local inference engine)
- **Qwen3 1.7B** (LLM, lightweight for CPU-only machines)
- **Rule-based validation** (no external APIs)

### Video & Publishing
- **FFmpeg** (scene clips, zoom/pan, burned-in captions), **Pillow** (background image), **pyttsx3** (offline voice)
- **Publisher interface** with a dry-run publisher (Instagram and YouTube publishers are planned)

---

## 📁 Project Structure

```text
shopmate.ai/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── content_agent.py       # Main AI workflow
│   │   │   └── reel_script.py         # Reel validation & rendering
│   │   ├── publishing/
│   │   │   ├── base.py                # Publisher interface
│   │   │   └── dry_run.py             # Dry-run publisher (no platform contact)
│   │   ├── routes/
│   │   │   ├── ai.py                  # /api/ai/* endpoints
│   │   │   ├── posts.py               # /api/posts/* publish queue
│   │   │   ├── products.py            # /api/products/* endpoints
│   │   │   ├── reviews.py             # /api/reviews/* endpoints
│   │   │   └── videos.py              # /api/videos/* endpoints
│   │   ├── video/
│   │   │   ├── renderer.py            # FFmpeg video rendering
│   │   │   └── tts.py                 # Per-scene offline voiceover
│   │   ├── config.py                  # Config from .env
│   │   ├── database.py                # SQLite setup
│   │   ├── responsible_ai.py          # Screening rules
│   │   └── main.py                    # FastAPI app
│   ├── tests/
│   │   ├── test_reel_script.py        # Reel validation tests
│   │   ├── test_api.py                # API tests
│   │   └── test_posts.py              # Publish queue tests
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

### Videos
```
POST /api/videos/render
GET /api/videos/{review_id}
```
See **Video Rendering** below.

### Posts (publish queue)
```
GET /api/posts/mode
POST /api/posts
GET /api/posts
GET /api/posts/{id}
POST /api/posts/{id}/publish
POST /api/posts/{id}/cancel
```
See **Publish Queue** below.

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

Leave this window open. Ollama listens on `http://localhost:11434`. If it says the port is already in use, Ollama is already running in the background, which is fine.

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

Backend runs at `http://localhost:5000`. Interactive API docs are at `http://localhost:5000/docs`.

Optional settings in `backend/.env` (see `.env.example`): `OLLAMA_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`, `SHOPMATE_DB`, `CORS_ORIGINS`, and `PUBLISH_MODE` (`dry-run` by default).

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
   - Ollama runs on your CPU. On an Intel i3-1215U laptop, Qwen3 1.7B generates about 10–12 tokens per second, so a reel script takes well under a minute once the model is loaded. Older machines are slower.
   - The reel script appears as 4 editable scenes.
5. **Check the Responsible AI** box below the script.
   - If ✓ "No obvious issues", proceed to step 6.
   - If ⚠️ "Review required", the check lists what failed. Edit the scenes to fix it.
6. **Click Send to Review** to save the draft to the Review Queue.
7. **Go to Review Queue**.
   - The draft appears as a "Pending" item.
   - Click **Approve** or **Reject**.
8. **Render the video** (API docs page, `http://localhost:5000/docs`):
   - `POST /api/products/{id}/image` to upload a product photo and copy the returned `image_path`.
   - `POST /api/videos/render` with the approved `review_id`, that `image_path` and `"quality": "preview"`, then open the MP4 in `backend/media/`.
   - Render again with `"quality": "final"` to save the video on the review.
9. **Queue and publish** (dry-run):
   - `POST /api/posts` with `{ "review_id": 2, "platforms": ["instagram"] }`.
   - `POST /api/posts/{id}/publish`. The post becomes `Posted` with a fake `dry-run-...` id; nothing is sent anywhere.

---

## 📊 Current Features

✅ Product browsing and dashboard  
✅ Trend Insights (sample data)  
✅ AI text content generation (captions, descriptions)  
✅ **Structured reel script generation** (Step 2)  
✅ **Reel validation & rule-based screening** (Step 2)  
✅ **Scene-by-scene reel editor** (Step 2)  
✅ **Product database with image upload** (Step 2.5)  
✅ **Video rendering** (Step 3): per-scene timing, zoom/pan, synced captions, preview and final quality  
✅ **Publish queue with dry-run mode** (Step 4)  
✅ Human review workflow  
✅ Responsible AI screening at multiple stages  
✅ Backend tests (40 passing)  
🚧 **Instagram Reels publishing** (Step 5, in progress)  
⏳ YouTube Shorts publishing, customer sign-up tracking with Telegram alerts (later)  

---

## 🎬 Video Rendering (Step 3)

### How It Works
1. **Per-scene voiceover:** each scene is spoken separately with pyttsx3 (local, offline), so every scene lasts exactly as long as its own audio, plus a 0.4 s pause (at least 2 s per scene).
2. **Background:** the product image becomes a 9:16 background. A photo that is not already close to 9:16 is shown whole in front of a blurred, dimmed copy of itself, so the product is never cropped.
3. **Camera movement:** each scene gets a slow zoom in, pan, zoom out or pan back (FFmpeg `zoompan`), cycling through the four moves.
4. **Captions:** the on-screen text is a yellow headline at the top for the whole scene. The spoken words appear in short white chunks near the bottom, timed in proportion to their length (an estimate, not exact word timing). Both stay clear of Instagram's buttons.
5. **Assembly:** FFmpeg joins the scene clips and burns the captions in (ASS subtitles). No per-frame image files are written.
6. **Memory:** before rendering, the Ollama model is unloaded to free RAM (useful on 8 GB machines).
7. **Storage:** a final video's path is saved on the review. Previews are not saved.

### Requirements
- **FFmpeg:** `winget install Gyan.FFmpeg` (Windows). Open a new terminal afterwards so the PATH updates.
- **Python libraries:** pyttsx3, pillow (in `requirements.txt`).

### API Endpoints
```
POST /api/videos/render
GET /api/videos/{review_id}
```

Request:
```json
{
  "review_id": 2,
  "product_image_path": "media/product_2_abc123.webp",
  "quality": "preview"
}
```
`quality` is `final` (default) or `preview`.

Response:
```json
{
  "review_id": 2,
  "video_path": "media/reel_2_product_2_abc123_preview.mp4",
  "quality": "preview",
  "duration_seconds": 14.2,
  "warnings": [],
  "message": "Video rendered successfully"
}
```
`GET /api/videos/{review_id}` returns the saved final video path.

### Video Specifications
- **Final:** 1080×1920 at 30 FPS, CRF 23. **Preview:** 720×1280 at 24 FPS, CRF 28.
- **Codec:** H.264 video, AAC audio.
- **Duration:** the sum of the scene voiceovers plus pauses (typically 12 to 20 seconds for a 4-scene reel).
- **Image formats:** `.jpg`, `.jpeg`, `.png`, `.webp` only.
- **Speed (measured on an Intel i3-1215U laptop, no GPU):** an 18 s test reel rendered in about 5 s as a preview and about 10 s as final.

### Limitations
- **Voice:** pyttsx3 uses the system voice, which sounds synthetic. A better offline voice (Piper) is planned.
- **No background music.**
- **Caption timing is an estimate** (spread across each scene by text length).
- **One product image per video.**
- **The render endpoint takes an image path, not a product ID**, and does not check that the review is approved. The publish queue does check approval.
- If an FFmpeg build cannot draw captions, the video is still produced and the response lists a warning.

---

## 📤 Publish Queue (Step 4)

Approved reels with a rendered final video can be queued for Instagram and/or YouTube, then published. Each post is a row in the `posts` table with a status: `Queued` → `Publishing` → `Posted`, or `Failed` / `Cancelled`.

### Safety rules
- Only reels (content type "Reel Script") that are **Approved** and have a **saved final video** can be queued.
- The video must be a file inside `backend/media/`.
- The same reel cannot be queued twice for a platform while a post is Queued, Publishing or Posted.
- Publishing claims the post first, so a double click can never post it twice.
- Just before publishing, the reel is re-checked: if it was rejected after queueing, the post fails instead of going out.
- `PUBLISH_MODE=dry-run` (the default) records a post as published without contacting any platform. Only the exact value `live` turns on real posting, and live mode currently fails with "not set up yet" until the real publishers exist.

### API Endpoints
- `GET /api/posts/mode` returns `dry-run` or `live`.
- `POST /api/posts` queues an approved reel: `{ "review_id": 2, "platforms": ["instagram", "youtube"] }`. Returns one post per platform.
- `GET /api/posts` lists posts, newest first (optional `status` and `review_id` filters).
- `GET /api/posts/{id}` returns one post.
- `POST /api/posts/{id}/publish` publishes a queued post. The result (`Posted` or `Failed`, with an error message) is saved on the post.
- `POST /api/posts/{id}/cancel` cancels a post that has not been published.

YouTube posts get `#Shorts` added to the title and description.

---

## 📷 Instagram Publishing (Step 5, in progress)

**Goal:** publish approved reels to Instagram through the Instagram API, behind the same human approval gate and queue.

**What it needs:**
- An Instagram **professional** (Business or Creator) account.
- A Meta developer app using the use case "Manage messaging & content on Instagram".
- An access token and the Instagram account ID, stored in `backend/.env` (gitignored).

**Status:** the Instagram account and the Meta app are created. Meta's current "API setup with Unified login" requires a business portfolio, so the token step is still being completed. The Instagram publisher is not written yet; dry-run stays the default until it is tested.

**Design:** an `InstagramPublisher` will plug into the existing publisher interface, so the queue, safety rules and tests stay unchanged.

---

## ⚠️ AI Limitations

This project uses a **small, lightweight model (Qwen3 1.7B)** for local inference on CPU-only machines. This means:

- **Hallucination:** The model may invent product features, customer reviews, or specifications not mentioned in highlights.
- **Errors:** Grammar, capitalization, and tone inconsistencies are common.
- **Brevity:** Long, detailed content is difficult.
- **Specificity:** The model struggles with very niche products or unusual requests.

**Mitigation:** The validation rules and Responsible AI screening catch some mistakes (invented testimonials, unsupported claims, privacy risks). However, **human review is always required**. Do not rely on the AI alone.

---

## 🐞 Known Issues

- **The small model invents claims.** Even when a product has real highlights, Qwen3 1.7B sometimes adds features that were never provided (for example "eco-friendly" or "long-lasting" for a desk lamp). The checker flags some of these ("guaranteed", "cures", "long-lasting") but it is word-based and does not catch everything, so a human must read every script.
- **Products page is demo data** in the browser; the product database and image upload are used through the API.
- **Trend Insights uses sample data** and does not predict virality.

---

## 🔐 Privacy & Security

- **Data:** All AI inference, voice and video rendering happen locally. Content is sent to a platform only after a person approves it and queues it, and only when `PUBLISH_MODE=live`.
- **Credentials:** API keys, tokens and OAuth files are stored in `backend/.env` or `backend/secrets/` only. Both are gitignored and must never be committed.
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

**Current goal: Instagram only.**

1. **Finish the Meta setup:** attach a business portfolio to the app, add the Instagram account, and generate the access token and account ID in `backend/.env`.
2. **Write `InstagramPublisher`** (create a REELS media container, wait until it is ready, publish) with tests that mock the HTTP calls, then try it on your own account in `live` mode.
3. **Add Publish buttons and post status to the UI** (queue, publish, status, error message).
4. **Optional scheduler** that publishes queued posts at set times.

**Later:**
- YouTube Shorts publisher (Google OAuth in Testing mode expires every 7 days).
- Customer sign-up and purchase tracking with Telegram alerts and a self-updating customer file.
- A better offline voice (Piper) and optional background music.
- Render endpoint: accept a product ID instead of a file path, and require an approved review.
- Stronger claim checking: flag product features that are not in the product's highlights.
- Frontend tests.

---

**Questions?** See the README for setup details, or check the code comments in `backend/app/agent/reel_script.py` and `backend/app/agent/content_agent.py` for the AI logic.
