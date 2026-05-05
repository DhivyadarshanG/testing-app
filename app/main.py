"""Bug Zoo - Main FastAPI application."""

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from app.database import init_db
from app.routers import auth, users, products, orders, bugs
from app.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Bug Zoo",
    description="A deliberately buggy FastAPI application for testing self-healing agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("🦗 Bug Zoo started successfully!")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🐛 Bug Control: http://localhost:8000/bugs/catalog")


@app.get("/", tags=["health"])
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Bug Zoo 🦗",
        "description": "A deliberately buggy application for testing self-healing agents",
        "docs": "/docs",
        "bug_catalog": "/bugs/catalog"
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
app.include_router(bugs.router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error messages."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
            "hint": "Check if a bug is enabled at /bugs/catalog"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
