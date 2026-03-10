from fastapi import FastAPI, HTTPException, Query, Path
from service.products import (
    get_all_products,
    add_product,
    remove_product,
    change_product
)
from schema.product import Product, ProductUpdate
from uuid import uuid4, UUID
from datetime import datetime

app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Product API running 🚀"}


# ---------------- GET ALL PRODUCTS ----------------
@app.get("/products")
def list_products(
    name: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search by product name (case insensitive)"
    ),
    sort_by_price: bool = Query(
        default=False,
        description="Sort products by price"
    ),
    order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order when sort_by_price=true"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of products to return"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination offset"
    )
):

    products = get_all_products()

    # ---------- search ----------
    if name:
        needle = name.strip().lower()
        products = [
            p for p in products
            if needle in p.get("name", "").lower()
        ]

    # ---------- sort ----------
    if sort_by_price:
        reverse = order == "desc"
        products = sorted(
            products,
            key=lambda p: p.get("price", 0),
            reverse=reverse
        )

    total = len(products)

    # ---------- pagination ----------
    paginated_products = products[offset: offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": paginated_products
    }


# ---------------- GET PRODUCT BY ID ----------------
@app.get("/products/{product_id}")
def get_product_by_id(
    product_id: UUID = Path(
        ...,
        description="UUID of the product"
    )
):

    products = get_all_products()

    for product in products:
        if product["id"] == str(product_id):
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# ---------------- CREATE PRODUCT ----------------
@app.post("/products", status_code=201)
def create_product(product: Product):

    product_dict = product.model_dump(mode="json")

    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        add_product(product_dict)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return product_dict


# ---------------- DELETE PRODUCT ----------------
@app.delete("/products/{product_id}")
def delete_product(
    product_id: UUID = Path(..., description="Product UUID")
):

    try:
        result = remove_product(str(product_id))
        return {"message": "Product deleted successfully", "data": result}

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ---------------- UPDATE PRODUCT ----------------
@app.put("/products/{product_id}")
def update_product(
    product_id: UUID = Path(..., description="Product UUID"),
    payload: ProductUpdate = ...
):

    try:
        updated_product = change_product(
            str(product_id),
            payload.model_dump(
                mode="json",
                exclude_unset=True
            )
        )

        return updated_product

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )