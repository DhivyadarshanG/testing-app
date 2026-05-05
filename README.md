# 🦗 Bug Zoo - Buggy E-Commerce API

A production-grade e-commerce API with **intentional bugs** for testing self-healing agents. This application contains real bugs that commonly occur in production systems.

## ⚠️ Warning

This application contains **intentional bugs** for testing purposes. Do not use in production!

## 🐛 Bugs Included

This application contains **10 production-grade bugs** across different categories:

### Authentication & Security Bugs
1. **Missing Null Check on Token Validation** - Crashes when validating invalid tokens
2. **Token Expiry Not Checked** - Accepts expired authentication tokens
3. **Password Hash Not Verified** - Incorrect password comparison logic
4. **Missing Permission Check** - Any user can delete any other user

### Data Handling Bugs
5. **Null Pointer on Discount Calculation** - Crashes when product has no discount
6. **Missing User Validation** - Crashes when creating order with invalid user

### Transaction & Concurrency Bugs
7. **Missing Transaction Rollback** - Leaves inconsistent state when payment fails
8. **Race Condition in Stock Update** - Concurrent orders can cause negative stock

### Resource Management Bugs
9. **Database Connection Leak** - Creates connections without closing them
10. **Redis Connection Pool Exhaustion** - Creates new Redis client for each request

### Business Logic Bugs
11. **No Quantity Validation** - Allows negative order quantities
12. **No Discount Validation** - Allows discount > 100%
13. **Incorrect Tax Calculation** - Calculates tax on wrong amount
14. **Cache Invalidation Race** - Updates cache before database commit

## 🏗️ Application Architecture

```
Bug Zoo E-Commerce API
├── Authentication System (JWT tokens, sessions)
├── User Management (CRUD operations)
├── Product Catalog (with pricing & discounts)
├── Order Processing (cart, checkout, payment)
├── Cache Layer (Redis)
└── Database (PostgreSQL)
```

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.ibm.com/Dhivyadarshan-G1/testingapp.git
cd testingapp

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f app
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run the application
uvicorn app.main:app --reload
```

## 📡 API Endpoints

Once running, access:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Main Endpoints

**Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user info

**Users**
- `GET /users/` - List all users
- `GET /users/{id}` - Get user by ID
- `DELETE /users/{id}` - Delete user (buggy!)

**Products**
- `GET /products/` - List all products
- `GET /products/{id}` - Get product by ID (buggy!)
- `POST /products/` - Create product
- `PUT /products/{id}/discount` - Apply discount (buggy!)

**Orders**
- `POST /orders/` - Create order (buggy!)
- `GET /orders/` - List user's orders
- `POST /orders/{id}/checkout` - Process payment (buggy!)

## 🧪 Testing the Bugs

### Bug 1: Missing Null Check on Token

```bash
# This will crash with 500 error
curl http://localhost:8000/auth/validate \
  -H "Authorization: Bearer invalid_token_12345"

# Expected: 401 Unauthorized
# Actual: 500 Internal Server Error (AttributeError)
```

### Bug 2: Token Expiry Not Checked

```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -d "username=user@example.com&password=password" | jq -r .access_token)

# Wait for token to expire (or manually create expired token in DB)
# Token still works even after expiry!
```

### Bug 3: Password Hash Not Verified

```bash
# This bug causes all logins to fail because it compares plain text with hash
curl -X POST http://localhost:8000/auth/login \
  -d "username=user@example.com&password=correctpassword"

# Always returns 401 even with correct password
```

### Bug 4: Missing Permission Check

```bash
# User A can delete User B without permission
curl -X DELETE http://localhost:8000/users/2 \
  -H "Authorization: Bearer $USER_A_TOKEN"

# Expected: 403 Forbidden
# Actual: 204 No Content (deleted!)
```

### Bug 5: Null Pointer on Discount

```bash
# Create product without discount
curl -X POST http://localhost:8000/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test","description":"Test","price":100,"stock_quantity":10}'

# Get product - crashes on discount calculation
curl http://localhost:8000/products/1

# Expected: 200 with price
# Actual: 500 (TypeError: unsupported operand type)
```

### Bug 6: Missing User Validation

```bash
# Create order with invalid user_id
curl -X POST http://localhost:8000/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"product_id":1,"quantity":1,"user_id":99999}'

# Expected: 400 Bad Request
# Actual: 500 (AttributeError: 'NoneType' has no attribute 'email')
```

### Bug 7: Missing Transaction Rollback

```bash
# Create order
ORDER_ID=1

# Try to checkout with invalid payment
curl -X POST http://localhost:8000/orders/$ORDER_ID/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"payment_method":"invalid"}'

# Payment fails but order status is already changed to "processing"
# Expected: Order status remains "pending"
# Actual: Order status is "processing" (data inconsistency)
```

### Bug 8: Race Condition in Stock

```bash
# Two concurrent requests to buy the last item
# Both succeed, stock becomes negative
```

### Bug 9: Database Connection Leak

```bash
# Bulk import products
curl -X POST http://localhost:8000/products/import \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"products":[...1000 products...]}'

# Creates 1000 database connections without closing them
# Eventually exhausts connection pool
```

### Bug 10: Redis Connection Pool Exhaustion

```bash
# Make many requests
for i in {1..100}; do
  curl http://localhost:8000/products/ &
done

# Each request creates new Redis connection
# Eventually exhausts connection pool
```

## 🔧 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_bugs.py::test_null_check_on_token -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 📊 CI/CD Integration

The GitHub Actions workflow automatically:
1. Runs tests on every push
2. Detects failures
3. Can trigger your self-healing agent via webhook

See `.github/workflows/ci.yml` for configuration.

## 🎯 For Self-Healing Agent Testing

This application is designed to test self-healing agents that can:

1. **Detect bugs** from test failures and stack traces
2. **Understand context** by analyzing the codebase
3. **Generate fixes** using AI/LLM
4. **Validate fixes** by re-running tests
5. **Learn from fixes** to handle similar bugs faster

### Expected Agent Workflow

```
1. CI runs tests → Test fails
2. Agent receives webhook with error details
3. Agent analyzes code and identifies bug location
4. Agent searches for similar past fixes (if any)
5. Agent generates fix using LLM + context
6. Agent validates fix by running tests
7. Agent opens PR with fix
8. Human reviews and merges
```

## 📝 Bug Documentation

For detailed information about each bug, including:
- Exact location in code
- How to trigger it
- Expected vs actual behavior
- Expected fix

See `docs/bug_catalog.md`

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Testing**: pytest
- **CI/CD**: GitHub Actions

## 📂 Project Structure

```
testingapp/
├── app/
│   ├── models/          # Database models
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic (bugs here!)
│   ├── utils/           # Utilities
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── main.py          # FastAPI app
├── tests/               # Test suite
├── docs/                # Documentation
├── .github/workflows/   # CI/CD
├── docker-compose.yml   # Docker setup
└── README.md
```

## 🤝 Contributing

This is a test application with intentional bugs. To add new bugs:

1. Add the buggy code to appropriate service
2. Document the bug in `docs/bug_catalog.md`
3. Add test case in `tests/`
4. Update this README

## 📄 License

MIT License - For testing purposes only

---

**Repository**: https://github.ibm.com/Dhivyadarshan-G1/testingapp

**⚠️ Remember**: This application contains intentional bugs. Do not use in production!