# ShopMate.ai — one-shot project scaffold (PowerShell version)
# Usage: run this FROM INSIDE your existing shopmate-ai folder (the one already on GitHub)
# .\scaffold.ps1
# Safe to re-run: it will NOT overwrite your existing README.md or any file that already exists.

# Root files (README.md skipped on purpose — you already have one)
New-Item -ItemType File -Path ".gitignore", ".env.example" -ErrorAction SilentlyContinue | Out-Null

# Frontend (React)
New-Item -ItemType Directory -Force -Path "frontend/public", "frontend/src/components", "frontend/src/pages", "frontend/src/redux", "frontend/src/services" | Out-Null
New-Item -ItemType File -Path "frontend/src/App.jsx", "frontend/src/index.js", "frontend/package.json", "frontend/.env.example" -ErrorAction SilentlyContinue | Out-Null

# Backend (Node/Express)
New-Item -ItemType Directory -Force -Path "backend/src/models", "backend/src/routes", "backend/src/controllers", "backend/src/middleware", "backend/src/config" | Out-Null
New-Item -ItemType File -Path "backend/src/server.js", "backend/package.json", "backend/.env.example" -ErrorAction SilentlyContinue | Out-Null

# Agents (Python)
New-Item -ItemType Directory -Force -Path "agents/product_sourcing_agent", "agents/trend_agent", "agents/shared" | Out-Null
New-Item -ItemType File -Path "agents/product_sourcing_agent/ingest.py", "agents/product_sourcing_agent/filter_agent.py", "agents/product_sourcing_agent/dedupe.py", "agents/product_sourcing_agent/requirements.txt" -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "agents/trend_agent/trends_fetch.py", "agents/trend_agent/engagement_score.py", "agents/trend_agent/rank_products.py", "agents/trend_agent/requirements.txt" -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "agents/shared/llm_client.py", "agents/shared/db_writer.py" -ErrorAction SilentlyContinue | Out-Null

# Java microservice (inventory/orders)
New-Item -ItemType Directory -Force -Path "services/inventory-service-java/src/main/java/com/shopmate/inventory/controller" | Out-Null
New-Item -ItemType Directory -Force -Path "services/inventory-service-java/src/main/java/com/shopmate/inventory/model" | Out-Null
New-Item -ItemType Directory -Force -Path "services/inventory-service-java/src/main/java/com/shopmate/inventory/repository" | Out-Null
New-Item -ItemType Directory -Force -Path "services/inventory-service-java/src/main/java/com/shopmate/inventory/service" | Out-Null
New-Item -ItemType Directory -Force -Path "services/inventory-service-java/src/main/resources" | Out-Null
New-Item -ItemType File -Path "services/inventory-service-java/src/main/resources/application.properties" -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "services/inventory-service-java/pom.xml" -ErrorAction SilentlyContinue | Out-Null

# C++ tool (image processing)
New-Item -ItemType Directory -Force -Path "tools/image-processor-cpp/src", "tools/image-processor-cpp/include", "tools/image-processor-cpp/build" | Out-Null
New-Item -ItemType File -Path "tools/image-processor-cpp/src/main.cpp", "tools/image-processor-cpp/CMakeLists.txt" -ErrorAction SilentlyContinue | Out-Null

# Content pipeline (AI reels + IG publishing)
New-Item -ItemType Directory -Force -Path "content-pipeline/assets/stock_footage", "content-pipeline/assets/fonts", "content-pipeline/assets/output", "content-pipeline/review_queue" | Out-Null
New-Item -ItemType File -Path "content-pipeline/script_generator.py", "content-pipeline/voiceover.py", "content-pipeline/video_assembler.py", "content-pipeline/instagram_publisher.py", "content-pipeline/requirements.txt" -ErrorAction SilentlyContinue | Out-Null

# Docs
New-Item -ItemType Directory -Force -Path "docs/module-writeups" | Out-Null
New-Item -ItemType File -Path "docs/module-writeups/01-storefront.md", "docs/module-writeups/02-sourcing-agent.md", "docs/module-writeups/03-trend-agent.md", "docs/module-writeups/04-content-pipeline.md", "docs/module-writeups/05-instagram-publishing.md", "docs/module-writeups/06-inventory-service.md" -ErrorAction SilentlyContinue | Out-Null
New-Item -ItemType File -Path "docs/architecture-diagram.png", "docs/er-diagram.png", "docs/api-reference.md", "docs/limitations-and-future-work.md" -ErrorAction SilentlyContinue | Out-Null

# Scripts
New-Item -ItemType Directory -Force -Path "scripts" | Out-Null
New-Item -ItemType File -Path "scripts/seed_db.py", "scripts/run_all.sh" -ErrorAction SilentlyContinue | Out-Null

# Tests
New-Item -ItemType Directory -Force -Path "tests/backend", "tests/agents", "tests/content-pipeline" | Out-Null

Write-Host "ShopMate.ai project structure created successfully." -ForegroundColor Green
