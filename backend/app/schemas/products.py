from pydantic import BaseModel
from typing import Optional, List

# Base and Create schemas for Category
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Base and Create schemas for Product
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int = 0
    is_active: bool = True
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    category: CategoryResponse

    class Config:
        from_attributes = True

# Schema for updating an existing category
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Schema for updating an existing product
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None