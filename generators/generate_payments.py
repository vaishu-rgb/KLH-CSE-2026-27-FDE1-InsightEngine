"""
Generate synthetic payments linked to orders.
Produces: data/raw/payments.csv
"""
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from generators.config import (
    PAYMENT_METHODS, PAYMENT_METHOD_WEIGHTS,
    PAYMENT_STATUSES, PAYMENT_STATUS_WEIGHTS,
    DIRTY_RATES, RANDOM_SEED, DATA_RAW_DIR
)

random.seed(RANDOM_SEED + 3)
np.random.seed(RANDOM_SEED + 3)


def generate_payments(orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each order, generate 0 or 1 payment.
    Cancelled orders mostly have no payment.
    """
    rows = []
    pay_counter = 1

    for _, order in orders_df.iterrows():
        status = order["status"]
        # cancelled orders usually didn't pay
        if status == "cancelled" and random.random() < 0.8:
            continue

        pay_status = random.choices(PAYMENT_STATUSES, weights=PAYMENT_STATUS_WEIGHTS)[0]

        if random.random() < DIRTY_RATES["payment_invalid_status"]:
            pay_status = "UNKNOWN_" + str(random.randint(1, 99))

        order_ts = datetime.fromisoformat(order["order_timestamp"])
        pay_ts = order_ts + timedelta(minutes=random.randint(1, 120))

        rows.append({
            "payment_id": f"PAY{pay_counter:08d}",
            "order_id": order["order_id"],
            "payment_date": pay_ts.date().isoformat(),
            "payment_timestamp": pay_ts.isoformat(),
            "amount": order["total_amount"],
            "method": random.choices(PAYMENT_METHODS, weights=PAYMENT_METHOD_WEIGHTS)[0],
            "status": pay_status,
            "currency": "USD",
        })
        pay_counter += 1

    return pd.DataFrame(rows)


def main():
    orders_df = pd.read_csv(DATA_RAW_DIR / "orders.csv")
    df = generate_payments(orders_df)
    df.to_csv(DATA_RAW_DIR / "payments.csv", index=False)
    print(f"[payments] wrote {len(df):,} rows -> payments.csv")


if __name__ == "__main__":
    main()