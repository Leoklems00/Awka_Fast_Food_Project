import pandas as pd
import numpy as np
import streamlit as st

from decimal import Decimal
from datetime import datetime, date

from etl import calculate_quality_metrics, clean_data, prepare_data
from insights import create_business_insights, create_selectables, fmt_num
from base import df_cleaned_tables, prep_data, selectables, insights

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
        tuple(["All"]+selectables['years'].tolist()),
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

insights = create_business_insights(prep_data, pay_method, store, year)

col1, col2, col3 = st.columns(3)
col1.metric(label="Total Revenue", value=f"₦{fmt_num(insights['daily_sales']['total_revenue'].sum())}", format="compact")
col2.metric(label="Sales Volumne", value=f"{fmt_num(insights['daily_sales']['transaction_count'].sum())}", format="compact")
col3.metric(label="Average Daily Revenue", value=f"₦{fmt_num(insights['daily_sales']['total_revenue'].mean())}")

with st.container(border=True):
    monthly_trend = st.toggle("Monthly Trend")

st.line_chart(insights['yearly_sales'], x='year', y='total_revenue', color="green")
# st.line_chart(insights['daily_sales'], x='date', y='total_revenue', color=insights['daily_sales']['date'].year)

st.subheader("By Days of the week")

st.bar_chart(insights['daily_sales_by_day'], x='day', y='total_revenue', color="day")

st.subheader("Active Daily Hours")

st.line_chart(insights['hourly_pattern'], x='hour', y='order_count', color="green")


