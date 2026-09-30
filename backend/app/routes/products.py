from fastapi import APIRouter


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


# ---------- Sample Product Data ----------
# Single source of truth for the demo products. The frontend loads these
# through GET /api/products and no longer keeps its own copy.

products = [
    {
        "id": 1,
        "name": "Portable Blender",
        "category": "Kitchen",
        "cost": 650,
        "price": 1299,
        "rating": 4.5,
        "status": "Shortlisted",
        "supplier": "Demo Supplier",
        "trendScore": 82
    },
    {
        "id": 2,
        "name": "LED Desk Lamp",
        "category": "Home & Office",
        "cost": 420,
        "price": 899,
        "rating": 4.3,
        "status": "Under Review",
        "supplier": "Demo Supplier",
        "trendScore": 58
    },
    {
        "id": 3,
        "name": "Travel Organizer",
        "category": "Travel",
        "cost": 280,
        "price": 599,
        "rating": 4.6,
        "status": "Shortlisted",
        "supplier": "Demo Supplier",
        "trendScore": 69
    },
    {
        "id": 4,
        "name": "Mini Bluetooth Speaker",
        "category": "Electronics",
        "cost": 800,
        "price": 1499,
        "rating": 4.2,
        "status": "Pending",
        "supplier": "Demo Supplier",
        "trendScore": 45
    }
]


# ---------- Get Products ----------

@router.get("")
def get_products():
    return products
