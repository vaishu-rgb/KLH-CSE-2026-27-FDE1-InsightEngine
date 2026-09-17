"""
InsightEngine — Business Intelligence Dashboard.

Run:
    streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analytics.insights import (
    headline_kpis, daily_revenue, monthly_revenue, top_products,
    category_performance, customer_segments, payment_success, inventory_health,
)

# ============================================================
# Page config + theme
# ============================================================
st.set_page_config(
    page_title="InsightEngine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        border-radius: 10px;
        padding: 18px 20px;
        color: white;
    }
    .kpi-label { font-size: 0.85rem; opacity: 0.85; margin-bottom: 6px; }
    .kpi-value { font-size: 1.6rem; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Cached data loaders
# ============================================================
@st.cache_data(ttl=60, show_spinner=False)
def load_kpis():
    return headline_kpis()

@st.cache_data(ttl=60, show_spinner=False)
def load_daily(days: int):
    return daily_revenue(days).sort_values("full_date")

@st.cache_data(ttl=60, show_spinner=False)
def load_monthly():
    return monthly_revenue()

@st.cache_data(ttl=60, show_spinner=False)
def load_top_products(limit: int):
    return top_products(limit)

@st.cache_data(ttl=60, show_spinner=False)
def load_categories():
    return category_performance()

@st.cache_data(ttl=60, show_spinner=False)
def load_segments():
    return customer_segments()

@st.cache_data(ttl=60, show_spinner=False)
def load_payments():
    return payment_success()

@st.cache_data(ttl=60, show_spinner=False)
def load_inventory():
    return inventory_health()


# ============================================================
# Sidebar
# ============================================================
st.sidebar.title("📊 InsightEngine")
st.sidebar.caption("End-to-end Data Engineering Platform")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Overview", "👥 Customers", "📦 Products", "⚙️ Operations"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Stack**  \n"
    "Python · Pandas · PostgreSQL  \n"
    "Kafka · PySpark · Airflow · Streamlit"
)

if st.sidebar.button("🔄 Refresh data"):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# Helper: KPI card
# ============================================================
def kpi_card(label: str, value: str):
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# Page: OVERVIEW
# ============================================================
if page == "🏠 Overview":
    st.title("Business Overview")
    st.caption("Headline metrics and revenue trends")

    kpis = load_kpis()
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Total Revenue", f"${kpis['total_revenue']:,.0f}")
    with c2: kpi_card("Total Orders", f"{int(kpis['total_orders']):,}")
    with c3: kpi_card("Customers", f"{int(kpis['total_customers']):,}")
    with c4: kpi_card("Products", f"{int(kpis['total_products']):,}")
    with c5: kpi_card("Avg Order Value", f"${kpis['avg_order_value']:,.2f}")

    st.markdown("### Revenue trend")
    col1, col2 = st.columns([2, 1])
    with col1:
        days = st.slider("Days to show", 30, 365, 90, step=15, key="trend_days")
        daily = load_daily(days)
        fig = px.area(
            daily, x="full_date", y="revenue",
            title=f"Daily revenue (last {days} days)",
            labels={"full_date": "", "revenue": "Revenue ($)"},
        )
        fig.update_traces(line_color="#2c5282")
        fig.update_layout(height=350, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        monthly = load_monthly()
        fig = px.bar(
            monthly, x="month_name", y="revenue",
            title="Monthly revenue",
            labels={"month_name": "", "revenue": "Revenue ($)"},
            color="revenue", color_continuous_scale="Blues",
        )
        fig.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                          margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Category performance")
    cats = load_categories()
    fig = px.bar(
        cats.sort_values("revenue", ascending=True),
        x="revenue", y="category", orientation="h",
        color="avg_margin_pct", color_continuous_scale="Viridis",
        labels={"revenue": "Revenue ($)", "category": "", "avg_margin_pct": "Margin %"},
        title="Revenue by category (color = avg margin %)",
    )
    fig.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# Page: CUSTOMERS
# ============================================================
elif page == "👥 Customers":
    st.title("Customer Analytics")
    st.caption("Segment performance and geographic distribution")

    segs = load_segments()

    # ---- Segment aggregates ----
    seg_agg = (segs.groupby("segment", as_index=False)
                   .agg(customers=("customer_count", "sum"),
                        orders=("order_count", "sum"),
                        revenue=("revenue", "sum"))
                   .sort_values("revenue", ascending=False))

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            seg_agg, names="segment", values="revenue",
            title="Revenue share by segment", hole=0.4,
        )
        fig.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            seg_agg, x="segment", y="revenue",
            title="Revenue by segment", text_auto=".2s",
            color="segment",
        )
        fig.update_layout(height=380, showlegend=False,
                          margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Top countries by revenue")
    country_agg = (segs.groupby("country", as_index=False)
                        .agg(customers=("customer_count", "sum"),
                             orders=("order_count", "sum"),
                             revenue=("revenue", "sum"),
                             rev_per_cust=("revenue_per_customer", "mean"))
                        .sort_values("revenue", ascending=False))
    fig = px.bar(
        country_agg, x="country", y="revenue", color="segment" if False else None,
        text_auto=".2s", title="Revenue by country",
    )
    fig.update_layout(height=350, margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Segment × country breakdown")
    st.dataframe(
        segs.style.format({
            "revenue": "${:,.0f}",
            "avg_order_value": "${:,.2f}",
            "revenue_per_customer": "${:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Page: PRODUCTS
# ============================================================
elif page == "📦 Products":
    st.title("Product Analytics")
    st.caption("Top sellers, category performance, and pricing bands")

    top_n = st.slider("How many top products?", 5, 50, 15, step=5)
    prods = load_top_products(top_n)

    st.markdown(f"### Top {top_n} products by revenue")
    fig = px.bar(
        prods.iloc[::-1],
        x="revenue", y="product_name", orientation="h",
        color="category",
        labels={"revenue": "Revenue ($)", "product_name": "", "category": "Category"},
        title=None,
    )
    fig.update_layout(height=max(350, top_n * 22), margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Price band performance")
    cats = load_categories()
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            cats, x="category", y="avg_margin_pct",
            color="avg_margin_pct", color_continuous_scale="Greens",
            title="Average margin % by category", text_auto=".1f",
        )
        fig.update_layout(height=380, showlegend=False, coloraxis_showscale=False,
                          margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            cats, x="units_sold", y="revenue",
            size="order_count", color="category",
            title="Volume vs revenue by category",
            labels={"units_sold": "Units sold", "revenue": "Revenue ($)"},
        )
        fig.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Category table")
    st.dataframe(
        cats.style.format({
            "revenue": "${:,.0f}",
            "avg_margin_pct": "{:.1f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# Page: OPERATIONS
# ============================================================
elif page == "⚙️ Operations":
    st.title("Operations")
    st.caption("Payment success, delays, and inventory health")

    pays = load_payments()
    inv = load_inventory()

    # ---- Payment method breakdown ----
    method_agg = (pays.groupby("method", as_index=False)
                      .agg(payment_count=("payment_count", "sum"),
                           total_amount=("total_amount", "sum"))
                      .sort_values("payment_count", ascending=False))

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            method_agg, names="method", values="payment_count",
            title="Payment count by method", hole=0.4,
        )
        fig.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Delay bucket distribution
        delay_agg = (pays.groupby("delay_bucket", as_index=False)
                         .agg(payment_count=("payment_count", "sum")))
        fig = px.bar(
            delay_agg, x="delay_bucket", y="payment_count",
            title="Payment delay distribution", text_auto=".2s",
            color="delay_bucket",
        )
        fig.update_layout(height=380, showlegend=False,
                          margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Payment status summary")
    status_agg = (pays.groupby("status", as_index=False)
                      .agg(payments=("payment_count", "sum"),
                           amount=("total_amount", "sum"),
                           avg_delay=("avg_delay_hours", "mean")))
    st.dataframe(
        status_agg.style.format({
            "amount": "${:,.0f}",
            "avg_delay": "{:.2f} hrs",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ---- Inventory ----
    st.markdown("### Inventory health")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            inv, x="warehouse", y="sku_count", color="stock_status",
            title="SKU count by warehouse and status",
            labels={"sku_count": "SKUs", "warehouse": ""},
            barmode="group",
        )
        fig.update_layout(height=380, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        alerts = (inv.groupby("warehouse", as_index=False)
                     .agg(reorder_alerts=("reorder_alerts", "sum"))
                     .sort_values("reorder_alerts", ascending=False))
        fig = px.bar(
            alerts, x="warehouse", y="reorder_alerts",
            title="Reorder alerts by warehouse", text_auto=True,
            color="reorder_alerts", color_continuous_scale="Reds",
        )
        fig.update_layout(height=380, showlegend=False, coloraxis_showscale=False,
                          margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(inv, use_container_width=True, hide_index=True)


# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.caption("InsightEngine · Data warehouse: `insightengine_dw` · "
           "Source: 7 analytics views · Cached 60s")