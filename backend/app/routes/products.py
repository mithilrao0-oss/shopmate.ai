from fastapi import APIRouter


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


# ---------- Sample Product Data ----------
# Single source of truth for the demo products. The frontend loads these
# through GET /api/products and no longer keeps its own copy.
#
# "highlights" are the only product facts the AI is allowed to talk about.
# The demo highlights below come straight from the product names. A real
# seller should replace them with verified facts.

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
        "trendScore": 82,
        "highlights": ["Portable size", "Blends drinks"]
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
        "trendScore": 58,
        "highlights": ["LED light", "Made for desks"]
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
        "trendScore": 69,
        "highlights": ["Keeps travel items organised"]
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
        "trendScore": 45,
        "highlights": ["Bluetooth connection", "Mini size"]
    }
]


# ---------- Get Products ----------

@router.get("")
def get_products():
    return products
