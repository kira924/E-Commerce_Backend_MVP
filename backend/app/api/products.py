from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.products import Product, Category
from app.schemas.products import ProductCreate, ProductResponse, CategoryCreate, CategoryResponse, CategoryUpdate, ProductUpdate
from app.api.deps import get_current_admin_user
from app.models.user import User

# Initialize the router for products and categories
router = APIRouter(
    prefix="/api",
    tags=["Products & Categories"]
)

@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Check if category name already exists
    db_category = db.query(Category).filter(Category.name == category.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = Category(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    # Retrieve all categories
    return db.query(Category).all()

@router.post("/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Verify that the linked category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    new_product = Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    # Retrieve all products
    return db.query(Product).all()

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    # Query the database for the specific product by ID
    product = db.query(Product).filter(Product.id == product_id).first()
    
    # If the product does not exist, raise a 404 error
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Find the category
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # If the admin is updating the name, ensure it does not conflict with an existing category
    if category_in.name is not None and category_in.name != category.name:
        existing_category = db.query(Category).filter(Category.name == category_in.name).first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category name already exists")

    # Extract only the fields provided in the request
    update_data = category_in.model_dump(exclude_unset=True)
    
    # Update the category model
    for field, value in update_data.items():
        setattr(category, field, value)
        
    db.commit()
    db.refresh(category)
    return category

@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Find the product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # If the admin is updating the category_id, verify the new category exists
    if product_in.category_id is not None:
        category = db.query(Category).filter(Category.id == product_in.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    # Extract only the fields provided in the request
    update_data = product_in.model_dump(exclude_unset=True)
    
    # Update the product model
    for field, value in update_data.items():
        setattr(product, field, value)
        
    db.commit()
    db.refresh(product)
    return product

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Find the category
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    # Check if there are any products linked to this category
    linked_products = db.query(Product).filter(Product.category_id == category_id).first()
    if linked_products:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete category because it contains products. Please delete or reassign the products first."
        )
        
    # Delete the category
    db.delete(category)
    db.commit()
    
    return {"message": "Category deleted successfully"}

@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Find the product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Delete the product
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}