-- ============================================================
-- InsightEngine — Analytics Views
-- Built on the star schema in insightengine_dw
-- These are what the Streamlit dashboard queries.
-- ============================================================

CREATE SCHEMA IF NOT EXISTS analytics;

-- ---------- 1. Daily revenue trend ----------
DROP VIEW IF EXISTS analytics.v_daily_revenue CASCADE;
CREATE VIEW analytics.v_daily_revenue AS
SELECT
    d.full_date,
    d.year,
    d.month,
    d.month_name,
    d.day_of_week,
    d.day_name,
    d.is_weekend,
    COUNT(DISTINCT f.order_id)           AS order_count,
    ROUND(SUM(f.total_amount)::numeric, 2) AS revenue,
    ROUND(AVG(f.total_amount)::numeric, 2) AS avg_order_value
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
WHERE f.status NOT IN ('cancelled')
GROUP BY d.full_date, d.year, d.month, d.month_name,
         d.day_of_week, d.day_name, d.is_weekend
ORDER BY d.full_date;

-- ---------- 2. Top products by revenue ----------
DROP VIEW IF EXISTS analytics.v_top_products CASCADE;
CREATE VIEW analytics.v_top_products AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.price_band,
    COUNT(DISTINCT f.order_id)              AS order_count,
    SUM(f.quantity)                          AS units_sold,
    ROUND(SUM(f.revenue_per_line)::numeric, 2) AS revenue,
    ROUND(AVG(f.margin_pct)::numeric, 2)      AS avg_margin_pct
FROM warehouse.fact_order_items f
JOIN warehouse.dim_products p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category, p.brand, p.price_band
ORDER BY revenue DESC;

-- ---------- 3. Customer segment performance ----------
DROP VIEW IF EXISTS analytics.v_customer_segments CASCADE;
CREATE VIEW analytics.v_customer_segments AS
SELECT
    c.segment,
    c.country,
    COUNT(DISTINCT c.customer_id)             AS customer_count,
    COUNT(DISTINCT f.order_id)                AS order_count,
    ROUND(SUM(f.total_amount)::numeric, 2)    AS revenue,
    ROUND(AVG(f.total_amount)::numeric, 2)    AS avg_order_value,
    ROUND((SUM(f.total_amount) / NULLIF(COUNT(DISTINCT c.customer_id), 0))::numeric, 2)
                                              AS revenue_per_customer
FROM warehouse.fact_orders f
JOIN warehouse.dim_customers c ON f.customer_key = c.customer_key
GROUP BY c.segment, c.country
ORDER BY revenue DESC;

-- ---------- 4. Payment success rate ----------
DROP VIEW IF EXISTS analytics.v_payment_success CASCADE;
CREATE VIEW analytics.v_payment_success AS
SELECT
    method,
    status,
    delay_bucket,
    COUNT(*)                                   AS payment_count,
    ROUND(SUM(amount)::numeric, 2)             AS total_amount,
    ROUND(AVG(payment_delay_hours)::numeric, 2) AS avg_delay_hours
FROM warehouse.dim_payments
GROUP BY method, status, delay_bucket
ORDER BY payment_count DESC;

-- ---------- 5. Inventory health ----------
DROP VIEW IF EXISTS analytics.v_inventory_health CASCADE;
CREATE VIEW analytics.v_inventory_health AS
SELECT
    warehouse,
    stock_status,
    COUNT(*)                                 AS sku_count,
    SUM(quantity_on_hand)                    AS total_units,
    SUM(CASE WHEN needs_reorder THEN 1 ELSE 0 END) AS reorder_alerts
FROM warehouse.dim_inventory
GROUP BY warehouse, stock_status
ORDER BY warehouse, stock_status;

-- ---------- 6. Category performance (bonus) ----------
DROP VIEW IF EXISTS analytics.v_category_performance CASCADE;
CREATE VIEW analytics.v_category_performance AS
SELECT
    p.category,
    COUNT(DISTINCT f.order_id)               AS order_count,
    SUM(f.quantity)                          AS units_sold,
    ROUND(SUM(f.revenue_per_line)::numeric, 2) AS revenue,
    ROUND(AVG(f.margin_pct)::numeric, 2)     AS avg_margin_pct
FROM warehouse.fact_order_items f
JOIN warehouse.dim_products p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY revenue DESC;

-- ---------- 7. Monthly revenue trend (bonus) ----------
DROP VIEW IF EXISTS analytics.v_monthly_revenue CASCADE;
CREATE VIEW analytics.v_monthly_revenue AS
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_id)                AS order_count,
    ROUND(SUM(f.total_amount)::numeric, 2)    AS revenue,
    ROUND(AVG(f.total_amount)::numeric, 2)    AS avg_order_value
FROM warehouse.fact_orders f
JOIN warehouse.dim_date d ON f.date_key = d.date_key
WHERE f.status NOT IN ('cancelled')
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;