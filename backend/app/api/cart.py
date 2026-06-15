from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.cart import CartItem
from app.models.products import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemResponse, CartItemUpdate, CartSummary
from app.api.deps import get_current_active_user

# Initialize the router for cart items
router = APIRouter(
    prefix="/api/cart",
    tags=["Cart"]
)

@router.post("/", response_model=CartItemResponse)
def add_to_cart(
    item_in: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if the product exists
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # Check if the item is already in the user's cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item_in.product_id
    ).first()
    
    if existing_item:
        # If it exists, just update the quantity
        existing_item.quantity += item_in.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
        
    # If not, create a new cart item
    new_item = CartItem(
        user_id=current_user.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/", response_model=CartSummary)
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Retrieve all cart items for the current user
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    # Calculate the total price dynamically
    # Sum of (quantity * product price) for each item in the cart
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    
    return {
        "items": cart_items,
        "total_price": total_price
    }

@router.patch("/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    item_in: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Find the cart item ensuring it belongs to the current user
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
        
    # Update the quantity
    cart_item.quantity = item_in.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/{cart_item_id}")
def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Find the cart item ensuring it belongs to the current user
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
        
    # Delete the cart item
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.delete("/")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Delete all cart items belonging strictly to the currently logged-in user
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    
    db.commit()
    return {"message": "Cart cleared successfully"}