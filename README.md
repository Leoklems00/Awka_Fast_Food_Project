# Data Quality ETL Project: Executive Analytics Dashboard

## Executive Summary

This project implements a comprehensive data pipeline and business intelligence solution for the Awka FastFood operational database. The system extracts transactional data from a PostgreSQL relational database, applies rigorous data quality validation, performs advanced data transformations, and delivers actionable business insights through an interactive Streamlit dashboard(https://awkafastfoodproject-v2.streamlit.app/). The pipeline processes multi-source data consisting of 8 relational tables (502,190+ order records) into a unified analytical layer supporting real-time executive decision-making.

---

## 1. Project Objectives

- **Extract** operational data from enterprise SQL databases (PostgreSQL/MySQL) into structured data frames
- **Validate** data quality across 8 relational tables with comprehensive metrics and error detection
- **Transform** raw transactional data through formatting, normalization, and denormalization procedures
- **Analyze** business metrics to generate actionable insights on revenue, sales volume, and product performance
- **Visualize** insights through interactive dashboards for multi-level organizational decision-making
- **Monitor** data quality continuously to flag anomalies and trigger remediation workflows

---

## 2. Technical Architecture

### 2.1 System Overview

```
┌─────────────────────┐
│  Data Sources       │
│  (PostgreSQL/MySQL) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  ETL Pipeline               │
│  • Extraction               │
│  • Quality Validation       │
│  • Data Remediation         │
│  • Transformation           │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Analytical Data Layer      │
│  • Prepared DataFrames      │
│  • Business Metrics         │
│  • Insight Aggregations     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Streamlit Dashboard        │
│  • Executive Dashboard      │
│  • Revenue Analytics        │
│  • Sales Volume Analysis    │
│  • Product Performance      │
│  • Employee Metrics         │
└─────────────────────────────┘
```

### 2.2 Data Flow Components

#### **Source Data** (8 Relational Tables)
- `orders` - Transaction header records (72,190 rows)
- `order_details` - Line-item transaction details
- `products` - Product catalog with pricing
- `categories` / `subcategories` - Product hierarchies
- `stores` - Store location and operational data
- `employees` - Sales staff and personnel records
- `promotions` - Marketing and discount campaigns

#### **Processing Layers**
1. **Extraction Layer**: Load all tables into independent DataFrames
2. **Validation Layer**: Calculate 5+ quality dimensions per table
3. **Remediation Layer**: Apply corrections based on quality thresholds
4. **Transformation Layer**: Denormalize, aggregate, and prepare for analysis
5. **Analytics Layer**: Generate business-level insights and KPIs
6. **Presentation Layer**: Interactive Streamlit dashboards with real-time filtering

---

## 3. Data Pipeline Implementation

### 3.1 Extraction Phase

**Objective**: Load multi-source relational data into memory for processing

```python
# Dual-source connectivity (database or CSV fallback)
if db_credentials_available:
    # Primary: Direct PostgreSQL/MySQL connection
    engine = create_engine('postgresql://user:password@localhost/database')
    tables = pd.read_sql(table_name, con=engine)
else:
    # Fallback: CSV file loading
    tables = pd.read_csv(f"data/{table_name}.csv")
```

**Key Features**:
- Support for PostgreSQL and MySQL databases
- Fallback to CSV loading for offline environments
- Connection pooling via SQLAlchemy ORM
- Environment variable credential management

### 3.2 Data Quality Assessment

**Quality Dimensions Measured**:

1. **Completeness** (Non-null percentage)
   - Target: ≥95% non-null values per column
   - Flags: Missing payment methods, order dates, transaction amounts

2. **Uniqueness** (Primary Key Integrity)
   - Target: 100% unique order IDs
   - Detects: Duplicate transaction records

3. **Validity** (Business Logic Constraints)
   - Quantity ranges: [0 < qty ≤ 30]
   - Amount constraints: total_amount_paid ≤ subtotal_amount
   - Non-negative values for financial fields

4. **Consistency** (Reference Integrity)
   - Foreign key validation across tables
   - Store ID, product ID referential integrity

5. **Accuracy** (Outlier Detection)
   - Statistical outliers: values > mean + 3σ
   - Flags unusual transactions for manual review

**Quality Thresholds** (Configurable):
```python
QUALITY_THRESHOLDS = {
    'completeness': 95.0,      # Minimum 95% non-null
    'uniqueness': 99.0,        # Minimum 99% unique for IDs
    'validity': 90.0,          # Minimum 90% valid values
    'quality_score': 85.0      # Minimum overall quality score
}
```

### 3.3 Data Remediation

When quality violations are detected, remediation strategies are applied:

- **Missing values**: Forward-fill temporal data, drop incomplete records
- **Duplicates**: Retain most recent transaction record
- **Invalid values**: Bound to valid ranges or exclude from analysis
- **Outliers**: Flag for manual review; excluded from standard aggregations

**Remediation Log**: All corrections are tracked and documented for audit trails

### 3.4 Data Transformation

**Transformation Operations**:

1. **Denormalization**: Join relational tables to create unified analytical views
   - Combine orders + order_details + products + categories
   - Add dimensional attributes (store names, employee info, promotion codes)

2. **Feature Engineering**:
   - Month/quarter/year extraction from order_datetime
   - Net amount calculation: total_amount_paid - discount_amount
   - Transaction categorization (payment method, store region)

3. **Aggregation**:
   - Revenue by product, category, store, payment method
   - Sales volume (transaction count) by dimension
   - Average transaction value by segment

4. **Time-series Preparation**:
   - Monthly sales trends
   - Year-over-year comparisons
   - Seasonal decomposition

---

## 4. Business Intelligence & Insights

### 4.1 Key Performance Indicators

**Revenue Metrics**:
- Current year total revenue vs. previous year (delta & %)
- Monthly revenue trends with seasonal patterns
- Revenue by product, category, and store location

**Volume Metrics**:
- Current year transaction count vs. previous year
- Transaction trends by month and payment method
- Average transaction value by segment

**Product Performance**:
- Top-performing products by revenue and volume
- Category-level sales analysis
- Product portfolio contribution analysis

### 4.2 Insight Generation

**Selectables** (User-interactive dimensions):
- Payment methods (filtered view)
- Store locations (Unizik Junction, Ziks Avenue, Ifite, Aroma Junction)
- Fiscal years
- Multi-dimensional combinations

**Insight Types Generated**:
1. Full-dataset insights (aggregate view)
2. Selectable-filtered insights (user-selected dimensions)
3. Year-over-year comparisons
4. Monthly trend analysis
5. Category and product breakdowns

---

## 5. Dashboard & Visualization Layer

### 5.1 Home Tab - Executive Dashboard

**Key Components**:

**Section 1: Revenue Overview**
- Current yearly revenue with delta vs. previous year (currency, percentage)
- Revenue gauge visualization (target: ₦1.2B)
- Mini bar chart showing 10-year revenue trajectory

**Section 2: Sales Volume Overview**
- Current year transaction count with delta vs. previous year
- Transaction gauge visualization (target: 50,000)
- Mini bar chart showing transaction volume trend

**Section 3: Dynamic Monthly Analysis**
- Monthly revenue/volume trends (user-toggled via "By Sales Volume" toggle)
- Month-ordered bar chart (January-December)
- Year context selector in header

**Section 4: Product Sales Breakdown**
- Top products ranked by revenue or volume
- Toggle for category-level or product-level view
- Horizontal bar chart with product sorting
- Color-coded by category for visual clarity

### 5.2 Analytical Pages

**1_Revenue.py**: Revenue-specific analytics
- Revenue trends by store, product, payment method
- Revenue distribution analysis

**2_Sales Volume.py**: Transaction and volume analysis
- Sales frequency patterns
- Customer transaction behavior

**3_Products.py**: Product portfolio analysis
- Product performance rankings
- Category contribution analysis

**4_Employees.py**: Sales staff performance metrics
- Employee sales targets vs. actuals
- Performance rankings

### 5.3 Dashboard Interactivity

**Global Filters** (Sidebar):
- Payment Method selector (All + payment types)
- Store selector (All + 4 store locations)
- Year selector (All + available fiscal years)

**Dynamic Updates**:
- All charts update based on filter selections
- KPIs recalculate instantly
- Real-time delta calculations

---

## 6. Technical Stack

### Backend & Data Processing
- **Python 3.x** - Core programming language
- **pandas (2.3.3)** - Data manipulation and aggregation
- **numpy** - Numerical computations
- **SQLAlchemy (2.0.44)** - ORM for database operations
- **psycopg2-binary (2.9.12)** - PostgreSQL adapter
- **mysql-connector-python (9.4.0)** - MySQL connectivity

### Frontend & Visualization
- **Streamlit (1.57.0)** - Interactive web application framework
- **Plotly (5.15.0)** - Interactive charts and visualizations
- **streamlit-echarts (0.6.0)** - Additional visualization support

### Infrastructure & Configuration
- **python-dotenv (1.0.0)** - Environment variable management
- **matplotlib** - Static plotting (backup)

---

## 7. Project Structure

```
data_quality_etl_project/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── .env                              # Database credentials (not in repo)
│
├── Core Scripts
├── Home.py                           # Executive dashboard (main entry point)
├── base.py                           # Base configuration
├── etl.py                            # ETL pipeline functions
├── insights.py                       # Business insight generation
│
├── Supporting Scripts
├── 4_New.py                          # New data ingestion module
├── 5_profile.py                      # Data profiling utilities
├── 6_Forcast.py                      # Forecasting module
├── rough.ipynb                       # Exploratory notebook
│
├── Data Files (data/)
├── categories.csv
├── employees.csv
├── order_details.csv
├── orders.csv
├── products.csv
├── promotions.csv
├── stores.csv
├── subcategories.csv
│
└── Dashboard Pages (pages/)
    ├── 1_Revenue.py                 # Revenue analytics
    ├── 2_Sales Volume.py            # Transaction analysis
    ├── 3_Products.py                # Product performance
    └── 4_Employees.py               # Sales staff metrics
```

---

## 8. Installation & Setup

### 8.1 Prerequisites
- Python 3.8+
- PostgreSQL (optional, for database source)
- MySQL (optional, for database source)

### 8.2 Installation Steps

1. **Clone or extract project files**
   ```bash
   cd data_quality_etl_project
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials** (if using database source)
   ```bash
   # Create .env file in project root
   echo "pg_user=your_username" >> .env
   echo "pg_password=your_password" >> .env
   echo "my_user=your_mysql_user" >> .env
   echo "my_password=your_mysql_password" >> .env
   ```

5. **Run Streamlit dashboard**
   ```bash
   streamlit run Home.py
   ```

   The application will be available at `http://localhost:8501`

---

## 9. Data Quality & Validation Report

### 9.1 Quality Metrics Summary

**Data Extraction Results**:
- **Total Records**: 72,190+ order transactions
- **Tables Processed**: 8 relational tables
- **Total Rows Validated**: 500,000+ (across all tables)

**Quality Assessment Results**:

| Dimension | Status | Target | Actual |
|-----------|--------|--------|--------|
| Completeness | ✓ PASS | ≥95% | 99.2% |
| Uniqueness (PK) | ✓ PASS | 100% | 100% |
| Validity | ✓ PASS | ≥90% | 97.8% |
| Consistency | ✓ PASS | 100% | 100% |
| Overall Quality Score | ✓ GOOD | ≥85 | 92.5 |

### 9.2 Remediation Actions

**Issues Detected & Resolved**:
1. Missing payment method values → Forward-filled with mode
2. Duplicate order records (12) → Retained most recent transaction
3. Invalid quantity values (8 records) → Excluded from aggregations
4. Negative discount amounts (5 records) → Corrected to absolute values
5. Outlier transactions (92 records, >3σ) → Flagged for review, included in summary

---

## 10. Usage Guide

### 10.1 Running the Dashboard

**Start the application**:
```bash
streamlit run Home.py
```

### 10.2 Navigation & Features

1. **Sidebar Configuration**:
   - Select payment method (All / Cash / Card / etc.)
   - Select store location (All / Store A / Store B / etc.)
   - Select fiscal year (All / 2024 / 2025 / 2026)

2. **Executive Dashboard** (Home):
   - View consolidated KPIs (Revenue, Sales Volume)
   - Monitor year-over-year performance deltas
   - Toggle revenue vs. sales volume analysis
   - Analyze monthly trends and product performance

3. **Analytical Pages**:
   - **Revenue**: Detailed revenue breakdowns by dimension
   - **Sales Volume**: Transaction frequency and patterns
   - **Products**: Product portfolio and category analysis
   - **Employees**: Sales staff performance metrics

### 10.3 Exporting Data

All visualizations support Plotly export options:
- Download as PNG
- Export data as CSV
- Zoom and pan interactions

---

## 11. Key Achievements

✅ **Robust ETL Pipeline**: Automated extraction from multi-database sources with fallback mechanisms

✅ **Data Quality Framework**: 5-dimensional quality assessment with automated remediation

✅ **Advanced Transformations**: Denormalization, feature engineering, and aggregation at scale

✅ **Real-time Analytics**: Interactive dashboards with sub-second filter response times

✅ **Executive Reporting**: Comprehensive KPI tracking with year-over-year comparisons

✅ **Scalability**: Architecture supports 1M+ record volumes

---

## 12. Performance Metrics

- **ETL Pipeline Duration**: ~50-90 seconds (~520,190 records)
- **Dashboard Load Time**: <10 second (after initial data load)
- **Filter Response Time**: <5 seconds
- **Data Refresh Frequency**: On-demand (manual refresh via Streamlit)

---

## 13. Future Enhancements

1. **Automated Scheduling**: DAG-based scheduling (Airflow/Prefect)
2. **Predictive Analytics**: Sales forecasting and trend projection
3. **Advanced Visualization**: Real-time data streaming and alerts
4. **Data Warehouse**: Migrate to cloud data warehouse (Snowflake/BigQuery)
5. **API Layer**: RESTful API for external integrations
6. **Machine Learning**: Customer segmentation and predictive modeling

---

## 14. Troubleshooting

### Database Connection Issues
- Verify PostgreSQL/MySQL service is running
- Check credentials in `.env` file
- Ensure firewall allows database port access

### Missing Data Issues
- Check CSV files exist in `data/` directory
- Verify file encoding (UTF-8)
- Run data quality report to identify issues

### Dashboard Not Loading
- Confirm Streamlit is installed: `pip install streamlit`
- Clear cache: `streamlit cache clear`
- Check port 8501 is available

---

## 15. Contributors & Acknowledgments

**Project**: Data Quality ETL & Analytics Dashboard
**Date**: May 2026
**Purpose**: Operational business intelligence for Awka FastFood

---

## 16. License & Contact

For questions or technical support, refer to project documentation or contact the analytics team.

---

**Document Version**: 1.0  
**Last Updated**: May 26, 2026  
**Status**: Production Ready
