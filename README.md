# Order Processing Service

High-performance customer order intake and processing microservice built with FastAPI.

## Architecture & Features

- **Order Management**: Create, list, and query customer orders with itemized pricing.
- **Health Probes**: Liveness and readiness endpoints for container orchestration.
- **Type Safety**: Pydantic v2 data models and environment-based configuration.
- **CI/CD Automation**: Multi-stage GitHub Actions workflow for linting, testing, container packaging, and deployment.

---

## Local Development

### Prerequisites
- Python 3.11+
- Virtual environment

### Installation
```bash
pip install -e .[test]
```

### Running the Service Locally
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Running Unit Tests
```bash
pytest tests/ -v
```

### Running Linter
```bash
ruff check app/
```

---

## API Endpoints

- `GET /`: Service metadata and runtime status
- `GET /health`: Liveness and readiness probe endpoint
- `GET /api/v1/orders`: List all confirmed customer orders
- `POST /api/v1/orders`: Create a new customer order with itemized products
- `GET /api/v1/orders/{order_id}`: Retrieve order details by ID
