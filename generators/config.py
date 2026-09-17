"""
Central configuration for synthetic data generation.
All tunable knobs live here — change once, affects all generators.
"""
from pathlib import Path

# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Row counts ----------
N_CUSTOMERS = 5_000
N_PRODUCTS = 500
N_ORDERS = 50_000
AVG_ITEMS_PER_ORDER = 3
N_WAREHOUSES = 4

# ---------- Date range (last 12 months from today) ----------
DAYS_BACK = 365

# ---------- Dirty data injection rates ----------
DIRTY_RATES = {
    "customer_null_email": 0.02,       # 2% null emails
    "product_negative_price": 0.01,    # 1% negative prices
    "order_duplicate": 0.005,          # 0.5% duplicated orders
    "order_item_negative_qty": 0.01,   # 1% negative quantities
    "payment_invalid_status": 0.01,    # 1% garbage statuses
}

# ---------- Reproducibility ----------
RANDOM_SEED = 42

# ---------- Reference data ----------
COUNTRIES_CITIES = {
    "India":        ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"],
    "USA":          ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Seattle", "Boston"],
    "UK":           ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool"],
    "Germany":      ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"],
    "Canada":       ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
}

CUSTOMER_SEGMENTS = ["bronze", "silver", "gold", "platinum"]
CUSTOMER_SEGMENT_WEIGHTS = [0.5, 0.3, 0.15, 0.05]

PRODUCT_CATEGORIES = {
    "Electronics":   (50, 2000),
    "Clothing":      (10, 200),
    "Home & Kitchen":(15, 500),
    "Books":         (5, 80),
    "Sports":        (20, 800),
    "Beauty":        (8, 150),
    "Toys":          (10, 300),
    "Grocery":       (2, 50),
}

ORDER_STATUSES = ["pending", "shipped", "delivered", "cancelled", "returned"]
ORDER_STATUS_WEIGHTS = [0.05, 0.15, 0.70, 0.06, 0.04]

PAYMENT_METHODS = ["credit_card", "debit_card", "upi", "net_banking", "wallet", "cod"]
PAYMENT_METHOD_WEIGHTS = [0.35, 0.15, 0.25, 0.10, 0.10, 0.05]

PAYMENT_STATUSES = ["success", "failed", "refunded"]
PAYMENT_STATUS_WEIGHTS = [0.92, 0.05, 0.03]

WAREHOUSES = ["WH-North", "WH-South", "WH-East", "WH-West"]