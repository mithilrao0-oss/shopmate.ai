from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import initialize_database
from app.routes.reviews import router as review_router
from app.routes.products import router as products_router
from app.routes.ai import router as ai_router


app = FastAPI(
    title="ShopMate.ai API",
    description="Backend API for the ShopMate.ai AIOT project",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


initialize_database()


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "ShopMate.ai FastAPI backend is running"
    }


app.include_router(review_router)
app.include_router(products_router)
app.include_router(ai_router)