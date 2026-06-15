from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.products import ProductResponse
from app.schemas.address import AddressResponse

# Schema for incoming data when creating an order
class OrderCreate(BaseModel):
    address_id: int

# Schema for returning an individual item within an order
class OrderItemResponse(BaseModel):
    id: int
    product_id: Optional[int]
    product: Optional[ProductResponse]
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

# Schema for returning the complete order details
class OrderResponse(BaseModel):
    id: int
    user_id: int
    address_id: Optional[int]
    address: Optional[AddressResponse]
    status: str
    total_price: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

# Schema for updating the order status (Admin only)
class OrderStatusUpdate(BaseModel):
    status: str

# Schema for requesting a payment link
class PaymentRequest(BaseModel):
    payment_method: str = "card" # Can be "card" or "wallet"