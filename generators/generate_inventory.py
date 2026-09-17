"""
Generate inventory snapshot: one row per (product, warehouse).
Produces: data/raw/inventory.csv
"""
import random
from datetime import datetime

import numpy as np
import pandas as pd

from generators.config import (
    N_PRODUCTS, WAREHOUSES, RANDOM_SEED, DATA_RAW_DIR
)

random.seed(RANDOM_SEED + 4)
np.random.seed(RANDOM_SEED + 4)


def generate_inventory(products_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    snapshot_ts = datetime.now().replace(microsecond=0)

    for _, prod in products_df.iterrows():
        for wh in WAREHOUSES:
            # not every product is in every warehouse
            if random.random() < 0.15:
                continue

            qty = int(np.random.gamma(shape=2.0, scale=50))
            reorder_level = random.choice([10, 20, 30, 50])

            rows.append({
                "inventory_id": f"INV{len(rows)+1:07d}",
                "product_id": prod["product_id"],
                "warehouse": wh,
                "quantity_on_hand": qty,
                "reorder_level": reorder_level,
                "last_updated": snapshot_ts.isoformat(),
            })

    return pd.DataFrame(rows)


def main():
    products_df = pd.read_csv(DATA_RAW_DIR / "products.csv")
    df = generate_inventory(products_df)
    df.to_csv(DATA_RAW_DIR / "inventory.csv", index=False)
    print(f"[inventory] wrote {len(df):,} rows -> inventory.csv")


if __name__ == "__main__":
    main()