"""Application configuration and settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Bug Zoo"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://bugzoo:bugzoo123@localhost:5432/bugzoo"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Bug Control Flags - Each bug can be enabled/disabled
    bug_001_enabled: bool = False  # Missing Null Check on User Token
    bug_002_enabled: bool = False  # Unhandled None in Product Price
    bug_003_enabled: bool = False  # Missing User Validation in Order
    bug_004_enabled: bool = False  # Token Expiry Not Checked
    bug_005_enabled: bool = False  # Missing Permission Check on Delete
    bug_006_enabled: bool = False  # Password Hash Not Verified
    bug_007_enabled: bool = False  # Missing Transaction Rollback
    bug_008_enabled: bool = False  # Race Condition in Stock Update
    bug_009_enabled: bool = False  # Concurrent Session Creation
    bug_010_enabled: bool = False  # Cache Invalidation Race
    bug_011_enabled: bool = False  # Unclosed Database Connection
    bug_012_enabled: bool = False  # Redis Connection Pool Exhaustion
    bug_013_enabled: bool = False  # Negative Quantity Allowed
    bug_014_enabled: bool = False  # Discount Exceeds Price
    bug_015_enabled: bool = False  # Order Total Miscalculation
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def is_bug_enabled(bug_id: str) -> bool:
    """Check if a specific bug is enabled."""
    settings = get_settings()
    bug_attr = f"bug_{bug_id.lower()}_enabled"
    return getattr(settings, bug_attr, False)

# Made with Bob
