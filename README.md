# 🦗 Bug Zoo - Self-Healing Agent Test Application

A deliberately buggy FastAPI application designed to test and demonstrate self-healing bug fix agents. Contains 15 common bug patterns across 6 categories that can be toggled on/off for systematic testing.

## 🎯 Purpose

This application serves as a comprehensive test suite for the **Self-Healing Bug Fix Agent** (wxo + Project Bob + Vector Memory). It provides:

- **15 realistic bug patterns** that mirror production issues
- **Controllable bug activation** via API or environment variables
- **Comprehensive test suite** that fails when bugs are enabled
- **CI/CD integration** that triggers the healing agent on failures
- **Full API documentation** for easy exploration

## 🏗️ Architecture

```
Bug Zoo (FastAPI)
├── Authentication & Authorization
├── User Management
├── Product Catalog
├── Order Processing
├── Cache Layer (Redis)
└── Database (PostgreSQL)
```

## 🐛 Bug Catalog

### Category 1: Null/None Handling (3 bugs)

| Bug ID | Description | Location | Severity |
|--------|-------------|----------|----------|
| **BUG-001** | Missing Null Check on User Token | `app/services/auth_service.py:validate_token()` | HIGH |
| **BUG-002** | Unhandled None in Product Price | `app/services/product_service.py:calculate_discount()` | MEDIUM |
| **BUG-003** | Missing User Validation in Order | `app/services/order_service.py:create_order()` | HIGH |

### Category 2: Authentication/Authorization (3 bugs)

| Bug ID | Description | Location | Severity |
|--------|-------------|----------|----------|
| **BUG-004** | Token Expiry Not Checked | `app/services/auth_service.py:validate_token()` | CRITICAL |
| **BUG-005** | Missing Permission Check on Delete | `app/services/user_service.py:delete_user()` | CRITICAL |
| **BUG-006** | Password Hash Not Verified | `app/services/auth_service.py:authenticate_user()` | CRITICAL |

### Category 3: Database Transactions (2 bugs)

| Bug ID | Description | Location | Severity |
|--------|-------------|----------|----------|
| **BUG-007** | Missing Transaction Rollback | `app/services/order_service.py:process_payment()` | HIGH |
| **BUG-008** | Race Condition in Stock Update | `app/services/product_service.py:decrease_stock()` | MEDIUM |

### Category 4: Race Conditions (2 bugs)

| Bug ID | Description | Location | Severity |
|--------|-------------|----------|----------|
| **BUG-009** | Concurrent Session Creation | `app/services/auth_service.py:create_session()` | MEDIUM |
| **BUG-010** | Cache Invalidation Race | `app/services/cache_service.py:update_user_cache()` | LOW |

### Category 5: Memory/Resource Leaks (2 bugs)

| Bug ID | Description | Location | Severity |
|--------|-------------|----------|----------|
| **BUG-011** | Unclosed Database Connection | `app/services/product_service.py:bulk_import()` | HIGH |
| **BUG-012** | Redis Connection Pool Exhaustion | `app/services/cache_service.py:get_cached_data()` | MEDIUM |

### Category 6: Logic/Business Rules (3 bugs)

| Bug ID | Description | Location | Severity |
|--------|-------------|----------|----------|
| **BUG-013** | Negative Quantity Allowed | `app/routers/orders.py:create_order()` | MEDIUM |
| **BUG-014** | Discount Exceeds Price | `app/services/product_service.py:apply_discount()` | LOW |
| **BUG-015** | Order Total Miscalculation | `app/services/order_service.py:calculate_total()` | MEDIUM |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- PostgreSQL (if not using Docker)
- Redis (if not using Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd bug-zoo

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app
```

The application will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Bug Control**: http://localhost:8000/bugs/catalog

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Start PostgreSQL and Redis (or use Docker)
docker-compose up -d postgres redis

# Run the application
uvicorn app.main:app --reload
```

## 🎮 Usage

### 1. Explore the API

Visit http://localhost:8000/docs for interactive API documentation.

### 2. View Bug Catalog

```bash
curl http://localhost:8000/bugs/catalog
```

### 3. Enable a Specific Bug

```bash
# Via API
curl -X POST http://localhost:8000/bugs/001/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Via Environment Variable
export BUG_001_ENABLED=true
```

### 4. Test the Bug

```bash
# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'

# Try to validate with invalid token (triggers BUG-001)
curl http://localhost:8000/auth/validate \
  -H "Authorization: Bearer invalid_token"
```

### 5. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific bug test
pytest tests/test_bugs.py::TestBugCategory1NullHandling::test_bug_001_missing_null_check_on_token -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 🔧 Bug Control API

### Get All Bugs Status

```bash
GET /bugs/catalog
```

### Get Specific Bug Status

```bash
GET /bugs/{bug_id}
```

### Toggle Bug On/Off

```bash
POST /bugs/{bug_id}/toggle
{
  "enabled": true
}
```

### Enable All Bugs

```bash
POST /bugs/enable-all
```

### Disable All Bugs

```bash
POST /bugs/disable-all
```

## 🧪 Testing Strategy

Each bug has three types of tests:

1. **Positive Test** (bug disabled) - Should pass
2. **Negative Test** (bug enabled) - Should fail
3. **Fix Validation** - Verifies the expected fix works

### Example Test Flow

```python
# 1. Enable the bug
enable_bug("001")

# 2. Run the test (should fail)
response = client.get("/auth/validate", headers={"Authorization": "Bearer invalid"})
assert response.status_code == 401  # Fails with bug (returns 500)

# 3. Disable the bug
disable_bug("001")

# 4. Run again (should pass)
response = client.get("/auth/validate", headers={"Authorization": "Bearer invalid"})
assert response.status_code == 401  # Passes without bug
```

## 🔄 CI/CD Integration

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:

1. Tests each bug individually
2. Reports failures with detailed context
3. Triggers the self-healing agent webhook
4. Provides bug ID, location, and stack trace

### Trigger CI Manually

```bash
# Via GitHub UI: Actions → Bug Zoo CI → Run workflow

# Or via API
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/ci.yml/dispatches \
  -d '{"ref":"main","inputs":{"bug_id":"001"}}'
```

## 📊 Expected Fixes

Each bug has a documented expected fix:

### BUG-001: Missing Null Check

**Current (Buggy):**
```python
user = db.query(User).filter(User.id == session.user_id).first()
return user
```

**Expected Fix:**
```python
if not session:
    raise TokenNotFoundError("Invalid or expired token")
user = db.query(User).filter(User.id == session.user_id).first()
return user
```

### BUG-002: Unhandled None in Discount

**Current (Buggy):**
```python
discount_amount = product.price * (product.discount_percentage / 100)
return product.price - discount_amount
```

**Expected Fix:**
```python
if product.discount_percentage is None or product.discount_percentage == 0:
    return product.price
discount_amount = product.price * (product.discount_percentage / 100)
return product.price - discount_amount
```

*See `docs/bug_catalog.md` for all expected fixes.*

## 🎯 Integration with Self-Healing Agent

### Webhook Payload

When a test fails, the CI sends this payload to your healing agent:

```json
{
  "repository": "owner/bug-zoo",
  "branch": "refs/heads/main",
  "commit": "abc123...",
  "bug_id": "001",
  "test_name": "test_bug_001_missing_null_check_on_token",
  "workflow_run_id": "123456789",
  "stack_trace": "...",
  "file_path": "app/services/auth_service.py",
  "line_number": 95
}
```

### Agent Workflow

1. **Localizer Agent**: Parses stack trace → identifies `auth_service.py:95`
2. **Memory Searcher**: Queries vector DB → finds similar past fix (94% match)
3. **Bob Patcher**: Generates fix using context + past fix as template
4. **Validator**: Applies patch → re-runs test → verifies fix
5. **PR Agent**: Opens PR with auto-generated description

## 📁 Project Structure

```
bug-zoo/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # FastAPI endpoints
│   ├── services/        # Business logic (bugs here!)
│   ├── utils/           # Utilities
│   ├── config.py        # Settings & bug flags
│   ├── database.py      # DB setup
│   └── main.py          # FastAPI app
├── tests/
│   ├── conftest.py      # Test fixtures
│   └── test_bugs.py     # Bug tests
├── .github/
│   └── workflows/
│       └── ci.yml       # CI pipeline
├── docs/
│   └── bug_catalog.md   # Detailed bug documentation
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🤝 Contributing

This is a test application with intentional bugs. To add new bugs:

1. Add bug flag to `app/config.py`
2. Implement buggy code in appropriate service
3. Add test in `tests/test_bugs.py`
4. Document in `docs/bug_catalog.md`
5. Update CI workflow matrix

## 📝 License

MIT License - This is a demonstration/testing application.

## 🙏 Acknowledgments

Built for testing the Self-Healing Bug Fix Agent using:
- **watsonx Orchestrate (wxo)** - Multi-agent orchestration
- **Project Bob** - Code understanding & patch generation
- **IBM Granite** - LLM backbone & embeddings
- **ChromaDB/Milvus** - Vector memory for past fixes

---

**⚠️ Warning**: This application contains intentional bugs. Do not use in production!

For questions or issues, please open a GitHub issue.