"""Order service with intentional bugs."""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.product import Product
from app.services.product_service import get_product, decrease_stock
from app.utils.exceptions import (
    UserNotFoundError, 
    ProductNotFoundError, 
    InvalidQuantityError,
    PaymentFailedError
)
from app.config import is_bug_enabled


def create_order(db: Session, user_id: int, product_id: int, quantity: int) -> Order:
    """
    Create a new order.
    
    BUG-003: Missing User Validation in Order Creation
    BUG-013: Negative Quantity Allowed
    """
    # BUG-003: Missing user validation
    if is_bug_enabled("003"):
        # BUGGY: Access user.email without checking if user exists
        user = db.query(User).filter(User.id == user_id).first()
        email = user.email  # Will crash if user is None
    else:
        # CORRECT: Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
    
    # Get product
    product = get_product(db, product_id)
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    
    # BUG-013: Negative quantity allowed
    if is_bug_enabled("013"):
        # BUGGY: No validation on quantity
        pass
    else:
        # CORRECT: Validate quantity
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")
    
    # Calculate order details
    unit_price = product.price
    discount_amount = 0.0
    if product.discount_percentage:
        discount_amount = unit_price * quantity * (product.discount_percentage / 100)
    
    # Calculate total
    total_amount = calculate_total(unit_price, quantity, discount_amount)
    
    # Create order
    order = Order(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        discount_amount=discount_amount,
        total_amount=total_amount,
        status=OrderStatus.PENDING
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


def calculate_total(unit_price: float, quantity: int, discount_amount: float) -> float:
    """
    Calculate order total.
    
    BUG-015: Order Total Miscalculation
    When enabled, calculates tax on discounted price instead of original.
    """
    TAX_RATE = 0.10  # 10% tax
    
    if is_bug_enabled("015"):
        # BUGGY: Calculate tax on discounted price
        subtotal = (unit_price * quantity) - discount_amount
        tax = subtotal * TAX_RATE
        total = subtotal + tax
        return total
    else:
        # CORRECT: Calculate tax on original price, then apply discount
        subtotal = unit_price * quantity
        tax = subtotal * TAX_RATE
        total = subtotal + tax - discount_amount
        return total


def process_payment(db: Session, order_id: int, payment_method: str) -> Order:
    """
    Process payment for an order.
    
    BUG-007: Missing Transaction Rollback
    When enabled, doesn't rollback on payment failure.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ProductNotFoundError(f"Order {order_id} not found")
    
    if is_bug_enabled("007"):
        # BUGGY: No transaction rollback on failure
        order.status = OrderStatus.PROCESSING
        db.commit()
        
        # Simulate payment processing
        if payment_method == "invalid":
            # Payment fails but order status already changed!
            raise PaymentFailedError("Payment processing failed")
        
        order.payment_status = "completed"
        order.status = OrderStatus.COMPLETED
        db.commit()
        db.refresh(order)
        return order
    else:
        # CORRECT: Use try-except with rollback
        try:
            order.status = OrderStatus.PROCESSING
            db.commit()
            
            # Simulate payment processing
            if payment_method == "invalid":
                raise PaymentFailedError("Payment processing failed")
            
            order.payment_status = "completed"
            order.status = OrderStatus.COMPLETED
            
            # Decrease product stock
            decrease_stock(db, order.product_id, order.quantity)
            
            db.commit()
            db.refresh(order)
            return order
        except Exception as e:
            db.rollback()
            order.status = OrderStatus.FAILED
            db.commit()
            raise


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get an order by ID."""
    return db.query(Order).filter(Order.id == order_id).first()


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    """Get all orders for a user."""
    return db.query(Order).filter(Order.user_id == user_id).all()

# Made with Bob
