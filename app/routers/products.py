"""Product management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.database import get_db
from app.services import product_service
from app.models.user import User
from app.routers.auth import get_current_user
from app.utils.exceptions import ProductNotFoundError, InvalidDiscountError

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    """Product creation schema."""
    name: str
    description: str
    price: float
    stock_quantity: int


class ProductResponse(BaseModel):
    """Product response schema."""
    id: int
    name: str
    description: str | None
    price: float
    discount_percentage: float | None
    stock_quantity: int
    discounted_price: float | None = None
    
    class Config:
        from_attributes = True


class DiscountUpdate(BaseModel):
    """Discount update schema."""
    discount_percentage: float


class BulkImportRequest(BaseModel):
    """Bulk import request schema."""
    products: List[ProductCreate]


@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all products."""
    products = product_service.get_products(db, skip=skip, limit=limit)
    
    # Calculate discounted prices (triggers BUG-002 if enabled)
    result = []
    for product in products:
        product_dict = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "discount_percentage": product.discount_percentage,
            "stock_quantity": product.stock_quantity,
            "discounted_price": product_service.calculate_discount(product)
        }
        result.append(product_dict)
    
    return result


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    Triggers BUG-002 if enabled (unhandled None in discount calculation).
    """
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "discount_percentage": product.discount_percentage,
        "stock_quantity": product.stock_quantity,
        "discounted_price": product_service.calculate_discount(product)
    }


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product (requires authentication)."""
    product = product_service.create_product(
        db=db,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity
    )
    return product


@router.put("/{product_id}/discount", response_model=ProductResponse)
def update_discount(
    product_id: int,
    discount_data: DiscountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update product discount.
    Triggers BUG-014 if enabled (discount exceeds price).
    """
    try:
        product = product_service.apply_discount(
            db=db,
            product_id=product_id,
            discount_percentage=discount_data.discount_percentage
        )
        return product
    except (ProductNotFoundError, InvalidDiscountError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import", response_model=List[ProductResponse])
def bulk_import_products(
    import_data: BulkImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bulk import products.
    Triggers BUG-011 if enabled (unclosed database connections).
    """
    products_data = [p.dict() for p in import_data.products]
    products = product_service.bulk_import(db, products_data)
    return products

# Made with Bob
