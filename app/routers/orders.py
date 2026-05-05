"""Order management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.services import order_service
from app.models.user import User
from app.models.order import OrderStatus
from app.routers.auth import get_current_user
from app.utils.exceptions import (
    UserNotFoundError,
    ProductNotFoundError,
    InvalidQuantityError,
    PaymentFailedError
)

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderCreate(BaseModel):
    """Order creation schema."""
    product_id: int
    quantity: int


class OrderResponse(BaseModel):
    """Order response schema."""
    id: int
    user_id: int
    product_id: int
    quantity: int
    unit_price: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    status: OrderStatus
    payment_status: str
    
    class Config:
        from_attributes = True


class PaymentRequest(BaseModel):
    """Payment processing request."""
    payment_method: str


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new order.
    Triggers BUG-003 if enabled (missing user validation).
    Triggers BUG-013 if enabled (negative quantity allowed).
    """
    try:
        order = order_service.create_order(
            db=db,
            user_id=current_user.id,
            product_id=order_data.product_id,
            quantity=order_data.quantity
        )
        return order
    except (UserNotFoundError, ProductNotFoundError, InvalidQuantityError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all orders for the current user."""
    orders = order_service.get_user_orders(db, current_user.id)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific order by ID."""
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    # Check if order belongs to current user
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.post("/{order_id}/checkout", response_model=OrderResponse)
def checkout_order(
    order_id: int,
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process payment for an order.
    Triggers BUG-007 if enabled (missing transaction rollback).
    Triggers BUG-015 if enabled (order total miscalculation).
    """
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found"
        )
    
    # Check if order belongs to current user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to checkout this order"
        )
    
    try:
        order = order_service.process_payment(
            db=db,
            order_id=order_id,
            payment_method=payment_data.payment_method
        )
        return order
    except PaymentFailedError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e)
        )

# Made with Bob
