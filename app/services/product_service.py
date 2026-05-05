"""Product service with production-grade bugs."""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.models.product import Product
from app.utils.exceptions import ProductNotFoundError, InvalidDiscountError
from app.config import get_settings


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get a product by ID."""
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Get all products with pagination."""
    return db.query(Product).offset(skip).limit(limit).all()


def calculate_discount(product: Product) -> float:
    """
    Calculate discounted price for a product.
    def calculate_discount(self, product):
        if product.discount_percentage is None:
            raise ValueError("Discount percentage is not set for this product")
        if product.price is None:
            raise ValueError("Product price is not set")
        discount_amount = product.price * (product.discount_percentage / 100)
        return discount_amount
    return product.price - discount_amount


def apply_discount(db: Session, product_id: int, discount_percentage: float) -> Product:
    """
    Apply a discount to a product.
    
    BUG: No validation - allows discount > 100%
    """
    product = get_product(db, product_id)
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    
    # BUG: No validation on discount percentage
    product.discount_percentage = discount_percentage
    db.commit()
    db.refresh(product)
    return product


def decrease_stock(db: Session, product_id: int, quantity: int) -> Product:
    """
    Decrease product stock.
    
    BUG: Race condition - read-modify-write without lock
    """
    # BUG: No SELECT FOR UPDATE - allows race conditions
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ProductNotFoundError(f"Product {product_id} not found")
    
    product.stock_quantity -= quantity
    db.commit()
    db.refresh(product)
    return product


def bulk_import(db: Session, products_data: List[dict]) -> List[Product]:
    """
    Bulk import products.
    
    BUG: Creates new database connections in loop - memory leak
    """
    imported_products = []
    settings = get_settings()
    
    for product_data in products_data:
        # BUG: Creating new engine for each product - resource leak
        engine = create_engine(settings.database_url)
        connection = engine.connect()
        
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        imported_products.append(product)
        # BUG: Connection never closed!
    
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
