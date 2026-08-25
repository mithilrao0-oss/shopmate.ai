# ShopMate.ai — AI-Powered Product Discovery & Auto-Content Dropshipping Platform

## Overview
A dropshipping platform (Meesho-style) that uses AI agents to:
1. Source and filter winning products from suppliers
2. Detect early trend signals (not "predict virality" — no one can do that reliably)
3. Auto-generate short-form video reels for products
4. Publish reels to Instagram (with human approval gate in v1)

## Reality Check (Read This First)
- **Fully autonomous end-to-end automation is NOT realistic for v1.** Treat this as an AI-assisted platform with a human-in-the-loop approval step, not a "set and forget" system.
- **"Predict virality" is misleading.** Reframe as "trend surfacing" — detecting products with early upward signal (search volume, competitor ad activity, engagement velocity), not predicting the future.
- **Dropshipping is mostly an operations problem**, not an AI problem. Returns, COD logistics (India), supplier reliability, and delivery SLAs will make or break this more than the AI layer.
- **Instagram Graph API has strict automation limits** and requires a Business/Creator account + Meta app review. Full auto-posting without review/rate-limit awareness will get flagged.
- **Scraping supplier sites (AliExpress, Amazon, etc.) risks ToS violations / IP bans.** Prefer official APIs (CJdropshipping, AliExpress affiliate API, etc.) wherever possible.
- **AI-generated faceless product reels are a saturated content genre.** The real differentiator is speed-to-trend + creative quality + conversion feedback loop — not the fact that AI made it.

## Recommended v1 Scope (Cut Ruthlessly)
**Build:**
- Product ingestion from a small number of official supplier APIs
- Agent-based filtering (margin, shipping time, review score, duplicate detection)
- Trend-surfacing agent using proxy signals (Google Trends, IG/TikTok engagement growth, ad library activity)
- AI reel generation pipeline (script → voiceover → video assembly → caption)
- Human approval step before any post goes live
- Manual/semi-automated IG posting via Graph API (respecting rate limits)

**Don't build yet:**
- Your own checkout/payment/warehouse stack — link out to an existing store backend (Shopify) or Meesho itself first
- Fully autonomous posting with zero human review
- Claims of "virality prediction" anywhere in marketing copy

## System Modules

### 1. Product Sourcing Agent
- Pulls product data via supplier APIs
- Filters on: margin %, shipping time, supplier rating, return rate, banned-category check
- Deduplicates near-identical listings

### 2. Trend Surfacing Agent
- Monitors Google Trends, IG/TikTok hashtag & engagement velocity, competitor ad spend (via ad libraries)
- Scores products by early-signal momentum, not "will it go viral"
- Outputs a ranked shortlist for human review

### 3. Content Generation Pipeline
- Script generation (LLM)
- Voiceover (e.g., ElevenLabs)
- Video assembly (e.g., Remotion / templated editor) using product images/clips + trending audio
- Caption + hashtag generation

### 4. Publishing Layer
- Human approval queue (review before posting)
- Instagram Graph API integration for scheduled posting
- Rate-limit-aware queue to avoid spam flags

### 5. Feedback Loop
- Track post performance (views, engagement, click-through, conversion)
- Feed results back into the Trend Surfacing Agent to improve future product selection
- This feedback loop — not the initial AI filtering — is the platform's real long-term moat

## Tech Stack (Suggested, Not Final)
- **Backend**: Node.js or Python (FastAPI)
- **Agents/LLM orchestration**: Claude/GPT API, LangChain or custom agent loop
- **Video generation**: Remotion, ElevenLabs, FFmpeg
- **Storefront**: Shopify (v1) → custom later if justified by scale
- **Data**: Postgres for catalog/orders, Redis for queues
- **Publishing**: Meta Graph API (Instagram Business)

## Legal/Compliance Checklist
- [ ] Use official supplier APIs, not scraping, where available
- [ ] Register Meta Business app, complete app review for Graph API posting
- [ ] Respect IG posting rate limits and automation policy
- [ ] Disclose AI-generated content where required by platform policy
- [ ] Verify product categories against Meta ad/commerce policy (no banned/restricted goods)

## Project Title
**ShopMate.ai – AI Agent-Assisted Product Discovery & Auto-Content Platform**
(Sem 5 college project — "trend detection," not "virality prediction," is the honest and defensible framing for the report/viva.)

## Build Roadmap (Phased, ~10-12 Weeks)

### Phase 0 — Setup (Week 1)
- Install VS Code, Node.js, Python, Git
- Create GitHub repo (this README as the starting doc), set up `.gitignore`, branch strategy (`main` + `dev`)
- Folder structure: `/frontend`, `/backend`, `/agents`, `/content-pipeline`, `/docs`

### Phase 1 — Core E-commerce Storefront (Weeks 2-4)
Build the Meesho-style storefront first — this is the foundation everything else plugs into.
- Tutorial: [MERN Stack E-Commerce Full Course (React, Node, Redux)](https://www.youtube.com/watch?v=hpgh2BTtac8)
- Alternative with full source code: [MERN-Stack ECommerce Website](https://www.youtube.com/watch?v=Fy9SdZLBTOo) — source: github.com/basir/node-react-ecommerce
- Deliverable: product listing, cart, checkout (dummy payment is fine for a college project), admin panel

### Phase 2 — Product Sourcing + Filtering Agent (Weeks 5-6)
The core "AI agent" — keep it simple and explainable for viva.
- Fundamentals first: [Building an AI Agent from Scratch in Python (Anthropic API)](https://www.leoniemonigatti.com/blog/ai-agent-from-scratch-in-python.html)
- Reference implementation: [GitHub: Ecommerce-Product-Recommendation-ChatGPT](https://github.com/ahmadluay9/Ecommerce-Product-Recommendation-ChatGPT)
- Build: an agent that takes a product list (CSV/API) and scores/filters by margin, rating, shipping time using LLM + rule-based logic — feed output into the storefront DB

### Phase 3 — Trend Surfacing Agent (Week 7)
Framed as "trend detection," not prediction.
- Use `pytrends` (Google Trends API wrapper) for search-interest signal
- Combine with a simple engagement-velocity score from any accessible public dataset/API
- Output: ranked shortlist feeding into Phase 4

### Phase 4 — AI Reel Generation Pipeline (Weeks 8-9)
The demo "wow factor" — adapt existing open-source pipelines rather than building from zero.
- Best structured reference: [SaarD00/AI-Youtube-Shorts-Generator](https://github.com/SaarD00/AI-Youtube-Shorts-Generator) — script → TTS (edge-tts, free) → stock footage → FFmpeg assembly
- Alternative with built-in script approval step: [Dark2C/Viral-Faceless-Shorts-Generator](https://github.com/Dark2C/Viral-Faceless-Shorts-Generator) — Dockerized
- Adapt the script-generation step to describe the *product* (from Phase 2/3 output) instead of a random trending topic

### Phase 5 — Instagram Publishing (Week 10)
Register the Meta Business app early (review can take days) even though this is built last.
- Tutorial: [Instagram Graph API Posting Content with Python](https://www.youtube.com/watch?v=j65W-L-gQs4)
- Reference with code: [Uploading a Reel via Instagram Graph API (Medium)](https://medium.com/@ritikkhndelwal/uploading-an-instagram-reel-using-python-and-instagram-graph-api-8364c4842367)
- Keep the human-approval step before posting — defensible design choice for the report

### Phase 6 — Integration, Docs, Demo (Weeks 11-12)
- Wire all modules behind one dashboard
- Write the project report using this README as the backbone (Abstract → Modules → Tech Stack → Limitations/Future Work)
- Record a demo video as backup in case live IG posting fails during viva (API/app-review issues are common)

## GitHub + VS Code Workflow (for the report's "Methodology" section)
- Feature-branch per module (`feature/product-agent`, `feature/reel-pipeline`, etc.), PR into `dev`, merge to `main` at milestones
- Use GitHub Projects (Kanban board) to show iterative development
- Commit README/docs updates alongside code, not all at the end

## Open Questions to Resolve Before Building
- Which supplier APIs are actually available for your target market (India-focused CJdropshipping, IndiaMART, etc.)?
- Payment/COD handling — own system or route through existing platform?
- What's the human-review bottleneck budget (how many products/reels per day can realistically be reviewed)?
- What defines "success" for a posted reel — views, click-through, or actual conversion? (Pick one primary metric early.)
