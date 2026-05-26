import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

from decimal import Decimal
from datetime import datetime, date

from insights import create_business_insights, generate_selectable_full_insights, fmt_num, generate_selectable_insight
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

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True, vertical_alignment="bottom"):
        col_1, col_2 = st.columns(2)
        with col_1:
            st.metric(f"Total Revenue{"for {year}" if year else ''}", value=f"₦{fmt_num(changing_insights['yearly_sales']['total_revenue'].sum())}")
        with col_2:
            st.markdown(
                f"<div style='height:100%; display:flex; align-items:flex-end; justify-content:flex-end; color:green; font-size:20px; font-weight:600;'>₦{fmt_num(insights['current_year_sales']['total_revenue'].sum())}</div>",
                unsafe_allow_html=True
            )
with col2:
    with st.container(border=True, vertical_alignment="bottom"):
        col_1, col_2 = st.columns(2)
        with col_1:
            st.metric(f"Average Revenue{"for {year}" if year else ''}", value=f"₦{fmt_num(changing_insights['yearly_sales']['total_revenue'].mean())}")
        with col_2:
            st.markdown(
                f"<div style='height:100%; display:flex; align-items:flex-end; justify-content:flex-end; color:green; font-size:20px; font-weight:600;'>₦{fmt_num(insights['current_year_sales']['total_revenue'].mean())}</div>",
                unsafe_allow_html=True
            )
with col3:
    with st.container(border=True, vertical_alignment="bottom"):
        col_1, col_2 = st.columns(2)
        with col_1:
            st.metric(f"Total Discount{"for {year}" if year else ''}", value=f"₦{fmt_num(changing_insights['yearly_sales']['total_discount'].sum())}")
        with col_2:
            st.markdown(
                f"<div style='height:100%; display:flex; align-items:flex-end; justify-content:flex-end; color:green; font-size:20px; font-weight:600;'>₦{fmt_num(insights['current_year_sales']['total_discount'].sum())}</div>",
                unsafe_allow_html=True
            )


# # col1.metric(label="Total Revenue", value=f"₦{fmt_num(insights['daily_sales']['total_revenue'].sum())}", format="compact")
# col2.metric(label="Sales Volumne", value=f"{fmt_num(changing_insights['daily_sales']['transaction_count'].sum())}", format="compact")
# col3.metric(label="Average Daily Revenue", value=f"₦{fmt_num(changing_insights['daily_sales']['total_revenue'].mean())}")

# with st.container(border=True):
#     monthly_trend = st.toggle("Monthly Trend")

# st.bar_chart(changing_insights['yearly_sales'], x='year', y='total_revenue', color="year")
with st.container(border=True):
    st.header("Yearly Revenue Trend")
    fig1 = px.bar(
        changing_insights['yearly_sales'].assign(year_label=changing_insights['yearly_sales']['year'].astype(str)),
        x='year',
        y='total_revenue',
        labels={'year': '', 'total_revenue': 'Total Revenue', 'year_label': 'Year'},
        color='year_label',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig1.update_layout(
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title='Year', showgrid=False, showline=False, zeroline=False, tickfont=dict(size=12)),
        yaxis=dict(title='Total Revenue', showgrid=False, showline=False, zeroline=False, tickfont=dict(size=12)),
        bargap=0.2,
    )
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
                        
# st.line_chart(insights['daily_sales'], x='date', y='total_revenue', color=insights['daily_sales']['date'].year)

# st.subheader("By Days of the week")

# st.bar_chart(changing_insights['daily_sales_by_day'], x='day', y='total_revenue', color="day")

# st.subheader("Active Daily Hours")

# st.line_chart(changing_insights['hourly_pattern'], x='hour', y='order_count', color="green")


