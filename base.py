

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import os
import re

from sqlalchemy import create_engine
import psycopg2 as pg2
import mysql.connector as msc

from decimal import Decimal
from datetime import datetime, date

from etl import calculate_quality_metrics, clean_data, prepare_data
from insights import create_business_insights, create_selectables, fmt_num

from dotenv import load_dotenv

load_dotenv()

pg_user = os.environ.get('pg_user')
my_user = os.environ.get('my_user')
pg_password = os.environ.get('pg_password')
my_password = os.environ.get('my_password')

pg_engine = create_engine(f'postgresql://{pg_user}:{pg_password}@localhost/awka_fastfood')

pg_conn = pg2.connect(database='awka_fastfood', user= pg_user, password=pg_password, port=5432)

cur = pg_conn.cursor()

if pg_user and  pg_password:

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
    year = None
else:
    year = int(year)

insights = create_business_insights(prep_data, pay_method, store, year)

col1, col2, col3 = st.columns(3)
col1.metric(label="Average Yearly Revenue", value=f"₦{fmt_num(insights['yearly_sales']['total_revenue'].mean())}")
col2.metric(label="Average Yearly Sales Volumne", value=f"{fmt_num(insights['yearly_sales']['transaction_count'].mean())}", format="compact")
col3.metric(label="Number of Years", value=f"{insights['yearly_sales']['year'].nunique():,.0f}")

st.bar_chart(insights['yearly_sales'], x='year', y='total_revenue')
