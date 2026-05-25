import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📈 Departmental Expenditure Forecasting")
st.caption("Using an Auto-Regressive Integrated Moving Average (ARIMA) Model")

# 1. GENERATE SYNTHETIC HISTORICAL DATA (Constructed Table)
@st.cache_data
def generate_historical_data():
    np.random.seed(42)
    start_date = datetime(2026, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(120)] # 120 days of data
    
    # Create a time series with a slight upward trend and some random noise
    base_spend = 5000
    trend = np.linspace(0, 1500, 120)
    noise = np.random.normal(0, 300, 120)
    weekly_cycle = 400 * np.sin(2 * np.pi * np.array(range(120)) / 7)
    
    spend = base_spend + trend + noise + weekly_cycle
    
    df = pd.DataFrame({"Date": dates, "Daily Spend ($)": spend.round(2)})
    df.set_index("Date", inplace=True)
    return df

df_history = generate_historical_data()

# Layout splits: Left sidebar for controls, Main panel for metrics and charts
with st.sidebar:
    st.header("Forecast Settings")
    # Let user decide how many days into the future to project
    forecast_steps = st.slider("Days to Forecast:", min_value=7, max_value=60, value=30)
    
    st.subheader("ARIMA Hyperparameters")
    p = st.number_input("p (Autoregressive Order)", min_value=0, max_value=5, value=1)
    d = st.number_input("d (Differencing Order)", min_value=0, max_value=2, value=1)
    q = st.number_input("q (Moving Average Order)", min_value=0, max_value=5, value=1)

# 2. TRAIN THE ARIMA MODEL
@st.cache_resource
def run_arima_forecast(series, p, d, q, steps):
    # Fit the ARIMA model on the historical column
    model = ARIMA(series, order=(p, d, q))
    model_fitted = model.fit()
    
    # Generate predictions and fetch the confidence intervals
    forecast_res = model_fitted.get_forecast(steps=steps)
    forecast_index = pd.date_range(start=series.index[-1] + timedelta(days=1), periods=steps)
    
    forecast_df = pd.DataFrame({
        "Forecasted Spend ($)": forecast_res.predicted_mean.values,
        "Lower Bound ($)": forecast_res.conf_int().iloc[:, 0].values,
        "Upper Bound ($)": forecast_res.conf_int().iloc[:, 1].values
    }, index=forecast_index)
    
    return forecast_df

with st.spinner("Fitting ARIMA Model and calculating projections..."):
    df_forecast = run_arima_forecast(df_history["Daily Spend ($)"], p, d, q, forecast_steps)

# 3. DISPLAY PERFORMANCE METRICS
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Last Recorded Daily Spend", 
        value=f"${df_history['Daily Spend ($)'].iloc[-1]:,.2f}"
    )
with col2:
    projected_avg = df_forecast["Forecasted Spend ($)"].mean()
    st.metric(
        label="Projected Average Daily Spend", 
        value=f"${projected_avg:,.2f}",
        delta=f"{(projected_avg - df_history['Daily Spend ($)'].iloc[-1]):+,.2f} vs last day"
    )
with col3:
    st.metric(
        label="Total Projected Budget Needed (Next 30 Days)", 
        value=f"${df_forecast['Forecasted Spend ($)'].iloc[:30].sum():,.2f}"
    )

# 4. PLOT HISTORICAL VS FORECAST WITH CONFIDENCE INTERVAL ENVELOPES
fig = go.Figure()

# Historical Line
fig.add_trace(go.Scatter(
    x=df_history.index, 
    y=df_history["Daily Spend ($)"],
    name="Historical Spend",
    line=dict(color="#1f77b4", width=2)
))

# Forecasted Line
fig.add_trace(go.Scatter(
    x=df_forecast.index, 
    y=df_forecast["Forecasted Spend ($)"],
    name="ARIMA Forecast",
    line=dict(color="#ff7f0e", width=2, dash="dash")
))

# Upper Bound Interval Line (Invisible, used for filling background zone)
fig.add_trace(go.Scatter(
    x=df_forecast.index,
    y=df_forecast["Upper Bound ($)"],
    showlegend=False,
    line=dict(width=0),
    hoverinfo="skip"
))

# Lower Bound Interval Line (Fills space between Upper and Lower bounds)
fig.add_trace(go.Scatter(
    x=df_forecast.index,
    y=df_forecast["Lower Bound ($)"],
    name="95% Confidence Interval",
    fill='tonexty',
    fillcolor='rgba(255, 127, 14, 0.15)', # Light transparent orange
    line=dict(width=0),
    hoverinfo="skip"
))

# Layout configurations
fig.update_layout(
    title="Financial Run-Rate and ARIMA Projections",
    xaxis_title="Timeline",
    yaxis_title="Expenditure ($)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=80, b=20),
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# 5. DATA TABLES LOOKUP BELOW
expander = st.expander("Inspect Raw Forecast Data Sheet")
with expander:
    st.dataframe(df_forecast, use_container_width=True)
