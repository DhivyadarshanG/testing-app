# 🐛 Complete Bug Catalog & Expected Fixes

This document provides detailed information about each bug, including the exact location, trigger conditions, expected behavior, buggy behavior, and the expected fix.

---

## Category 1: Null/None Handling Bugs

### BUG-001: Missing Null Check on User Token

**Location**: `app/services/auth_service.py:validate_token()`

**Severity**: HIGH

**Description**: The function accesses `session.user_id` without first checking if `session` is None, causing an AttributeError when an invalid token is provided.

**Trigger**:
```bash
curl http://localhost:8000/auth/validate \
  -H "Authorization: Bearer invalid_token_12345"
```

**Expected Behavior**: Return 401 Unauthorized with message "Invalid or expired token"

**Buggy Behavior**: Crashes with 500 Internal Server Error - `AttributeError: 'NoneType' object has no attribute 'user_id'`

**Current Code (Buggy)**:
```python
def validate_token(db: Session, token: str) -> Optional[User]:
    session = db.query(UserSession).filter(UserSession.token == token).first()
    
    if is_bug_enabled("001"):
        # BUGGY: Accessing user_id without checking if session is None
        user = db.query(User).filter(User.id == session.user_id).first()
        return user
```

**Expected Fix**:
```python
def validate_token(db: Session, token: str) -> Optional[User]:
    session = db.query(UserSession).filter(UserSession.token == token).first()
    
    # CORRECT: Check if session exists before accessing attributes
    if not session:
        raise TokenNotFoundError("Invalid or expired token")
    
    user = db.query(User).filter(User.id == session.user_id).first()
    return user
```

---

### BUG-002: Unhandled None in Product Price Calculation

**Location**: `app/services/product_service.py:calculate_discount()`

**Severity**: MEDIUM

**Description**: Performs mathematical operation on None discount_percentage without checking if it's None first.

**Trigger**:
```bash
# Create product with None discount
curl -X POST http://localhost:8000/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test","description":"Test","price":100,"stock_quantity":10}'

# Get product (triggers discount calculation)
curl http://localhost:8000/products/1
```

**Expected Behavior**: Return product with original price when discount is None

**Buggy Behavior**: Crashes with `TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'`

**Current Code (Buggy)**:
```python
def calculate_discount(product: Product) -> float:
    if is_bug_enabled("002"):
        # BUGGY: No null check on discount_percentage
        discount_amount = product.price * (product.discount_percentage / 100)
        return product.price - discount_amount
```

**Expected Fix**:
```python
def calculate_discount(product: Product) -> float:
    # CORRECT: Handle None discount
    if product.discount_percentage is None or product.discount_percentage == 0:
        return product.price
    
    discount_amount = product.price * (product.discount_percentage / 100)
    return product.price - discount_amount
```

---

### BUG-003: Missing User Validation in Order Creation

**Location**: `app/services/order_service.py:create_order()`

**Severity**: HIGH

**Description**: Accesses `user.email` without validating that the user exists.

**Trigger**:
```python
# In code, call create_order with invalid user_id
order_service.create_order(db, user_id=99999, product_id=1, quantity=1)
```

**Expected Behavior**: Raise UserNotFoundError with message "User 99999 not found"

**Buggy Behavior**: Crashes with `AttributeError: 'NoneType' object has no attribute 'email'`

**Current Code (Buggy)**:
```python
def create_order(db: Session, user_id: int, product_id: int, quantity: int) -> Order:
    if is_bug_enabled("003"):
        # BUGGY: Access user.email without checking if user exists
        user = db.query(User).filter(User.id == user_id).first()
        email = user.email  # Will crash if user is None
```

**Expected Fix**:
```python
def create_order(db: Session, user_id: int, product_id: int, quantity: int) -> Order:
    # CORRECT: Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
```

---

## Category 2: Authentication/Authorization Bugs

### BUG-004: Token Expiry Not Checked

**Location**: `app/services/auth_service.py:validate_token()`

**Severity**: CRITICAL (Security Issue)

**Description**: Returns user even if the session token has expired.

**Trigger**:
```python
# Create expired session in database
expired_session = UserSession(
    user_id=1,
    token="expired_token",
    expires_at=datetime.utcnow() - timedelta(hours=1)
)
db.add(expired_session)
db.commit()

# Try to use expired token
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer expired_token"
```

**Expected Behavior**: Return 401 with "Token has expired"

**Buggy Behavior**: Returns 200 with user data (security vulnerability!)

**Current Code (Buggy)**:
```python
if is_bug_enabled("004"):
    # BUGGY: Return user even if token is expired
    user = db.query(User).filter(User.id == session.user_id).first()
    return user
```

**Expected Fix**:
```python
# CORRECT: Check token expiry
if session.is_expired():
    raise TokenNotFoundError("Token has expired")

user = db.query(User).filter(User.id == session.user_id).first()
return user
```

---

### BUG-005: Missing Permission Check on Delete

**Location**: `app/services/user_service.py:delete_user()`

**Severity**: CRITICAL (Security Issue)

**Description**: Any authenticated user can delete any other user without permission check.

**Trigger**:
```bash
# User A tries to delete User B
curl -X DELETE http://localhost:8000/users/2 \
  -H "Authorization: Bearer $USER_A_TOKEN"
```

**Expected Behavior**: Return 403 Forbidden "You don't have permission to delete this user"

**Buggy Behavior**: Returns 204 and deletes the user (security vulnerability!)

**Current Code (Buggy)**:
```python
def delete_user(db: Session, user_id: int, current_user: User) -> bool:
    if is_bug_enabled("005"):
        # BUGGY: No permission check - any user can delete any user
        db.delete(user)
        db.commit()
        return True
```

**Expected Fix**:
```python
def delete_user(db: Session, user_id: int, current_user: User) -> bool:
    # CORRECT: Check if user is deleting themselves or is admin
    if current_user.id != user_id and not current_user.is_admin:
        raise_forbidden("You don't have permission to delete this user")
    
    db.delete(user)
    db.commit()
    return True
```

---

### BUG-006: Password Hash Not Verified

**Location**: `app/services/auth_service.py:authenticate_user()`

**Severity**: CRITICAL (Security Issue)

**Description**: Compares plain text password directly instead of using bcrypt verification.

**Trigger**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=test@example.com&password=wrongpassword"
```

**Expected Behavior**: Return 401 for wrong password

**Buggy Behavior**: Always returns 401 because plain text never matches hash

**Current Code (Buggy)**:
```python
if is_bug_enabled("006"):
    # BUGGY: Direct comparison instead of hash verification
    if password == user.hashed_password:
        return user
    return None
```

**Expected Fix**:
```python
# CORRECT: Use bcrypt verification
if not verify_password(password, user.hashed_password):
    return None
return user
```

---

## Category 3: Database Transaction Bugs

### BUG-007: Missing Transaction Rollback

**Location**: `app/services/order_service.py:process_payment()`

**Severity**: HIGH (Data Inconsistency)

**Description**: When payment fails, the order status is already changed and not rolled back.

**Trigger**:
```bash
curl -X POST http://localhost:8000/orders/1/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"payment_method":"invalid"}'
```

**Expected Behavior**: Payment fails, order status remains "pending"

**Buggy Behavior**: Payment fails but order status is changed to "processing" (data inconsistency)

**Current Code (Buggy)**:
```python
if is_bug_enabled("007"):
    # BUGGY: No transaction rollback on failure
    order.status = OrderStatus.PROCESSING
    db.commit()
    
    if payment_method == "invalid":
        # Payment fails but order status already changed!
        raise PaymentFailedError("Payment processing failed")
```

**Expected Fix**:
```python
# CORRECT: Use try-except with rollback
try:
    order.status = OrderStatus.PROCESSING
    db.commit()
    
    if payment_method == "invalid":
        raise PaymentFailedError("Payment processing failed")
    
    order.payment_status = "completed"
    order.status = OrderStatus.COMPLETED
    db.commit()
except Exception as e:
    db.rollback()
    order.status = OrderStatus.FAILED
    db.commit()
    raise
```

---

### BUG-008: Race Condition in Stock Update

**Location**: `app/services/product_service.py:decrease_stock()`

**Severity**: MEDIUM

**Description**: Uses read-modify-write pattern without row locking, causing race conditions in concurrent stock updates.

**Trigger**: Two concurrent requests trying to decrease stock

**Expected Behavior**: Stock decreases correctly even with concurrent requests

**Buggy Behavior**: Lost updates - final stock count is incorrect

**Current Code (Buggy)**:
```python
if is_bug_enabled("008"):
    # BUGGY: Read-modify-write without lock (race condition)
    product = db.query(Product).filter(Product.id == product_id).first()
    product.stock_quantity -= quantity
    db.commit()
```

**Expected Fix**:
```python
# CORRECT: Use SELECT FOR UPDATE to lock the row
product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
product.stock_quantity -= quantity
db.commit()
```

---

## Category 4: Race Condition Bugs

### BUG-009: Concurrent Session Creation

**Location**: `app/services/auth_service.py:create_session()`

**Severity**: MEDIUM

**Description**: Doesn't handle race conditions when multiple login requests create sessions simultaneously.

**Trigger**: Rapid concurrent login requests

**Expected Behavior**: Handle duplicate session creation gracefully

**Buggy Behavior**: May create duplicate sessions or crash with IntegrityError

**Current Code (Buggy)**:
```python
if is_bug_enabled("009"):
    # BUGGY: Just create without checking for existing sessions
    session = UserSession(user_id=user_id, token=token, expires_at=expires_at)
    db.add(session)
    db.commit()
```

**Expected Fix**:
```python
# CORRECT: Handle IntegrityError and return existing session
try:
    session = UserSession(user_id=user_id, token=token, expires_at=expires_at)
    db.add(session)
    db.commit()
except IntegrityError:
    db.rollback()
    existing = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).first()
    if existing:
        return existing
    raise
```

---

### BUG-010: Cache Invalidation Race

**Location**: `app/services/cache_service.py:update_user_cache()`

**Severity**: LOW (Stale Data)

**Description**: Updates cache before database commit, leading to stale data if commit fails.

**Trigger**: Update user data with cache enabled

**Expected Behavior**: Cache updated after successful DB commit

**Buggy Behavior**: Cache contains new data but DB still has old data

**Current Code (Buggy)**:
```python
if is_bug_enabled("010"):
    # BUGGY: Update cache before DB commit
    set_cached_data(cache_key, user_data)
    if db_commit_callback:
        db_commit_callback()
```

**Expected Fix**:
```python
# CORRECT: Commit to DB first, then invalidate cache
if db_commit_callback:
    db_commit_callback()

# Invalidate cache after DB commit to force refresh
invalidate_cache(cache_key)
```

---

## Category 5: Memory/Resource Leak Bugs

### BUG-011: Unclosed Database Connection

**Location**: `app/services/product_service.py:bulk_import()`

**Severity**: HIGH (Resource Exhaustion)

**Description**: Creates new database connections in a loop without closing them.

**Trigger**:
```bash
curl -X POST http://localhost:8000/products/import \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"products":[...]}'  # Large list
```

**Expected Behavior**: Use existing session, no connection leaks

**Buggy Behavior**: Creates new engine/connection for each product, exhausts connection pool

**Current Code (Buggy)**:
```python
if is_bug_enabled("011"):
    for product_data in products_data:
        # Creating new engine/connection each time - memory leak!
        engine = create_engine(settings.database_url)
        connection = engine.connect()
        # Connection never closed!
```

**Expected Fix**:
```python
# CORRECT: Use existing session, no extra connections
for product_data in products_data:
    product = Product(**product_data)
    db.add(product)

db.commit()
```

---

### BUG-012: Redis Connection Pool Exhaustion

**Location**: `app/services/cache_service.py:get_cached_data()`

**Severity**: MEDIUM

**Description**: Creates new Redis client for each call instead of reusing connection pool.

**Trigger**: High traffic to cached endpoints

**Expected Behavior**: Reuse connection pool

**Buggy Behavior**: Creates new connection each time, exhausts pool

**Current Code (Buggy)**:
```python
if is_bug_enabled("012"):
    # BUGGY: Creates new Redis client every time
    r = redis.Redis.from_url(settings.redis_url)
    data = r.get(key)
```

**Expected Fix**:
```python
# CORRECT: Reuse connection pool
pool = get_redis_pool()
r = redis.Redis(connection_pool=pool)
data = r.get(key)
```

---

## Category 6: Logic/Business Rule Bugs

### BUG-013: Negative Quantity Allowed

**Location**: `app/routers/orders.py:create_order()`

**Severity**: MEDIUM

**Description**: No validation on order quantity, allows negative values.

**Trigger**:
```bash
curl -X POST http://localhost:8000/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"product_id":1,"quantity":-5}'
```

**Expected Behavior**: Return 400 "Quantity must be positive"

**Buggy Behavior**: Creates order with negative quantity

**Current Code (Buggy)**:
```python
if is_bug_enabled("013"):
    # BUGGY: No validation on quantity
    pass
```

**Expected Fix**:
```python
# CORRECT: Validate quantity
if quantity <= 0:
    raise InvalidQuantityError("Quantity must be positive")
```

---

### BUG-014: Discount Exceeds Price

**Location**: `app/services/product_service.py:apply_discount()`

**Severity**: LOW

**Description**: Allows discount percentage greater than 100%, resulting in negative prices.

**Trigger**:
```bash
curl -X PUT http://localhost:8000/products/1/discount \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"discount_percentage":150}'
```

**Expected Behavior**: Return 400 "Discount must be between 0 and 100"

**Buggy Behavior**: Accepts 150% discount, price becomes negative

**Current Code (Buggy)**:
```python
if is_bug_enabled("014"):
    # BUGGY: Allow any discount percentage
    product.discount_percentage = discount_percentage
    db.commit()
```

**Expected Fix**:
```python
# CORRECT: Validate discount percentage
if discount_percentage < 0 or discount_percentage > 100:
    raise InvalidDiscountError("Discount must be between 0 and 100")

product.discount_percentage = discount_percentage
db.commit()
```

---

### BUG-015: Order Total Miscalculation

**Location**: `app/services/order_service.py:calculate_total()`

**Severity**: MEDIUM (Financial Impact)

**Description**: Calculates tax on discounted price instead of original price.

**Trigger**:
```bash
# Create order with product that has discount
curl -X POST http://localhost:8000/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"product_id":1,"quantity":1}'
```

**Expected Behavior**: Tax calculated on original price: `(price * 1.10) - discount`

**Buggy Behavior**: Tax calculated on discounted price: `(price - discount) * 1.10`

**Current Code (Buggy)**:
```python
if is_bug_enabled("015"):
    # BUGGY: Calculate tax on discounted price
    subtotal = (unit_price * quantity) - discount_amount
    tax = subtotal * TAX_RATE
    total = subtotal + tax
```

**Expected Fix**:
```python
# CORRECT: Calculate tax on original price, then apply discount
subtotal = unit_price * quantity
tax = subtotal * TAX_RATE
total = subtotal + tax - discount_amount
```

**Example**:
- Product: $100, Discount: 10%, Tax: 10%
- Buggy: ($100 - $10) * 1.10 = $99
- Correct: ($100 * 1.10) - $10 = $100

---

## Testing Each Bug

For each bug, follow this pattern:

```python
# 1. Enable the bug
enable_bug("XXX")
get_settings.cache_clear()

# 2. Trigger the buggy code path
response = client.post("/endpoint", ...)

# 3. Assert expected failure
assert response.status_code == expected_error_code

# 4. Disable the bug
disable_bug("XXX")
get_settings.cache_clear()

# 5. Verify fix works
response = client.post("/endpoint", ...)
assert response.status_code == 200
```

---

## Summary

| Category | Bug Count | Severity Distribution |
|----------|-----------|----------------------|
| Null/None Handling | 3 | 2 HIGH, 1 MEDIUM |
| Authentication/Authorization | 3 | 3 CRITICAL |
| Database Transactions | 2 | 1 HIGH, 1 MEDIUM |
| Race Conditions | 2 | 1 MEDIUM, 1 LOW |
| Memory/Resource Leaks | 2 | 1 HIGH, 1 MEDIUM |
| Logic/Business Rules | 3 | 2 MEDIUM, 1 LOW |
| **Total** | **15** | **3 CRITICAL, 4 HIGH, 6 MEDIUM, 2 LOW** |

All bugs are production-realistic and commonly found in real applications. They provide excellent test cases for self-healing agents.