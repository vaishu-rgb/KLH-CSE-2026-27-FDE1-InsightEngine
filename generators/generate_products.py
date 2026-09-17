"""
Generate synthetic product catalog.
Produces: data/raw/products.csv
"""
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from generators.config import (
    N_PRODUCTS, PRODUCT_CATEGORIES, DIRTY_RATES,
    RANDOM_SEED, DATA_RAW_DIR
)

fake = Faker()
Faker.seed(RANDOM_SEED + 1)
random.seed(RANDOM_SEED + 1)
np.random.seed(RANDOM_SEED + 1)


def generate_products(n: int = N_PRODUCTS) -> pd.DataFrame:
    categories = list(PRODUCT_CATEGORIES.keys())
    rows = []

    for i in range(1, n + 1):
        category = random.choice(categories)
        price_min, price_max = PRODUCT_CATEGORIES[category]
        price = round(random.uniform(price_min, price_max), 2)

        if random.random() < DIRTY_RATES["product_negative_price"]:
            price = -abs(price)

        created_at = datetime.now() - timedelta(days=random.randint(1, 800))

        rows.append({
            "product_id": f"PROD{i:05d}",
            "product_name": f"{fake.word().capitalize()} {fake.word().capitalize()} {category[:4]}",
            "category": category,
            "brand": fake.company(),
            "price": price,
            "cost": round(abs(price) * random.uniform(0.4, 0.7), 2),
            "created_at": created_at.date().isoformat(),
        })

    return pd.DataFrame(rows)


def main():
    df = generate_products()
    out = DATA_RAW_DIR / "products.csv"
    df.to_csv(out, index=False)
    print(f"[products] wrote {len(df):,} rows -> {out}")


if __name__ == "__main__":
    main()