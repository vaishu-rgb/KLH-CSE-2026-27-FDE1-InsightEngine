"""
Generate synthetic customer data.
Produces: data/raw/customers.csv
"""
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from generators.config import (
    N_CUSTOMERS, COUNTRIES_CITIES, CUSTOMER_SEGMENTS,
    CUSTOMER_SEGMENT_WEIGHTS, DIRTY_RATES, RANDOM_SEED, DATA_RAW_DIR
)

fake = Faker()
Faker.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def generate_customers(n: int = N_CUSTOMERS) -> pd.DataFrame:
    countries = list(COUNTRIES_CITIES.keys())

    rows = []
    for i in range(1, n + 1):
        country = random.choices(countries, weights=[0.5, 0.2, 0.1, 0.1, 0.1])[0]
        city = random.choice(COUNTRIES_CITIES[country])

        signup_date = datetime.now() - timedelta(days=random.randint(1, 900))
        segment = random.choices(CUSTOMER_SEGMENTS, weights=CUSTOMER_SEGMENT_WEIGHTS)[0]

        email = fake.email()
        # inject dirty data
        if random.random() < DIRTY_RATES["customer_null_email"]:
            email = None

        rows.append({
            "customer_id": f"CUST{i:06d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": email,
            "phone": fake.phone_number()[:20],
            "city": city,
            "country": country,
            "signup_date": signup_date.date().isoformat(),
            "segment": segment,
        })

    df = pd.DataFrame(rows)
    return df


def main():
    df = generate_customers()
    out = DATA_RAW_DIR / "customers.csv"
    df.to_csv(out, index=False)
    print(f"[customers] wrote {len(df):,} rows -> {out}")


if __name__ == "__main__":
    main()