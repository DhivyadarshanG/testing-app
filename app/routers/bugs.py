"""Bug control endpoints for testing."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict
from app.config import get_settings, Settings

router = APIRouter(prefix="/bugs", tags=["bug-control"])


class BugStatus(BaseModel):
    """Bug status response."""
    bug_id: str
    enabled: bool
    description: str


class BugToggleRequest(BaseModel):
    """Bug toggle request."""
    enabled: bool


class BugCatalog(BaseModel):
    """Complete bug catalog."""
    bugs: Dict[str, BugStatus]


# Bug descriptions
BUG_DESCRIPTIONS = {
    "001": "Missing Null Check on User Token - Accessing user_id without checking if token is None",
    "002": "Unhandled None in Product Price Calculation - Math operation on None discount value",
    "003": "Missing User Validation in Order Creation - Accessing user.email when user is None",
    "004": "Token Expiry Not Checked - Returns user even if token expired",
    "005": "Missing Permission Check on Delete - Any user can delete any user",
    "006": "Password Hash Not Verified - Compares plain text password directly",
    "007": "Missing Transaction Rollback - Payment fails but order status already changed",
    "008": "Race Condition in Stock Update - Read-modify-write without lock",
    "009": "Concurrent Session Creation - Multiple sessions created for same user",
    "010": "Cache Invalidation Race - Cache updated before DB commit",
    "011": "Unclosed Database Connection - Opens connection in loop without closing",
    "012": "Redis Connection Pool Exhaustion - Creates new Redis client each call",
    "013": "Negative Quantity Allowed - No validation on quantity parameter",
    "014": "Discount Exceeds Price - Discount percentage > 100 allowed",
    "015": "Order Total Miscalculation - Tax calculated on discounted price instead of original"
}


@router.get("/catalog", response_model=BugCatalog)
def get_bug_catalog():
    """Get complete bug catalog with current status."""
    settings = get_settings()
    bugs = {}
    
    for bug_id, description in BUG_DESCRIPTIONS.items():
        bug_attr = f"bug_{bug_id}_enabled"
        enabled = getattr(settings, bug_attr, False)
        bugs[bug_id] = BugStatus(
            bug_id=bug_id,
            enabled=enabled,
            description=description
        )
    
    return BugCatalog(bugs=bugs)


@router.get("/{bug_id}", response_model=BugStatus)
def get_bug_status(bug_id: str):
    """Get status of a specific bug."""
    if bug_id not in BUG_DESCRIPTIONS:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bug {bug_id} not found"
        )
    
    settings = get_settings()
    bug_attr = f"bug_{bug_id}_enabled"
    enabled = getattr(settings, bug_attr, False)
    
    return BugStatus(
        bug_id=bug_id,
        enabled=enabled,
        description=BUG_DESCRIPTIONS[bug_id]
    )


@router.post("/{bug_id}/toggle", response_model=BugStatus)
def toggle_bug(bug_id: str, toggle_data: BugToggleRequest):
    """
    Toggle a specific bug on/off.
    Note: This modifies environment variables at runtime.
    For persistent changes, update the .env file.
    """
    if bug_id not in BUG_DESCRIPTIONS:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bug {bug_id} not found"
        )
    
    import os
    env_var = f"BUG_{bug_id}_ENABLED"
    os.environ[env_var] = str(toggle_data.enabled).lower()
    
    # Clear settings cache to reload
    get_settings.cache_clear()
    
    settings = get_settings()
    bug_attr = f"bug_{bug_id}_enabled"
    enabled = getattr(settings, bug_attr, False)
    
    return BugStatus(
        bug_id=bug_id,
        enabled=enabled,
        description=BUG_DESCRIPTIONS[bug_id]
    )


@router.post("/enable-all")
def enable_all_bugs():
    """Enable all bugs for testing."""
    import os
    for bug_id in BUG_DESCRIPTIONS.keys():
        env_var = f"BUG_{bug_id}_ENABLED"
        os.environ[env_var] = "true"
    
    get_settings.cache_clear()
    return {"message": "All bugs enabled", "count": len(BUG_DESCRIPTIONS)}


@router.post("/disable-all")
def disable_all_bugs():
    """Disable all bugs."""
    import os
    for bug_id in BUG_DESCRIPTIONS.keys():
        env_var = f"BUG_{bug_id}_ENABLED"
        os.environ[env_var] = "false"
    
    get_settings.cache_clear()
    return {"message": "All bugs disabled", "count": len(BUG_DESCRIPTIONS)}

# Made with Bob
