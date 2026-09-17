"""
Generate synthetic orders + order items.
Produces: data/raw/orders.csv, data/raw/order_items.csv
"""
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from generators.config import (
    N_ORDERS, AVG_ITEMS_PER_ORDER, ORDER_STATUSES, ORDER_STATUS_WEIGHTS,
    DIRTY_RATES, RANDOM_SEED, DATA_RAW_DIR, N_CUSTOMERS, N_PRODUCTS, DAYS_BACK
)

random.seed(RANDOM_SEED + 2)
np.random.seed(RANDOM_SEED + 2)


def _random_order_datetime() -> datetime:
    """Weighted toward recent dates, with evening/weekend seasonality."""
    days_ago = int(np.random.exponential(scale=DAYS_BACK / 3))
    days_ago = min(days_ago, DAYS_BACK)
    dt = datetime.now() - timedelta(days=days_ago)

    # hour bias: more activity 10am–10pm
    hour = random.choices(
        range(24),
        weights=[1,1,1,1,1,2,3,5,7,9,10,11,12,11,10,10,11,12,13,14,13,11,7,3]
    )[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return dt.replace(hour=hour, minute=minute, second=second)


def generate_orders(n_orders: int = N_ORDERS):
    customer_ids = [f"CUST{i:06d}" for i in range(1, N_CUSTOMERS + 1)]
    product_ids = [f"PROD{i:05d}" for i in range(1, N_PRODUCTS + 1)]

    orders = []
    order_items = []

    for i in range(1, n_orders + 1):
        order_id = f"ORD{i:08d}"
        customer_id = random.choice(customer_ids)
        order_ts = _random_order_datetime()
        status = random.choices(ORDER_STATUSES, weights=ORDER_STATUS_WEIGHTS)[0]

        n_items = max(1, int(np.random.poisson(AVG_ITEMS_PER_ORDER)))
        line_items = []

        for j in range(n_items):
            product_id = random.choice(product_ids)
            qty = max(1, int(np.random.poisson(2)))

            if random.random() < DIRTY_RATES["order_item_negative_qty"]:
                qty = -qty

            unit_price = round(random.uniform(10, 500), 2)

            line_items.append({
                "order_item_id": f"OI{i:08d}{j+1:02d}",
                "order_id": order_id,
                "product_id": product_id,
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": round(qty * unit_price, 2),
            })

        total_amount = round(sum(li["line_total"] for li in line_items), 2)

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_ts.date().isoformat(),
            "order_timestamp": order_ts.isoformat(),
            "status": status,
            "total_amount": total_amount,
            "currency": "USD",
        })

        order_items.extend(line_items)

    orders_df = pd.DataFrame(orders)
    items_df = pd.DataFrame(order_items)

    # inject duplicates
    n_dupes = int(n_orders * DIRTY_RATES["order_duplicate"])
    if n_dupes > 0:
        dupes = orders_df.sample(n=n_dupes, random_state=RANDOM_SEED)
        orders_df = pd.concat([orders_df, dupes], ignore_index=True)

    return orders_df, items_df


def main():
    orders_df, items_df = generate_orders()
    orders_df.to_csv(DATA_RAW_DIR / "orders.csv", index=False)
    items_df.to_csv(DATA_RAW_DIR / "order_items.csv", index=False)
    print(f"[orders]     wrote {len(orders_df):,} rows -> orders.csv")
    print(f"[order_items] wrote {len(items_df):,} rows -> order_items.csv")


if __name__ == "__main__":
    main()