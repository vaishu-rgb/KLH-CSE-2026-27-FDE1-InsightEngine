"""
Orchestrator: runs all generators in dependency order.
Usage:  python -m generators.run_all
"""
import time

from generators import (
    generate_customers,
    generate_products,
    generate_orders,
    generate_payments,
    generate_inventory,
)


def main():
    print("=" * 60)
    print("InsightEngine — Synthetic Data Generation")
    print("=" * 60)

    t0 = time.time()

    print("\n[1/5] customers...")
    generate_customers.main()

    print("\n[2/5] products...")
    generate_products.main()

    print("\n[3/5] orders + order_items...")
    generate_orders.main()

    print("\n[4/5] payments...")
    generate_payments.main()

    print("\n[5/5] inventory...")
    generate_inventory.main()

    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print(f"✅ Generation complete in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()