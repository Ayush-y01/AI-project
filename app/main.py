from fastapi import FastAPI, HTTPException, Query, Path 
from service.products import get_all_products, add_product ,remove_product, change_product
from fastapi.responses import JSONResponse
from schema.product import Product, ProductUpdate
from uuid import uuid4,UUID
from datetime import datetime

app = FastAPI()

@app.get("/")
async def read_root():
    return {"hello": "world"}

# @app.get('/products')
# def get_product():
#     return get_all_products() 

@app.get("/products")
def list_products(
    name: str = Query(default=None, min_length=1, max_length=50, description="Search by product name (case insensitive)"),
    sort_by_price: bool = Query(default=False, description="sort products by price"),
    order:str = Query(default="asc", description="sort order when sort_by_price=true (asc,desc)"),
    limit:int =Query(
        default=3,
        ge=1,
        le=100,
        description="Number of items to return"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination Offset"
    )
    ):

    products = get_all_products()

    if name:
        needle = name.strip().lower()
        products = [p for p in products if needle in p.get("name","").lower()]

    if not products:
        raise HTTPException(status_code=404, detail=f"Product not Found!!!! name={name}")
        
    if sort_by_price:
        reverse = order == 'desc'
        products = sorted(products, key=lambda p:p.get("price",0),reverse=reverse)

        
    total = len(products)
    products = products[offset: offset + limit]


    return {
        "total":total,
        "limit":limit,
        "items": products
    }



@app.get("/products/{product_id}")
def get_product_by_id(product_id: str = Path(...,min_length=36, max_length=36, description="UUID of the products", example="0005a4ea-ce3f-4dd7-bee0-f4ccc70fea6a")):
    products = get_all_products()

    for product in products:
        if product["id"] == product_id:
            return product


    raise HTTPException(status_code=404, detail="product not found")




@app.post("/products", status_code=201)
def create_product(product: Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "z"
    
    try:
        add_product(product_dict)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
    return product.model_dump(mode="json")



@app.delete("/products/{product_id}")
def delete_product(product_id:UUID = Path(..., description="Product id ")):
    try:
        res = remove_product(str(product_id))
        return res
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@app.put("/products/{product_id}")
def update_product(product_id:UUID = Path(..., description="Product uuid "),
payload: ProductUpdate = ...,):
    try:
        update_product = change_product(str(product_id), payload.model_dump(mode="json", exclude_unset=True))
        return update_product
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 