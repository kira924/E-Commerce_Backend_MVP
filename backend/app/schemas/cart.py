from typing import List
from pydantic import BaseModel
from app.schemas.products import ProductResponse

# Base schema for cart items
class CartItemBase(BaseModel):
    product_id: int
    quantity: int

# Schema for adding an item to the cart
class CartItemCreate(CartItemBase):
    pass

# Schema for updating the quantity of a cart item
class CartItemUpdate(BaseModel):
    quantity: int

# Schema for returning the cart item with product details
class CartItemResponse(BaseModel):
    id: int
    user_id: int
    quantity: int
    product: ProductResponse

    class Config:
        from_attributes = True

# Schema for returning the entire cart with the total calculated price
class CartSummary(BaseModel):
    items: List[CartItemResponse]
    total_price: float