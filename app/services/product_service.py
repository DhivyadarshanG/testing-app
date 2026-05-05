"""Product service with intentional bugs."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.product import Product
from app.utils.exceptions import ProductNotFoundError, InvalidDiscountError
from app.config import is_bug_enabled


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get a product by ID."""
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Get all products with pagination."""
    return db.query(Product).offset(skip).limit(limit).all()


def calculate_discount(product: Product) -> float:
    """
    Calculate discounted price for a product.
    
    BUG-002: Unhandled None in Product Price Calculation
    When enabled, performs math operation on None discount value.
    """
    if is_bug_enabled("002"):
        # BUGGY: No null check on discount_percentage
        discount_amount = product.price * (product.discount_percentage / 100)
        return product.price - discount_amount
    else:
        # CORRECT: Handle None discount
        if product.discount_percentage is None or product.discount_percentage == 0:
            return product.price
        discount_amount = product.price * (product.discount_percentage / 100)
        return product.price - discount_amount


def apply_discount(db: Session, product_id: int, discount_percentage: float) -> Product:
    """
    Apply a discount to a product.
    
    BUG-014: Discount Exceeds Price
    When enabled, allows discount percentage > 100.
    """
    product = get_product(db, product_id)
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    
    # BUG-014: No validation on discount percentage
    if is_bug_enabled("014"):
        # BUGGY: Allow any discount percentage
        product.discount_percentage = discount_percentage
        db.commit()
        db.refresh(product)
        return product
    else:
        # CORRECT: Validate discount percentage
        if discount_percentage < 0 or discount_percentage > 100:
            raise InvalidDiscountError("Discount must be between 0 and 100")
        
        product.discount_percentage = discount_percentage
        db.commit()
        db.refresh(product)
        return product


def decrease_stock(db: Session, product_id: int, quantity: int) -> Product:
    """
    Decrease product stock.
    
    BUG-008: Race Condition in Stock Update
    When enabled, uses read-modify-write without lock.
    """
    if is_bug_enabled("008"):
        # BUGGY: Read-modify-write without lock (race condition)
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        product.stock_quantity -= quantity
        db.commit()
        db.refresh(product)
        return product
    else:
        # CORRECT: Use SELECT FOR UPDATE to lock the row
        product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        
        product.stock_quantity -= quantity
        db.commit()
        db.refresh(product)
        return product


def bulk_import(db: Session, products_data: List[dict]) -> List[Product]:
    """
    Bulk import products.
    
    BUG-011: Unclosed Database Connection
    When enabled, creates connections in loop without closing.
    """
    imported_products = []
    
    if is_bug_enabled("011"):
        # BUGGY: Creates new connection for each product without closing
        from sqlalchemy import create_engine
        from app.config import get_settings
        settings = get_settings()
        
        for product_data in products_data:
            # Creating new engine/connection each time - memory leak!
            engine = create_engine(settings.database_url)
            connection = engine.connect()
            
            product = Product(**product_data)
            db.add(product)
            db.commit()
            db.refresh(product)
            imported_products.append(product)
            # Connection never closed!
        
        return imported_products
    else:
        # CORRECT: Use existing session, no extra connections
        for product_data in products_data:
            product = Product(**product_data)
            db.add(product)
        
        db.commit()
        
        # Refresh all products
        for product in imported_products:
            db.refresh(product)
        
        return imported_products


def create_product(db: Session, name: str, description: str, price: float, stock_quantity: int) -> Product:
    """Create a new product."""
    product = Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# Made with Bob
