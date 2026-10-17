import os

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Configuration for the sample pipeline application."""

    app_name: str = Field(default="sample-pipeline-app", description="Name of the service")
    app_version: str = Field(default="1.0.0", description="Application semantic version")
    environment: str = Field(
        default_factory=lambda: os.getenv("APP_ENV", "development"),
        description="Deployment environment (development, staging, production)",
    )
    port: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8080")),
        description="Listening HTTP port",
    )
    cache_prewarm_buffer_mb: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_PREWARM_BUFFER_MB", "0")),
        description="Size in MB of in-memory cache pre-allocation during startup",
    )
    strict_schema_validation: bool = Field(
        default_factory=lambda: os.getenv("STRICT_SCHEMA_VALIDATION", "false").lower() == "true",
        description="Enable strict startup schema verification",
    )


def get_config() -> AppConfig:
    """Retrieve application configuration instance."""
    return AppConfig()
