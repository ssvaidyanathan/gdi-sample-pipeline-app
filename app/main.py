import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .config import get_config


def format_order_currency(value: float) -> str:
    formatted_val = round(value, 2)
    return f"${formatted_val:.2f}"




logger = logging.getLogger("sample-pipeline-app")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class OrderItem(BaseModel):
    item_id: str = Field(..., description="Unique product ID")
    name: str = Field(..., description="Item name")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    unit_price: float = Field(..., ge=0.0, description="Price per unit in USD")


class OrderCreate(BaseModel):
    customer_id: str = Field(..., description="Customer identifier")
    customer_email: str = Field(..., description="Customer contact email")
    items: list[OrderItem] = Field(..., min_length=1, description="List of ordered items")


class Order(BaseModel):
    order_id: str
    customer_id: str
    customer_email: str
    items: list[OrderItem]
    total_amount: float
    status: str = "confirmed"


# In-memory store for confirmed customer orders
ORDERS_DB: dict[str, Order] = {
    "ord-initial-001": Order(
        order_id="ord-initial-001",
        customer_id="cust-100",
        customer_email="alice@example.com",
        items=[
            OrderItem(
                item_id="item-sku-42",
                name="Cloud Native Handbook",
                quantity=2,
                unit_price=29.99,
            )
        ],
        total_amount=59.98,
        status="confirmed",
    )
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup, cache prewarming, and lifecycle."""
    cfg = get_config()
    logger.info("Initializing sample-pipeline-app (env=%s, port=%d)", cfg.environment, cfg.port)

    # Prewarm order history cache if configured
    if cfg.cache_prewarm_buffer_mb > 0:
        logger.info("Pre-warming in-memory cache buffer (%d MB)...", cfg.cache_prewarm_buffer_mb)
        _ = bytearray(cfg.cache_prewarm_buffer_mb * 1024 * 1024)

    yield
    logger.info("Shutting down sample-pipeline-app...")


app = FastAPI(
    title="Order Processing Service",
    description="High-throughput asynchronous customer order processing service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def get_root() -> dict[str, Any]:
    """Root metadata endpoint."""
    cfg = get_config()
    return {
        "service": cfg.app_name,
        "version": cfg.app_version,
        "environment": cfg.environment,
        "status": "online",
    }


@app.get("/health")
def get_health() -> dict[str, str]:
    """Readiness and liveness probe endpoint."""
    cfg = get_config()
    return {
        "status": "healthy",
        "service": cfg.app_name,
        "version": cfg.app_version,
    }


@app.get("/api/v1/orders", response_model=list[Order])
def list_orders() -> list[Order]:
    """List all confirmed orders."""
    return list(ORDERS_DB.values())


@app.post("/api/v1/orders", response_model=Order, status_code=201)
def create_order(payload: OrderCreate) -> Order:
    """Create and confirm a new customer order."""
    total = sum(item.quantity * item.unit_price for item in payload.items)
    order_id = f"ord-{uuid4().hex[:8]}"
    order = Order(
        order_id=order_id,
        customer_id=payload.customer_id,
        customer_email=payload.customer_email,
        items=payload.items,
        total_amount=round(total, 2),
        status="confirmed",
    )
    ORDERS_DB[order_id] = order
    logger.info(
        "Created order %s for customer %s (total: $%.2f)",
        order_id,
        payload.customer_id,
        total,
    )
    return order


@app.get("/api/v1/orders/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    """Retrieve an existing order by ID."""
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return ORDERS_DB[order_id]
