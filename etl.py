import pandas as pd
import numpy as np

from datetime import datetime, date


# Quality thresholds
QUALITY_THRESHOLDS = {
    'completeness': 95.0,  # Minimum 95% non-null
    'uniqueness': 99.0,     # Minimum 99% unique for IDs
    'validity': 90.0,       # Minimum 90% valid values
    'quality_score': 85.0   # Minimum overall quality score
}


# ============================================
# DATA QUALITY CALCULATIONS
# ============================================

def calculate_quality_metrics(df):
    """Calculate comprehensive data quality metrics"""
    
    metrics = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'timestamp': datetime.now().isoformat()
    }
    
    # Completeness (non-null percentage)
    completeness = {}
    for col in df.columns:
        non_null_pct = (df[col].count() / len(df)) * 100
        if non_null_pct != 100:
            completeness[col] = round(non_null_pct.item(), 2)
    if completeness:
        metrics['completeness'] = completeness
    
    # Average completeness score (excluding ID columns for scoring)
    id_columns = [col for col in df.columns if 'id' in col.lower()]
    completeness_for_score = {k: v for k, v in completeness.items() if k not in id_columns}
    if completeness:
        metrics['avg_completeness'] = round(np.mean(list(completeness_for_score.values())).item(), 2)
    
#   'orders': {'total_rows': 72190,
#   'total_columns': 8,
#   'timestamp': '2026-05-15T11:59:35.994141',
#   'validity': {'quantity_valid_pct': np.float64(99.46)},
#   'avg_validity': 99.46,
#   'overall_quality_score': 5544.81,
#   'quality_status': 'GOOD'}

    # Uniqueness (primary key check)
    if 'order_id' in df.columns and not 'order_detail_id' in df.columns:
        unique_pct = (df['order_id'].nunique() / len(df)) * 100
        if unique_pct < 100:
            metrics['order_uniqueness'] = round(unique_pct, 2)
            metrics['duplicate_orders'] = len(df) - df['order_id'].nunique()
    
    # Validity checks
    validity = {}
    
    # Age validity (total_amount_paid <= subtotal_amount) amount before discount
    if 'discount_amount' in df.columns and 'total_amount_paid' in df.columns:
        valid_record = (df['total_amount_paid'] <= df['subtotal_amount']).sum()
        valid_pct = round((valid_record.item() / len(df)) * 100, 2)
        if valid_pct < 100:
            validity['total_amount_paid_valid_pct'] = valid_pct
    
    # Amount validity (non-negative)
    if 'total_amount_paid' in df.columns:
        valid_amount = (df['total_amount_paid'] >= 0).sum()
        valid_pct = round((valid_amount.item() / len(df)) * 100, 2)
        if valid_pct < 100:
            validity['amount_negative_valid_pct'] = valid_pct
    
    # Quantity validity (positive and greater than 30)
    if 'quantity' in df.columns:
        valid_quantity = ((df['quantity'] > 0) & (df['quantity'] <= 30)).sum()
        valid_pct = round((valid_quantity.item() / len(df)) * 100, 2)
        if valid_pct < 100:
            validity['quantity_valid_pct'] = valid_pct
    
    if validity:
        metrics['validity'] = validity
        metrics['avg_validity'] = round(np.mean(list(validity.values())).item(), 2) if validity else 100
    
    # Outlier detection (transactions > 3 standard deviations)
    if 'discount_amount' in df.columns and 'total_amount_paid' in df.columns:
        mean_amount = df['total_amount_paid'].mean()
        std_amount = df['total_amount_paid'].std()
        outlier_threshold = mean_amount + 3 * std_amount
        outlier_count = (df['total_amount_paid'] > outlier_threshold).sum()
        if outlier_count > 0:
            metrics['outlier_count'] = outlier_count
            metrics['outlier_percentage'] = round((outlier_count.item() / len(df)) * 100, 2)
    
    # Data freshness - max age in hours
    if 'order_datetime' in df.columns:
        max_date = df['order_datetime'].max()
        age_hours = (datetime.now() - max_date).total_seconds() / 3600
        metrics['data_freshness_hours'] = round(age_hours, 2)
    
    # Calculate overall quality score (0-100)
    weights = {
        'completeness': 0.35,
        'validity': 0.35,
        'uniqueness': 0.20,
        'freshness': 0.10
    }
    
    if 'avg_completeness' in metrics:
        completeness_score = min(100, metrics['avg_completeness']) / 100
    else:
        completeness_score = 1

    if 'avg_validity' in metrics:
        validity_score = min(100, metrics['avg_validity']) / 100
    else:
        validity_score = 1

    if 'order_uniqueness' in metrics:
        uniqueness_score = min(100, metrics.get('order_uniqueness', 100)) / 100
    else:
        uniqueness_score = 1

    if 'data_freshness_hours' in metrics:
        freshness_score = max(0, 1 - (metrics.get('data_freshness_hours', 0) / 24))  # Penalize after 24 hours
    else:
        freshness_score = 1

    quality_score = (
        completeness_score * weights['completeness'] +
        validity_score * weights['validity'] +
        uniqueness_score * weights['uniqueness'] +
        freshness_score * weights['freshness']
    ) * 100
    
    metrics['overall_quality_score'] = round(quality_score, 2)
    
    # Quality status
    if quality_score >= QUALITY_THRESHOLDS['quality_score']:
        metrics['quality_status'] = 'GOOD'
    elif quality_score >= QUALITY_THRESHOLDS['quality_score'] - 5:
        metrics['quality_status'] = 'WARNING'
    else:
        metrics['quality_status'] = 'CRITICAL'
    
    return metrics


# ============================================
# DATA CLEANING AND REMEDIATION
# ============================================

def clean_data(df, quality_metrics, tables):
    """Apply automatic fixes to data quality issues"""
    
    df_clean = df.copy()
    remediation_log = []
    
    # 1. Remove duplicates (keep first occurrence)
    if quality_metrics.get('duplicate_orders', 0) > 0:
        before_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['order_id'], keep='first')
        after_count = len(df_clean)
        remediation_log.append({
            'error': 'duplicate_orders',
            'action': 'remove_duplicates',
            'rows_affected': before_count.item() - after_count.item(),
            'success': True
        })
    
    # 1. Handle missing payment methods by filling with the most common method
    if quality_metrics.get('avg_completeness', 0) > 0 and quality_metrics.get('avg_completeness', 0) < 100:
        # print("In ------------ ", quality_metrics , "-------------")
        # Check if 'payment_method' metric exists AND the column is actually in df_clean
        # 1. Safely extract completeness and ensure it is a valid dictionary
        completeness_dict = quality_metrics.get('completeness') or {}
        # 2. Check for the key and the column together
        if 'payment_method' in completeness_dict and 'payment_method' in df_clean.columns:
            
            # Check if the column has any non-null data to avoid index errors on mode()
            if not df_clean['payment_method'].dropna().empty:
                most_common_method = df_clean['payment_method'].mode()[0]
                missing_mask = df_clean['payment_method'].isna()
                missing_count = missing_mask.sum()
                
                # # Perform your imputation here
                # df_clean.loc[missing_mask, 'payment_method'] = most_common_method
    
            if missing_count > 0:
                df_clean.loc[missing_mask, 'payment_method'] = most_common_method
                remediation_log.append({
                    'error': 'missing_payment_methods',
                    'action': 'fill_missing_payment_methods',
                    'rows_affected': missing_count.item(),
                    'most_common_method': most_common_method,
                    'success': True
                })
        else:
            remediation_log.append({
                'error': f'{", ".join(quality_metrics.get("completeness", {}).keys())}',  # List all columns with completeness issues
                'action': 'Nothing',
                'rows_affected': 0,
                'most_common_method': None,
                'success': False
            })
    # else:
    #     print(quality_metrics.get('avg_completeness', 0))
    
    # 2. Fix negative amounts
    if 'discount_amount' in df.columns and 'total_amount_paid' in df.columns:
        negative_mask = df_clean['total_amount_paid'] < 0
        negative_count = negative_mask.sum()
        if negative_count > 0:
            df_clean.loc[negative_mask, 'total_amount_paid'] = df_clean.loc[negative_mask, 'total_amount_paid'].abs()
            remediation_log.append({
                'error': 'negative_amounts',
                'action': 'fix_negative_amounts',
                'rows_affected': negative_count.item(),
                'success': True
            })
    
    # 3. Cap outliers in amount (99th percentile)
    # 3. Cap outliers in amount (99th percentile)
    if quality_metrics.get('outlier_percentage', 0) > 0 and quality_metrics.get('outlier_percentage', 0) < 100:
        if quality_metrics.get('total_amount_paid', 0) < 100 and 'total_amount_paid' in df_clean.columns:
            # print("Outliers detected: ", quality_metrics.get('outlier_count', 0), " out of ", len(df_clean), " rows (", quality_metrics.get('outlier_percentage', 0), "%)")
            
            if not df_clean['total_amount_paid'].dropna().empty:
                cap_value = df_clean['total_amount_paid'].quantile(0.99)
                outlier_mask = df_clean['total_amount_paid'] > cap_value
                outlier_count = outlier_mask.sum()
                
            if outlier_count > 0:
                # print("Capping total_amount_paid at: ", cap_value)
                affected_order_ids_in_dit = df_clean.loc[outlier_mask, 'order_id'].tolist() if 'order_id' in df_clean.columns else []
                
                # Fix: Use the original outlier_mask directly since it's already aligned with df_clean
                # No need to create new_outlier_mask
                
                # Update order_details table
                order_details_mask = tables['order_details']['order_id'].isin(affected_order_ids_in_dit)
                
                qtty_cap_value = tables['order_details']['quantity'].quantile(0.99) if 'quantity' in tables['order_details'].columns else None
                # if qtty_cap_value:
                #     print("Quantity cap value: ", qtty_cap_value)
                
                all_matching_records = tables['order_details'][order_details_mask]
                matching_quantity_records_mask = all_matching_records['quantity'] > qtty_cap_value

                # Update the quantity in the original dataframe
                if matching_quantity_records_mask.any():
                    
                    tables['order_details'].loc[order_details_mask & matching_quantity_records_mask, 'quantity'] = qtty_cap_value
                    
                    tables['order_details'].loc[order_details_mask, 'discount_pct'] = (
                        tables['order_details'].loc[order_details_mask, 'discount_amount'] / 
                        tables['order_details'].loc[order_details_mask, 'gross_amount']
                    )
                    
                    # Update gross_amount and net_amount for all affected records
                    tables['order_details'].loc[order_details_mask, 'gross_amount'] = (
                        tables['order_details'].loc[order_details_mask, 'quantity'] * 
                        tables['order_details'].loc[order_details_mask, 'unit_price']
                    )
                    
                    # Recalculateb the discount amount
                    tables['order_details'].loc[order_details_mask, 'discount_amount'] = (
                        tables['order_details'].loc[order_details_mask, 'discount_pct'] * 
                        tables['order_details'].loc[order_details_mask, 'gross_amount']
                    )

                    tables['order_details'].loc[order_details_mask, 'net_amount'] = (
                        tables['order_details'].loc[order_details_mask, 'gross_amount'] - 
                        tables['order_details'].loc[order_details_mask, 'discount_amount']
                    )
                    tables['order_details'].drop(['discount_pct'], axis=1, inplace=True)
                    

                # Map the aggregated order metrics cleanly back to df_clean rows
                order_gross_totals = tables['order_details'].groupby('order_id')['gross_amount'].sum()
                order_net_totals = tables['order_details'].groupby('order_id')['net_amount'].sum()
                total_items_totals = tables['order_details'].groupby('order_id')['quantity'].sum()
                
                # Use the original outlier_mask which is aligned with df_clean
                df_clean.loc[outlier_mask, 'subtotal_amount'] = df_clean.loc[outlier_mask, 'order_id'].map(order_gross_totals)
                df_clean.loc[outlier_mask, 'total_amount_paid'] = df_clean.loc[outlier_mask, 'order_id'].map(order_net_totals)
                df_clean.loc[outlier_mask, 'total_items'] = df_clean.loc[outlier_mask, 'order_id'].map(total_items_totals)
                
                remediation_log.append({
                    'error': 'amount_outliers',
                    'action': 'cap_amount_outliers',
                    'rows_affected': outlier_count.item(),
                    'cap_value': round(cap_value.item(), 2),
                    'success': True
                })
        else:
            remediation_log.append({
                'error': 'other_outliers',
                'action': 'Nothing',
                'rows_affected': 0,
                'cap_value': None,
                'success': False
            })
    # 4. Fix invalid ages (set to median)
    # if 'customer_age' in df_clean.columns:
    #     invalid_mask = (df_clean['customer_age'] < 0) | (df_clean['customer_age'] > 120)
    #     invalid_count = invalid_mask.sum()
    #     if invalid_count > 0:
    #         median_age = df_clean.loc[~invalid_mask, 'customer_age'].median()
    #         df_clean.loc[invalid_mask, 'customer_age'] = median_age
    #         remediation_log.append({
    #             'error': 'invalid_ages',
    #             'action': 'fix_invalid_ages',
    #             'rows_affected': invalid_count,
    #             'median_used': round(median_age, 1),
    #             'success': True
    #         })
    
    # 5. Fill missing ages with median
    # if 'customer_age' in df_clean.columns:
    #     missing_mask = df_clean['customer_age'].isna()
    #     missing_count = missing_mask.sum()
    #     if missing_count > 0:
    #         median_age = df_clean['customer_age'].median()
    #         df_clean.loc[missing_mask, 'customer_age'] = median_age
    #         remediation_log.append({
    #             'error': 'missing_ages',
    #             'action': 'fill_missing_ages',
    #             'rows_affected': missing_count,
    #             'median_used': round(median_age, 1),
    #             'success': True
    #         })
    
    return df_clean, remediation_log


# ============================================
# PREPARE DATA
# ============================================

def prepare_data(df_preps: dict):
    """Create any relevant transformations in preparation for data analysis"""
    

    # tables
    # df_order_details = df_preps['order_details']
    df_orders = df_preps['orders']
    # df_stores = df_preps['stores']
    # df_employees = df_preps['employees']
    # df_promotions = df_preps['promotions']
    
    # Ensure transaction_date is datetime
    df_orders['order_datetime'] = pd.to_datetime(df_orders['order_datetime'])
    
    df_orders['year'] = df_orders['order_datetime'].dt.year

    # Merge category, subcategory and products into one table
    cats = pd.merge(df_preps['subcategories'], df_preps['categories'], on='category_id')
    products = pd.merge(df_preps['products'], cats, on='subcategory_id').drop(['subcategory_id', 'category_id'], axis=1)
    
    # Remove the category, subcategory and products tables from df_preps then add the newly prepared products table
    tables_to_be_droped = ['subcategories', 'categories', 'products']
    for table in tables_to_be_droped:
        if table in df_preps:
            del df_preps[table]
    
    df_preps['products'] = products
    
    return df_preps

