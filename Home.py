

import pandas as pd
import numpy as np

# import matplotlib.pyplot as plt
# import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")

import os
# import re

from sqlalchemy import create_engine
import psycopg2 as pg2
import mysql.connector as msc

# from decimal import Decimal
from datetime import datetime, date

from etl import calculate_quality_metrics, clean_data, prepare_data
from insights import create_business_insights, create_selectables, fmt_num, generate_selectable_insight, generate_selectable_full_insights

from dotenv import load_dotenv

load_dotenv()

pg_user = os.environ.get('pg_user')
my_user = os.environ.get('my_user')
pg_password = os.environ.get('pg_password')
my_password = os.environ.get('my_password')

if pg_user and  pg_password:

    pg_engine = create_engine(f'postgresql://{pg_user}:{pg_password}@localhost/awka_fastfood')

    pg_conn = pg2.connect(database='awka_fastfood', user= pg_user, password=pg_password, port=5432)

    cur = pg_conn.cursor()

    cur.execute(
        """
            select * 
            from information_schema.tables
            where table_schema ='public';
        """
    )
    rows = cur.fetchall()

    tables = {}
    for row in rows:
        if row[2] not in tables.keys():
            table_obj = pd.read_sql(row[2], con=pg_engine)
            tables[row[2]] = table_obj
else:
    tables = {}
    table_names = ['subcategories', 'products', 'categories', 'stores', 'employees', 'promotions', 'orders', 'order_details']
    for name in table_names:
        table_obj = pd.read_csv(f"data/{name}.csv")
        tables[name] = table_obj

result_quality_check = {}
result_remediation_log = {}
df_cleaned_tables = {}
for name,table in tables.items():
    quality_metrics = calculate_quality_metrics(table)
    remediation = clean_data(table, quality_metrics, tables)
    result_quality_check[f'{name}'] = quality_metrics
    if remediation[1]:
        result_remediation_log[f'{name}'] = remediation[1]
    df_cleaned_tables[f'{name}'] = remediation[0]

prep_data = prepare_data(df_cleaned_tables)

selectables = create_selectables(prep_data)

with st.sidebar:
    st.title("Executive Dashboard")
    st.header("Settings")

    pay_method = st.selectbox(
        "Select Payment Method",
        tuple(["All"]+selectables['payment_methods']['payment_method'].tolist()),
        key='base_pay'
    )

    store = st.selectbox(
        "Select Store",
        tuple(["All"]+selectables['stores']['store_name'].tolist()),
        key='base_store'
    )

    year = st.selectbox(
        "Select Year",
        tuple(["All"]+selectables['years'].tolist()),
        key='base_year'
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
    year = datetime.now().year
else:
    year = int(year)

changing_insights = generate_selectable_insight(prep_data, pay_method, store, year)
changing_full_insights = generate_selectable_full_insights(prep_data, pay_method, store, year)
insights = create_business_insights(prep_data)

col1, col2 = st.columns(2)
deltas = {
    "revenue": [insights['current_year_sales']['total_revenue'].sum(), insights['previous_year_sales']['total_revenue'].sum()],
    "volume": [insights['current_year_sales']['transaction_count'].sum(), insights['previous_year_sales']['transaction_count'].sum()]
}
def guage_setup(value, range_, color=None):

    # progress ratio toward the upper range value
    target = range_[1] if len(range_) >= 2 else None
    progress = 0.0
    if target and target > 0:
        progress = min(max(value / target, 0.0), 1.0)

    # Map 0%..80% to red->green; above 80% stays green
    color_scale = min(progress / 0.8, 1.0) if target else 0.0
    gauge_color = f"rgb({int(255 * (1 - color_scale))},{int(255 * color_scale)},0)"

    # Construct a clean circular ring gauge (Non-Speedometer)
    fig = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = value,
        number = {
            'prefix': "₦", 
            'font': {'color': gauge_color}
        },
        gauge = {
            'shape': "angular",
            'axis': {'range': range_, 'tickprefix': "₦"},
            'bar': {'color': gauge_color, 'thickness': 1.0},
            'bgcolor': "#e5ecf6",
            'borderwidth': 0,
            'steps': [
                {'range': [i, i+1],
                'color': f"rgba({int(255 - i*2.55)},  {int(i*2.55)}, 0, 1)"}
                for i in range(100)
            ],
        }
    ))

    # Clean layout frame adjustments
    fig.update_layout(
        height=150,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    return fig

    # 5. Render side-by-side metrics and the gauge plot "#1f77b4"
    col1, col2 = st.columns([1, 2])

# with col1:
#     st.markdown("<br><br>", unsafe_allow_html=True)
#     st.metric(label="Funds Expended", value=f"${current_spend:,}")
#     st.metric(label="Allocated Limit", value=f"${total_budget:,}")

target = 1000_000_000

# with col2:
#     st.plotly_chart(fig, use_container_width=True)

with col1:
    with st.container(border=True, width='content', vertical_alignment="center"):
        col_1, col_2 = st.columns([1, 2])
        with col_1:
            delta = deltas["revenue"][0] - deltas["revenue"][1]
            delta_percent = (delta/deltas["revenue"][1]) * 100
            delta_str = f"{delta:+,.0f} ({delta_percent:+.2f}%)"
            st.metric("Curent Yearly Revenue", value=f"₦{fmt_num(insights['current_year_sales']['total_revenue'].sum())}", delta=delta_str)
            fig1 = px.bar(insights['yearly_sales'], x='year', y='total_revenue')
            # Hide axis titles
            fig1.update_layout(
                xaxis_title = None,
                yaxis_title = None, 
                height=30,
                margin=dict(l=0, r=10, t=0, b=0),
                plot_bgcolor = "rgba(0,0,0,0)",
                paper_bgcolor = "rgba(0,0,0,0)"
            )
            # Hide axis values/tick labels
            fig1.update_xaxes(showticklabels=False, showline=False, showgrid=False)
            fig1.update_yaxes(showticklabels=False, showline=False, showgrid=False)

            # set bar width in percentage of available space
            fig1.update_traces(width=0.8, marker_color = "#1f77b4")
            st.plotly_chart(fig1, width="content", config={"displayModeBar":False})
        with col_2:
            st.plotly_chart(guage_setup(deltas["revenue"][0], range_=[0, 1_200_000_000 if pg_user else 450_000_000], color="#1f77b4"), width='content')



with col2:
    with st.container(border=True, width='content', height='content'):
        col_1, col_2 = st.columns([1, 2])
        with col_1:
            delta = deltas["volume"][0] - deltas["volume"][1]
            delta_percent = (delta/deltas["volume"][1]) * 100
            delta_str = f"{delta:+,.0f} ({delta_percent:+.2f}%)"
            st.metric("Curent Year Sales Volume", value=f"₦{fmt_num(insights['current_year_sales']['transaction_count'].sum())}", delta=delta_str)
            fig1 = px.bar(insights['yearly_sales'], x='year', y='transaction_count')
            # Hide axis titles
            fig1.update_layout(
                xaxis_title = None,
                yaxis_title = None, 
                height=30,
                margin=dict(l=0, r=10, t=0, b=0),
                plot_bgcolor = "rgba(0,0,0,0)",
                paper_bgcolor = "rgba(0,0,0,0)"
            )
            # Hide axis values/tick labels
            fig1.update_xaxes(showticklabels=False, showline=False, showgrid=False)
            fig1.update_yaxes(showticklabels=False, showline=False, showgrid=False)

            # set bar width in percentage of available space
            fig1.update_traces(width=0.8, marker_color = "#1f77b4")
            st.plotly_chart(fig1, width="content", config={"displayModeBar":False})
            # st.bar_chart(changing_insights['yearly_sales'], x='year', y='transaction_count', height=50)
        with col_2:
            st.plotly_chart(guage_setup(deltas["volume"][0], range_=[0, 50_000 if pg_user else 20_000], color="#1fb41f"))
# col1.metric(label="Curent Yearly Revenue", value=f"₦{fmt_num(insights['current_year_sales']['total_revenue'].sum())}")
# col2.metric(label="Average Yearly Sales Volumne", value=f"{fmt_num(changing_insights['yearly_sales']['transaction_count'].mean())}", format="compact")
# col3.metric(label="Number of Years", value=f"{changing_insights['yearly_sales']['year'].nunique():,.0f}")

with st.container(border=True):
    by_sales_volume = st.toggle("By Sales Volume")

viz_col1, viz_col2 = st.columns(2)
with viz_col1:
    with st.container():

        st.header(f"Monthly {('Revenue' if not by_sales_volume else 'Sales Volume')} Trend for {year if year else date.today().year}")
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        fig2 = px.bar(
            changing_insights['current_monthly_sales'],
            x='month_name',
            y='total_revenue' if not by_sales_volume else 'transaction_count',
            category_orders={'month_name': month_order},
            labels={'month_name': '', 'total_revenue': ''},
            color_discrete_sequence=['#636EFA']
        )
        fig2.update_layout(
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(title='', showgrid=False, showline=False, zeroline=False, tickfont=dict(size=12)),
            yaxis=dict(title='', showgrid=False, showline=False, zeroline=False, tickfont=dict(size=12)),
            bargap=0.2,
        )
        fig2.update_traces(marker_line_width=0)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

with viz_col2:
    with st.container():
        st.header(f"Product Sales Trend for {year if year else date.today().year} ({'Volume' if by_sales_volume else 'Revenue'})")
        category = st.toggle("By Category")
        fig3 = px.bar(
            changing_full_insights['product_sales'],
            x='total_revenue' if not by_sales_volume else 'transaction_count',
            y='product' if not category else 'category',
            labels={'product': '', 'total_revenue': ''},
            color_discrete_sequence=px.colors.qualitative.Pastel,
            category_orders={'product' if not category else 'category': changing_full_insights['product_sales']
                             .sort_values('total_revenue' if not by_sales_volume else 'transaction_count', ascending=False)[('product' if not category else 'category')]
                             .tolist()},
            color='product' if category else 'category',
            hover_name=f"{'product' if category else 'category'}",
            # hover_data=f"{'total_revenue' if not by_sales_volume else 'transaction_count'}"
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
