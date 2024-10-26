from fastapi import FastAPI, HTTPException, Response, status
from typing import List, Optional, Dict
from pydantic import BaseModel
import uuid


app = FastAPI(title="Shop API")


class ItemBase(BaseModel):
    name: str
    price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None


class ItemResponse(ItemBase):
    id: int
    deleted: bool = False

    class Config:
        orm_mode = True


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool = True


class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float

    class Config:
        orm_mode = True


class CartCreate(BaseModel):
    pass


items_db: Dict[int, ItemResponse] = {}
carts_db: Dict[int, Cart] = {}

# Счетчики для генерации ID
item_counter = 1
cart_counter = 1


@app.post("/item", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    global item_counter, items_db
    item_id = item_counter
    new_item = ItemResponse(id=item_id, name=item.name, price=item.price, deleted=False)
    items_db[item_id] = new_item
    item_counter += 1
    return new_item


@app.get("/item/{id}", response_model=ItemResponse)
async def get_item(id: int):
    item = items_db.get(id)
    if item is None or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")
    return item


@app.get("/item", response_model=List[ItemResponse])
async def get_items(
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False,
):
    if offset < 0 or limit < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params"
        )

    if (min_price is not None and min_price < 0) or (
        max_price is not None and max_price < 0
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params"
        )

    items = list(items_db.values())

    if min_price is not None:
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price <= max_price]

    if not show_deleted:
        items = [item for item in items if not item.deleted]

    return items[offset : offset + limit]


@app.patch("/item/{id}", response_model=ItemResponse)
async def update_item(id: int, item_update: ItemUpdate):
    item = items_db.get(id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.deleted:
        raise HTTPException(status_code=422, detail="Item already deleted")

    update_data = item_update.dict(exclude_unset=True)

    if "name" in update_data:
        item.name = update_data["name"]
    if "price" in update_data:
        item.price = update_data["price"]

    return item


@app.put("/item/{id}", response_model=ItemResponse)
async def replace_item(id: int, item_update: ItemUpdate):
    existing_item = items_db.get(id)
    if existing_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item_update.price is None or item_update.name is None:
        raise HTTPException(status_code=422, detail="Both name and price are required")

    updated_item = existing_item.model_copy(
        update=item_update.model_dump(exclude_unset=True)
    )
    items_db[id] = updated_item
    return updated_item


@app.delete("/item/{id}", status_code=status.HTTP_200_OK)
async def delete_item(id: int):
    item = items_db.get(id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.deleted:
        return {"message": "Item already deleted"}

    item.deleted = True
    return {"message": "Item successfully deleted"}


@app.post("/cart", response_model=Dict[str, int], status_code=status.HTTP_201_CREATED)
async def create_cart():
    global cart_counter, carts_db

    cart_id = cart_counter
    carts_db[cart_id] = Cart(id=cart_id, items=[], price=0.0)
    cart_counter += 1

    return {"id": cart_id}


@app.get("/cart/{id}", response_model=Cart)
async def get_cart(id: int):
    cart = carts_db.get(id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@app.get("/cart", response_model=List[Cart])
async def get_carts(
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None,
):
    if offset < 0 or limit < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params"
        )

    if (
        (min_price is not None and min_price < 0)
        or (max_price is not None and max_price < 0)
        or (min_quantity is not None and min_quantity < 0)
        or (max_quantity is not None and max_quantity < 0)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Bad query params"
        )

    carts = list(carts_db.values())[offset : offset + limit]

    if min_price is not None:
        carts = [cart for cart in carts if cart.price >= min_price]
    if max_price is not None:
        carts = [cart for cart in carts if cart.price <= max_price]

    if min_quantity is not None:
        carts = [
            cart
            for cart in carts
            if sum(item.quantity for item in cart.items) >= min_quantity
        ]
    if max_quantity is not None:
        carts = [
            cart
            for cart in carts
            if sum(item.quantity for item in cart.items) <= max_quantity
        ]

    return carts


@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_db.get(cart_id)
    item = items_db.get(item_id)

    if not cart or not item or item.deleted:
        raise HTTPException(
            status_code=404, detail="Cart or item not found or item is deleted"
        )

    existing_item = None
    for i in cart.items:
        if i.id == item_id:
            existing_item = i
            break

    if existing_item:
        existing_item.quantity += 1
    else:
        cart.items.append(
            CartItem(id=item.id, name=item.name, quantity=1, available=not item.deleted)
        )

    cart.price += item.price
    return cart
