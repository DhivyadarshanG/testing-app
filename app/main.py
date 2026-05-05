"""Bug Zoo - Main FastAPI application with production-grade bugs."""

from fastapi import FastAPI
from app.database import init_db
from app.routers import auth, users, products, orders
from app.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Bug Zoo - Buggy E-Commerce API",
    description="A deliberately buggy e-commerce API for testing self-healing agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("🦗 Bug Zoo started!")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print("⚠️  WARNING: This application contains intentional bugs for testing purposes")


@app.get("/", tags=["health"])
def root():
    """Root endpoint."""
    return {
        "message": "Bug Zoo - E-Commerce API",
        "description": "A deliberately buggy application for testing self-healing agents",
        "docs": "/docs",
        "warning": "Contains production-grade bugs for testing"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
