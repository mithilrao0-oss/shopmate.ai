from fastapi import APIRouter


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


# ---------- Sample Product Data ----------

products = [
    {
        "id": 1,
        "name": "LED Desk Lamp",
        "category": "Home & Office",
        "price": 499,
        "supplier": "Demo Supplier",
        "trendScore": 87
    },
    {
        "id": 2,
        "name": "Travel Organizer",
        "category": "Travel",
        "price": 599,
        "supplier": "Demo Supplier",
        "trendScore": 82
    },
    {
        "id": 3,
        "name": "Portable Mini Fan",
        "category": "Electronics",
        "price": 399,
        "supplier": "Demo Supplier",
        "trendScore": 78
    }
]


# ---------- Get Products ----------

@router.get("")
def get_products():
    return products