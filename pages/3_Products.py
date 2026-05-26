import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

from decimal import Decimal
from datetime import datetime, date

from etl import calculate_quality_metrics, clean_data, prepare_data
from insights import create_business_insights, create_selectables, fmt_num, generate_selectable_insight, generate_selectable_full_insights
from Home import df_cleaned_tables, prep_data, selectables, insights, years

with st.sidebar:
    st.title("Daily Analytics")
    st.header("Settings")

    pay_method = st.selectbox(
        "Select Payment Method",
        tuple(["All"]+selectables['payment_methods']['payment_method'].tolist()),
        key='daily_pay'
    )

    store = st.selectbox(
        "Select Store",
        tuple(["All"]+selectables['stores']['store_name'].tolist()),
        key='daily_store'
    )

    year = st.selectbox(
        "Select Year",
        tuple(["All"]+years),
        key='daily_year'
    )
# st.write("This is will give you insights on some of the happenings")
if pay_method == "All":
    pay_method = None

if store == "Unizik Junction":
    store = 1
elif store == "Ziks Avenue":
    store = 2
elif store == "Ifite":
    store = 3
elif store == "Aroma Junction":
    store = 4
else:
    store = None

if year == "All":
    year = None
else:
    year = int(year)

changing_insights = generate_selectable_insight(prep_data, pay_method, store, year)
changing_full_insights = generate_selectable_full_insights(prep_data, pay_method, store, year)
insights = create_business_insights(prep_data)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True, vertical_alignment="bottom"):
            st.metric(f"Number of Products", value=f"{fmt_num(changing_full_insights['product_sales']['category'].nunique())}")
with col2:
    with st.container(border=True, vertical_alignment="bottom"):
        col_1, col_2 = st.columns(2)
        with col_1:
            st.metric(f"Average Order Value{"for {year}" if year else ''}", value=f"₦{fmt_num(changing_insights['average_order_value'])}")
        with col_2:
            st.markdown(
                f"<div style='height:100%; display:flex; align-items:flex-end; justify-content:flex-end; color:green; font-size:20px; font-weight:600;'>₦{fmt_num(insights['current_year_average_order_value'])}</div>",
                unsafe_allow_html=True
            )
# with st.container(border=True):
#     monthly_trend = st.toggle("Monthly Trend")
with st.container(border=True):
    st.header("Top Selling Products")
    by_sales_volume = st.toggle("By Sales Volume", key="product_sales_volume")
    category = st.toggle("By Category")
    fig3 = px.bar(
        changing_full_insights['product_sales'].head(10) if not category else changing_full_insights['product_sales'],
        x='total_revenue' if not by_sales_volume else 'transaction_count',
        y='product' if not category else 'category',
        labels={'product': '', 'total_revenue': ''},
        color_discrete_sequence=px.colors.qualitative.Pastel,
        category_orders={'category' if category else 'product': changing_full_insights['product_sales'].head(10)
                            .sort_values('total_revenue' if not by_sales_volume else 'transaction_count', ascending=False)[('product' if not category else 'category')]
                            .tolist()},
        color='product' if category else 'category',
        hover_data={'total_revenue': ':,', 'transaction_count': ':,', 'product': True, 'category': True},
        hover_name='product' if category else 'category'
    )
    fig3.update_layout(
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title='', showgrid=False, showline=False, zeroline=False, tickfont=dict(size=12)),
        yaxis=dict(title='', showgrid=False, showline=False, zeroline=False, tickfont=dict(size=12)),
        bargap=0.2,
    )
    fig3.update_traces(marker_line_width=0)
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
# st.subheader("By Sales Revenue")
# st.bar_chart(changing_full_insights['product_sales'], x='category', y='total_revenue', color="category")
# # # st.line_chart(insights['daily_sales'], x='date', y='total_revenue', color=insights['daily_sales']['date'].year)

# st.subheader("By Sales Volume")

# st.bar_chart(changing_full_insights['product_sales'], x='category', y='transaction_count', color="category")

# st.subheader("Active Daily Hours")

# st.line_chart(insights['hourly_pattern'], x='hour', y='order_count', color="green")


