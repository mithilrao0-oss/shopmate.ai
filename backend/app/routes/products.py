import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import DATABASE_PATH
from app.database import get_db_connection


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)

# Where product images are stored (relative to backend folder).
MEDIA_DIR = Path(__file__).resolve().parent.parent.parent / "media"
MEDIA_DIR.mkdir(exist_ok=True)

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


class ProductCreate(BaseModel):
    name: str
    category: str = ""
    cost: float | None = None
    price: float | None = None
    rating: float | None = None
    status: str = "Pending"
    supplier: str = ""
    highlights: list[str] = []


class ProductUpdate(BaseModel):
    name: str = ""
    category: str = ""
    cost: float | None = None
    price: float | None = None
    rating: float | None = None
    status: str = ""
    supplier: str = ""
    highlights: list[str] = []


def _row_to_dict(row):
    item = dict(row)

    raw_highlights = item.get("highlights")

    if raw_highlights:
        try:
            item["highlights"] = json.loads(raw_highlights)
        except (ValueError, TypeError):
            item["highlights"] = []
    else:
        item["highlights"] = []

    return item


def _seed_demo_products():
    """
    Populate the database with demo products if the table is empty.
    This happens the first time the app starts.
    """

    connection = get_db_connection()

    existing = connection.execute("SELECT COUNT(*) as count FROM products").fetchone()

    if existing["count"] > 0:
        connection.close()
        return

    demo = [
        {
            "name": "Portable Blender",
            "category": "Kitchen",
            "cost": 650,
            "price": 1299,
            "rating": 4.5,
            "status": "Shortlisted",
            "supplier": "Demo Supplier",
            "highlights": ["Portable size", "Blends drinks"],
        },
        {
            "name": "LED Desk Lamp",
            "category": "Home & Office",
            "cost": 420,
            "price": 899,
            "rating": 4.3,
            "status": "Under Review",
            "supplier": "Demo Supplier",
            "highlights": ["LED light", "Made for desks"],
        },
        {
            "name": "Travel Organizer",
            "category": "Travel",
            "cost": 280,
            "price": 599,
            "rating": 4.6,
            "status": "Shortlisted",
            "supplier": "Demo Supplier",
            "highlights": ["Keeps travel items organised"],
        },
        {
            "name": "Mini Bluetooth Speaker",
            "category": "Electronics",
            "cost": 800,
            "price": 1499,
            "rating": 4.2,
            "status": "Pending",
            "supplier": "Demo Supplier",
            "highlights": ["Bluetooth connection", "Mini size"],
        },
    ]

    for product in demo:
        connection.execute(
            """
            INSERT INTO products
            (name, category, cost, price, rating, status, supplier, highlights)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product["name"],
                product["category"],
                product["cost"],
                product["price"],
                product["rating"],
                product["status"],
                product["supplier"],
                json.dumps(product["highlights"], ensure_ascii=False),
            ),
        )

    connection.commit()
    connection.close()


# --- Get Products ---

@router.get("")
def get_products():
    """
    Get all products.
    """

    _seed_demo_products()

    connection = get_db_connection()

    rows = connection.execute(
        "SELECT id, name, category, cost, price, rating, status, supplier, highlights, image_path FROM products ORDER BY id"
    ).fetchall()

    connection.close()

    return [_row_to_dict(row) for row in rows]


@router.get("/{product_id}")
def get_product(product_id: int):
    """Get a single product by ID."""

    connection = get_db_connection()

    row = connection.execute(
        "SELECT id, name, category, cost, price, rating, status, supplier, highlights, image_path FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()

    connection.close()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    return _row_to_dict(row)


# --- Create Product ---

@router.post("")
def create_product(product: ProductCreate):
    """Create a new product."""

    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO products
        (name, category, cost, price, rating, status, supplier, highlights)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product.name,
            product.category,
            product.cost,
            product.price,
            product.rating,
            product.status,
            product.supplier,
            json.dumps(product.highlights, ensure_ascii=False),
        ),
    )

    connection.commit()

    product_id = cursor.lastrowid

    row = connection.execute(
        "SELECT id, name, category, cost, price, rating, status, supplier, highlights, image_path FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()

    connection.close()

    return _row_to_dict(row)


# --- Upload Product Image ---

@router.post("/{product_id}/image")
async def upload_product_image(product_id: int, file: UploadFile = File(...)):
    """
    Upload an image for a product.
    """

    connection = get_db_connection()

    product = connection.execute(
        "SELECT id FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()

    if not product:
        connection.close()
        raise HTTPException(status_code=404, detail="Product not found")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file size.
    contents = await file.read()

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Max size is {MAX_IMAGE_SIZE // 1024 // 1024} MB.",
        )

    # Check file type.
    allowed_types = {"image/jpeg", "image/png", "image/webp"}

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_types)}",
        )

    # Save the file with a unique name.
    file_ext = Path(file.filename).suffix.lower()
    unique_name = f"product_{product_id}_{uuid.uuid4().hex}{file_ext}"
    file_path = MEDIA_DIR / unique_name

    with open(file_path, "wb") as f:
        f.write(contents)

    # Update the product's image path in the database.
    relative_path = f"media/{unique_name}"

    connection.execute(
        "UPDATE products SET image_path = ? WHERE id = ?",
        (relative_path, product_id),
    )

    connection.commit()
    connection.close()

    return {
        "product_id": product_id,
        "image_path": relative_path,
        "message": "Image uploaded successfully",
    }


# --- Delete Product Image ---

@router.delete("/{product_id}/image")
def delete_product_image(product_id: int):
    """Remove the image for a product."""

    connection = get_db_connection()

    product = connection.execute(
        "SELECT image_path FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()

    if not product:
        connection.close()
        raise HTTPException(status_code=404, detail="Product not found")

    image_path = product["image_path"]

    if image_path:
        file_path = Path(image_path)

        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                connection.close()
                raise HTTPException(
                    status_code=500,
                    detail=f"Could not delete image: {e}",
                )

    connection.execute(
        "UPDATE products SET image_path = NULL WHERE id = ?",
        (product_id,),
    )

    connection.commit()
    connection.close()

    return {"message": "Image deleted successfully"}
