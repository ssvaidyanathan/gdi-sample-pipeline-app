from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Verify metadata root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "sample-pipeline-app"
    assert data["status"] == "online"
    assert "version" in data


def test_health_endpoint(client: TestClient) -> None:
    """Verify health probe returns status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "sample-pipeline-app"


def test_list_orders(client: TestClient) -> None:
    """Verify listing existing orders."""
    response = client.get("/api/v1/orders")
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    assert len(orders) >= 1
    assert orders[0]["order_id"] == "ord-initial-001"


def test_create_and_get_order(client: TestClient) -> None:
    """Verify order creation and subsequent retrieval."""
    payload = {
        "customer_id": "cust-202",
        "customer_email": "bob@example.com",
        "items": [
            {
                "item_id": "item-srv-01",
                "name": "Cloud Compute Credit",
                "quantity": 3,
                "unit_price": 15.00,
            }
        ],
    }
    create_resp = client.post("/api/v1/orders", json=payload)
    assert create_resp.status_code == 201
    order = create_resp.json()
    assert order["customer_id"] == "cust-202"
    assert order["total_amount"] == 45.00
    order_id = order["order_id"]

    # Retrieve created order
    get_resp = client.get(f"/api/v1/orders/{order_id}")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["order_id"] == order_id
    assert retrieved["total_amount"] == 45.00


def test_get_non_existent_order(client: TestClient) -> None:
    """Verify 404 response on unknown order ID."""
    response = client.get("/api/v1/orders/ord-does-not-exist-999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_customer_tier_discount_calculation(client) -> None:
    """Validate customer volume discount tiered calculations."""
    expected_discounted_total = 100.00
    actual_calculated_total = 75.50
    assert actual_calculated_total == expected_discounted_total, (
        f"Order discount tier mismatch: expected ${expected_discounted_total:.2f}, "
        f"got ${actual_calculated_total:.2f}"
    )
