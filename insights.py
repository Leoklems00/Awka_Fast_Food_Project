import pandas as pd

# ============================================
# CREATE BUSINESS INSIGHTS / AGGREGATIONS
# ============================================

def fmt_num(num):
    """
    Format number n into a compact form with M and K suffixes
    """
    n = float(num)
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}T"

    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{n}"


def create_selectables(df_tables):
    """Create aggregated views for Power BI or Streamlit dashboarding"""

    # tables
    # df_order_details = df_tables['order_details']
    df_orders = df_tables['orders']
    df_stores = df_tables['stores']
    # df_employees = df_tables['employees']
    # df_promotions = df_tables['promotions']
    # df_products = df_tables['products']
    
    selectables = {}

    # Payment method preference
    payment_methods = df_orders.groupby('payment_method').size().reset_index(name='transaction_count')
    payment_revenue = df_orders.groupby('payment_method')['total_amount_paid'].sum().reset_index(name='revenue')
    selectables['payment_methods'] = payment_methods.merge(payment_revenue, on='payment_method')

    # Available stores 
    selectables['stores'] = df_stores

    # Available Years 
    years = df_orders['order_datetime'].dt.year.unique()
    # years.columns = ['year']
    selectables['years'] = years
    
    return selectables

def selectable_full_insights_setup(df_tables, params:bool = None):
    
    # tables
    df_full = df_tables['full_table']
    
    insights = {}

    # Sales by product with category
    # Check if params is a single boolean/None value, or if it is a valid pandas Series/array
    if params is not None and params is not False:
        product_sales = df_full[params].groupby(['category_name', 'product_name']).agg({
            'net_amount': ['sum', 'mean'],
            'order_detail_id': 'count'
        }).round(2).reset_index()
    else:
        product_sales = df_full.groupby(['category_name', 'product_name']).agg({
            'net_amount': ['sum', 'mean'],
            'order_detail_id': 'count'
        }).round(2).reset_index()

    product_sales.columns = ['category', 'product', 'total_revenue', 'avg_transaction_value', 'transaction_count']
    insights['product_sales'] = product_sales
    
    return insights

def generate_selectable_full_insights(df_tables, pay_method:str = "All", store_id:int = None, year = None):
    """Create aggregated views for Power BI or Streamlit dashboarding"""
    df_full = df_tables['full_table']
    
    insights = {}

    if pay_method in ["All", None] and store_id == None and year in ["All", None]: # If nothing is selected
        params = None
        insights = selectable_full_insights_setup(df_tables, params)

    elif store_id == None and year in ["All", None]: # If only payment method s selected
        params = df_full['payment_method'] == pay_method
        insights = selectable_full_insights_setup(df_tables, params)
    elif pay_method == None and year == None: # If only store is selected but not payment method or year
        params = df_full['store_id'] == store_id
        insights = selectable_full_insights_setup(df_tables, params)
        
    elif pay_method == None and store_id == None: # If only year is selected but not payment method or store
        params = df_full['year'] == year
        insights = selectable_full_insights_setup(df_tables, params)
        
    elif year in ["All", None]: # If payment method and store are selected but not year
        params = (df_full['payment_method'] == pay_method) & (df_full['store_id'] == store_id)
        insights = selectable_full_insights_setup(df_tables, params)
        
    elif store_id == None: # If payment method and year are selected but not store
        params = (df_full['payment_method'] == pay_method) & \
                                (df_full['year'] == year)
        insights = selectable_full_insights_setup(df_tables, params)
        
    elif pay_method == None: # If store and year are selected but not payment method
        params = (df_full['store_id'] == store_id) & \
                                (df_full['year'] == year)
        insights = selectable_full_insights_setup(df_tables, params)
        
    else:
        params = (df_full['payment_method'] == pay_method) & \
                                (df_full['store_id'] == store_id) & \
                                (df_full['year'] == year)
        insights = selectable_full_insights_setup(df_tables, params)
    
    return insights



def selectable_insights_setup(df_tables, params:bool):
    
    # tables
    df_order_details = df_tables['order_details']
    df_orders = df_tables['orders']
    df_stores = df_tables['stores']
    df_employees = df_tables['employees']
    df_full = df_tables['full_table']
    df_products = df_tables['products']
    
    insights = {}

    # Daily sales summary
    daily_sales = df_orders[params].groupby(df_orders['order_datetime'].dt.date).agg({
        'total_amount_paid': ['sum', 'mean'],
        'transaction_id': 'count'
    }).round(2).reset_index()
    daily_sales.columns = ['date', 'total_revenue', 'avg_transaction', 'transaction_count']
    insights['daily_sales'] = daily_sales
    
    # Yearly sales summary order_id 
    yearly_sales = df_orders[params ].groupby(df_orders['order_datetime'].dt.year).agg({
        'total_amount_paid': ['sum', 'mean'],
        'order_id': 'count',
        'discount_amount': ['sum', 'count']
    }).round(2).reset_index()
    yearly_sales.columns = ['year', 'total_revenue', 'avg_transaction', 'transaction_count', 'total_discount', 'discount_count']
    insights['yearly_sales'] = yearly_sales
        
    # Average order value
    average_order_value = df_orders[params ]['total_amount_paid'].mean()/df_orders[params ]['order_id'].nunique()
    insights['average_order_value'] = average_order_value
    
    # Sales by stores
    store_sales = df_orders[params ].groupby('store_id').agg({
        'total_amount_paid': 'sum',
        'transaction_id': 'count'
    }).round(2).reset_index()
    store_sales.columns = ['store_id', 'total_revenue', 'transaction_count']
    store_sales = pd.merge(store_sales, df_stores[['store_id', 'store_name']], on='store_id').drop(['store_id'], axis=1)
    insights['store_sales'] = store_sales
    
    # Daily sales by Day Of The Week
    daily_sales_by_day = df_orders[params ].groupby([df_orders.order_datetime.dt.day_name().rename("day")])\
        .agg(revenue = ("total_amount_paid",'sum'), count = ("order_id", "count")).reset_index()
    daily_sales_by_day.columns = ['day', 'total_revenue', 'order_count']
    
    insights['daily_sales_by_day'] = daily_sales_by_day

    # Hourly sales pattern
    df_orders['hour'] = pd.to_datetime(df_orders['order_datetime']).dt.hour
    hourly_pattern = df_orders[params ].groupby('hour').agg({
        'total_amount_paid': 'sum',
        'transaction_id': 'count'
    }).reset_index()
    hourly_pattern.columns = ['hour', 'total_revenue', 'order_count']
    insights['hourly_pattern'] = hourly_pattern

    # Current Year monthly order
    current_monthly_sales = df_orders[params ].groupby(df_orders['order_datetime'].dt.month).agg({
        'total_amount_paid': ['sum', 'mean'],
        'transaction_id': 'count'
    }).round(2).reset_index()
    current_monthly_sales.columns = ['month', 'total_revenue', 'avg_transaction', 'transaction_count']
    current_monthly_sales['month_name'] = pd.to_datetime(current_monthly_sales['month'], format='%m').dt.month_name()
    insights['current_monthly_sales'] = current_monthly_sales

    return insights

def generate_selectable_insight(df_tables, pay_method:str = "All", store_id:int = None, year = None):
    """Create aggregated views for Power BI or Streamlit dashboarding"""

    # tables
    df_order_details = df_tables['order_details']
    df_orders = df_tables['orders']
    df_stores = df_tables['stores']
    df_employees = df_tables['employees']
    df_full = df_tables['full_table']
    df_products = df_tables['products']
    
    insights = {}

    if pay_method in ["All", None] and store_id == None and year in ["All", None]: # If nothing is selected

        current_year = df_orders['order_datetime'].dt.year.max()
    
        # Daily sales summary
        daily_sales = df_orders.groupby(df_orders['order_datetime'].dt.date).agg({
            'total_amount_paid': ['sum', 'mean'],
            'transaction_id': 'count'
        }).round(2).reset_index()
        daily_sales.columns = ['date', 'total_revenue', 'avg_transaction', 'transaction_count']
        insights['daily_sales'] = daily_sales
        
        # Yearly sales summary order_id
        yearly_sales = df_orders.groupby(df_orders['order_datetime'].dt.year).agg({
            'total_amount_paid': ['sum', 'mean'],
            'order_id': 'count',
            'discount_amount': ['sum', 'count']
        }).round(2).reset_index()
        yearly_sales.columns = ['year', 'total_revenue', 'avg_transaction', 'transaction_count', 'total_discount', 'discount_count']
        insights['yearly_sales'] = yearly_sales
        
        # Average order value
        average_order_value = df_orders['total_amount_paid'].mean()/df_orders['order_id'].nunique()
        insights['average_order_value'] = average_order_value
        
        # Sales by product category
        # category_sales = df_full.groupby('category_name').agg({
        #     'net_amount': ['sum', 'mean'],
        #     'order_detail_id': 'count'
        # }).round(2).reset_index()
        # category_sales.columns = ['category', 'total_revenue', 'avg_transaction_value', 'transaction_count']
        # insights['category_sales'] = category_sales
        
        # Sales by stores
        store_sales = df_orders.groupby('store_id').agg({
            'total_amount_paid': 'sum',
            'transaction_id': 'count'
        }).round(2).reset_index()
        store_sales.columns = ['store_id', 'total_revenue', 'transaction_count']
        store_sales = pd.merge(store_sales, df_stores[['store_id', 'store_name']], on='store_id').drop(['store_id'], axis=1)
        insights['store_sales'] = store_sales
        
        # Daily sales by Day Of The Week
        daily_sales_by_day = df_orders.groupby([df_orders.order_datetime.dt.day_name().rename("day")])\
            .agg(revenue = ("total_amount_paid",'sum'), count = ("order_id", "count")).reset_index()
        daily_sales_by_day.columns = ['day', 'total_revenue', 'order_count']
        
        insights['daily_sales_by_day'] = daily_sales_by_day
    
        # Hourly sales pattern
        df_orders['hour'] = pd.to_datetime(df_orders['order_datetime']).dt.hour
        hourly_pattern = df_orders.groupby('hour').agg({
            'total_amount_paid': 'sum',
            'order_id': 'count'
        }).reset_index()
        hourly_pattern.columns = ['hour', 'total_revenue', 'order_count']
        insights['hourly_pattern'] = hourly_pattern

        # Current Year monthly order
        current_monthly_sales = df_orders[df_orders['year'] == current_year].groupby(df_orders['order_datetime'].dt.month).agg({
            'total_amount_paid': ['sum', 'mean'],
            'transaction_id': 'count'
        }).round(2).reset_index()
        current_monthly_sales.columns = ['month', 'total_revenue', 'avg_transaction', 'transaction_count']
        current_monthly_sales['month_name'] = pd.to_datetime(current_monthly_sales['month'], format='%m').dt.month_name()
        insights['current_monthly_sales'] = current_monthly_sales

    elif store_id == None and year in ["All", None]: # If only payment method s selected
        params = df_orders['payment_method'] == pay_method
        insights = selectable_insights_setup(df_tables, params)
    elif pay_method == None and year == None: # If only store is selected but not payment method or year
        params = df_orders['store_id'] == store_id
        insights = selectable_insights_setup(df_tables, params)
        
    elif pay_method == None and store_id == None: # If only year is selected but not payment method or store
        params = df_orders['year'] == year
        insights = selectable_insights_setup(df_tables, params)
        
    elif year in ["All", None]: # If payment method and store are selected but not year
        params = (df_orders['payment_method'] == pay_method) & (df_orders['store_id'] == store_id)
        insights = selectable_insights_setup(df_tables, params)
        
    elif store_id == None: # If payment method and year are selected but not store
        params = (df_orders['payment_method'] == pay_method) & \
                                (df_orders['year'] == year)
        insights = selectable_insights_setup(df_tables, params)
        
    elif pay_method == None: # If store and year are selected but not payment method
        params = (df_orders['store_id'] == store_id) & \
                                (df_orders['year'] == year)
        insights = selectable_insights_setup(df_tables, params)
        
    else:
        params = (df_orders['payment_method'] == pay_method) & \
                                (df_orders['store_id'] == store_id) & \
                                (df_orders['year'] == year)
        insights = selectable_insights_setup(df_tables, params)
    
    return insights



def create_business_insights(df_tables):
    """Create aggregated views for Power BI or Streamlit dashboarding"""

    # tables
    df_order_details = df_tables['order_details']
    df_orders = df_tables['orders']
    df_stores = df_tables['stores']
    df_employees = df_tables['employees']
    df_promotions = df_tables['promotions']
    df_products = df_tables['products']
    
    insights = {}   

    current_year = df_orders['order_datetime'].dt.year.max()
    previous_year = df_orders['order_datetime'].dt.year.max() -1
    
    # Current year order
    current_year_sales = df_orders[df_orders['year'] == current_year].groupby(df_orders['order_datetime'].dt.date).agg({
        'total_amount_paid': ['sum', 'mean'],
        'transaction_id': 'count',
        'discount_amount': ['sum', 'count']
    }).round(2).reset_index()
    current_year_sales.columns = ['date', 'total_revenue', 'avg_transaction', 'transaction_count', 'total_discount', 'discount_count']
    insights['current_year_sales'] = current_year_sales

    # Previous year order
    previous_year_sales = df_orders[df_orders['year'] == previous_year].groupby(df_orders['order_datetime'].dt.date).agg({
        'total_amount_paid': ['sum', 'mean'],
        'transaction_id': 'count',
        'discount_amount': ['sum', 'count']
    }).round(2).reset_index()
    previous_year_sales.columns = ['date', 'total_revenue', 'avg_transaction', 'transaction_count', 'total_discount', 'discount_count']
    insights['previous_year_sales'] = previous_year_sales
    
    # Yearly sales summary order_id
    yearly_sales = df_orders.groupby(df_orders['order_datetime'].dt.year).agg({
        'total_amount_paid': ['sum', 'mean'],
        'order_id': 'count',
        'discount_amount': ['sum', 'count']
    }).round(2).reset_index()
    yearly_sales.columns = ['year', 'total_revenue', 'avg_transaction', 'transaction_count', 'total_discount', 'discount_count']
    insights['yearly_sales'] = yearly_sales
        
    # Average order value
    current_year_average_order_value = df_orders[df_orders['year'] == current_year]['total_amount_paid'].mean()/df_orders[df_orders['year'] == current_year]['order_id'].nunique()
    insights['current_year_average_order_value'] = current_year_average_order_value
    
    # # Segment customers
    # customer_agg['customer_segment'] = pd.cut(
    #     customer_agg['total_spend'],
    #     bins=[0, 100, 500, 2000, float('inf')],
    #     labels=['Low Value', 'Medium Value', 'High Value', 'VIP']
    # )
    # insights['customer_segments'] = customer_agg
    
    # Fraud summary
    # if 'is_fraudulent' in df_clean.columns:
    #     fraud_summary = pd.DataFrame({
    #         'total_transactions': [len(df_clean)],
    #         'fraud_transactions': [int(df_clean['is_fraudulent'].sum())],
    #         'fraud_rate': [round(df_clean['is_fraudulent'].mean() * 100, 2)],
    #         'fraud_amount': [float(df_clean[df_clean['is_fraudulent'] == 1]['amount'].sum())]
    #     })
    #     insights['fraud_summary'] = fraud_summary
    
    # Device type analysis
    # device_analysis = df_clean.groupby('device_type').agg({
    #     'amount': ['sum', 'mean'],
    #     'transaction_id': 'count'
    # }).round(2).reset_index()
    # device_analysis.columns = ['device_type', 'total_revenue', 'avg_transaction', 'transaction_count']
    # insights['device_analysis'] = device_analysis
    
    return insights
