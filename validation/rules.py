"""
Validation rules for InsightEngine.
Every rule is a business decision, encoded in one place.
"""
from typing import Dict, List

# ---------- Allowed values ----------
ALLOWED_SEGMENTS = {"bronze", "silver", "gold", "platinum"}
ALLOWED_ORDER_STATUSES = {"pending", "shipped", "delivered", "cancelled", "returned"}
ALLOWED_PAYMENT_STATUSES = {"success", "failed", "refunded"}
ALLOWED_PAYMENT_METHODS = {"credit_card", "debit_card", "upi", "net_banking", "wallet", "cod"}
ALLOWED_CATEGORIES = {
    "Electronics", "Clothing", "Home & Kitchen", "Books",
    "Sports", "Beauty", "Toys", "Grocery",
}

# ---------- Column types to coerce to ----------
COLUMN_TYPES = {
    "customers": {
        "signup_date": "date",
    },
    "products": {
        "price": "float",
        "cost": "float",
        "created_at": "date",
    },
    "orders": {
        "order_date": "date",
        "order_timestamp": "datetime",
        "total_amount": "float",
    },
    "order_items": {
        "quantity": "int",
        "unit_price": "float",
        "line_total": "float",
    },
    "payments": {
        "payment_date": "date",
        "payment_timestamp": "datetime",
        "amount": "float",
    },
    "inventory": {
        "quantity_on_hand": "int",
        "reorder_level": "int",
        "last_updated": "datetime",
    },
}

# ---------- Referential integrity checks ----------
FOREIGN_KEYS = {
    "orders": [
        ("customer_id", "customers", "customer_id"),
    ],
    "order_items": [
        ("order_id", "orders", "order_id"),
        ("product_id", "products", "product_id"),
    ],
    "payments": [
        ("order_id", "orders", "order_id"),
    ],
    "inventory": [
        ("product_id", "products", "product_id"),
    ],
}

# ---------- Which tables we validate, in dependency order ----------
TABLE_ORDER: List[str] = [
    "customers",
    "products",
    "orders",
    "order_items",
    "payments",
    "inventory",
]

# ---------- Rule definitions (used for reporting) ----------
RULES: Dict[str, List[str]] = {
    "customers": [
        "customer_id must be unique",
        "segment must be in allowed list (else fixed to 'unknown')",
        "email nullability flagged, not rejected",
    ],
    "products": [
        "price must be > 0",
        "category must not be null",
    ],
    "orders": [
        "order_id must be unique",
        "customer_id must exist in customers",
        "status must be in allowed list (else fixed to 'unknown')",
        "total_amount must be > 0",
    ],
    "order_items": [
        "quantity must be > 0",
        "order_id must exist in orders",
        "product_id must exist in products",
    ],
    "payments": [
        "status must be in allowed list",
        "order_id must exist in orders",
        "amount must be > 0",
    ],
    "inventory": [
        "quantity_on_hand must be >= 0 (else fixed to 0)",
        "reorder_level must be > 0 (else fixed to 10)",
    ],
}