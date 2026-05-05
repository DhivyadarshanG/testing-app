"""Custom exceptions for Bug Zoo application."""

from fastapi import HTTPException, status


class BugZooException(Exception):
    """Base exception for Bug Zoo application."""
    pass


class TokenNotFoundError(BugZooException):
    """Raised when user token is not found or invalid."""
    pass


class UserNotFoundError(BugZooException):
    """Raised when user is not found."""
    pass


class ProductNotFoundError(BugZooException):
    """Raised when product is not found."""
    pass


class InsufficientStockError(BugZooException):
    """Raised when product stock is insufficient."""
    pass


class InvalidQuantityError(BugZooException):
    """Raised when order quantity is invalid."""
    pass


class InvalidDiscountError(BugZooException):
    """Raised when discount is invalid."""
    pass


class PaymentFailedError(BugZooException):
    """Raised when payment processing fails."""
    pass


class UnauthorizedError(BugZooException):
    """Raised when user is not authorized."""
    pass


# HTTP Exception helpers
def raise_not_found(detail: str):
    """Raise 404 Not Found exception."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def raise_unauthorized(detail: str = "Not authenticated"):
    """Raise 401 Unauthorized exception."""
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def raise_forbidden(detail: str = "Not enough permissions"):
    """Raise 403 Forbidden exception."""
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def raise_bad_request(detail: str):
    """Raise 400 Bad Request exception."""
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

# Made with Bob
