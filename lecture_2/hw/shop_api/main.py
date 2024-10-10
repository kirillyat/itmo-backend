

from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uuid

app = FastAPI(title="Shop API")

# Модели данных

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float


# In-memory "базы данных"
items_db = {}
carts_db = {}

# Item CRUD
@app.post("/item")
async def add_item(item: Item):
    if item.id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    items_db[item.id] = item
    return item

@app.get("/item/{id}")
async def get_item(id: int):
    item = items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")
    return item

@app.get("/item")
async def get_items(offset: int = 0, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None, show_deleted: bool = False):
    results = []
    for item in items_db.values():
        if item.deleted and not show_deleted:
            continue
        if min_price is not None and item.price < min_price:
            continue
        if max_price is not None and item.price > max_price:
            continue
        results.append(item)
    return results[offset : offset + limit]

@app.put("/item/{id}")
async def replace_item(id: int, item: Item):
    if id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[id] = item
    return item

@app.patch("/item/{id}")
async def update_item(id: int, item: Item):
    current_item = items_db.get(id)
    if not current_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.name:
        current_item.name = item.name
    if item.price:
        current_item.price = item.price
    items_db[id] = current_item
    return current_item

@app.delete("/item/{id}")
async def delete_item(id: int):
    item = items_db.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.deleted = True
    return {"status": "deleted"}

# Cart CRUD
@app.post("/cart")
async def create_cart():
    cart_id = str(uuid.uuid4())
    new_cart = Cart(id=cart_id, items=[], price=0.0)
    carts_db[cart_id] = new_cart
    return {"cart_id": cart_id}

@app.get("/cart/{id}")
async def get_cart(id: str):
    cart = carts_db.get(id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@app.get("/cart")
async def get_carts(offset: int = 0, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None,
                    min_quantity: Optional[int] = None, max_quantity: Optional[int] = None):
    results = []
    for cart in carts_db.values():
        if min_price is not None and cart.price < min_price:
            continue
        if max_price is not None and cart.price > max_price:
            continue
        total_items = sum([item.quantity for item in cart.items])
        if min_quantity is not None and total_items < min_quantity:
            continue
        if max_quantity is not None and total_items > max_quantity:
            continue
        results.append(cart)
    return results[offset : offset + limit]

@app.post("/cart/{cart_id}/add/{item_id}")
async def add_item_to_cart(cart_id: str, item_id: int):
    cart = carts_db.get(cart_id)
    item = items_db.get(item_id)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    # Если товар уже в корзине, увеличиваем его количество
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            return cart

    # Если товара нет в корзине, добавляем его
    new_cart_item = CartItem(id=item.id, name=item.name, quantity=1, available=not item.deleted)
    cart.items.append(new_cart_item)
    cart.price += item.price
    return cart