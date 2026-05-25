import streamlit as st
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("Streamlit Gauge Chart Example")

# 1. Create an input slider to dynamically update the gauge value
target_value = st.slider("Select Value:", min_value=0, max_value=100, value=65)

# 2. Build the Plotly Gauge Chart
fig = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = target_value,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "Server CPU Utilization (%)", 'font': {'size': 24}},
    delta = {'reference': 50, 'increasing': {'color': "RebeccaPurple"}},
    gauge = {
        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "darkblue"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 50], 'color': 'rgba(0, 255, 0, 0.3)'},      # Green zone
            {'range': [50, 85], 'color': 'rgba(255, 255, 0, 0.3)'},    # Yellow zone
            {'range': [85, 100], 'color': 'rgba(255, 0, 0, 0.3)'}     # Red zone
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 90
        }
    }
))

# 3. Optimize configuration for responsive mobile/desktop scaling
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=40, b=20)
)

# 4. Display the chart inside Streamlit
st.plotly_chart(fig, use_container_width=True)


# import streamlit as st
from streamlit_echarts import st_echarts

st.title("Streamlit ECharts Gauge Example")

# 1. User input to change the gauge value dynamically
metric_value = st.slider("Select Performance Score:", min_value=0, max_value=100, value=78)

# 2. Define the ECharts configuration dictionary
options = {
    "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
    "series": [
        {
            "name": "Indicator",
            "type": "gauge",
            "startAngle": 180,
            "endAngle": 0,
            "progress": {"show": True, "width": 18},
            "axisLine": {"lineStyle": {"width": 18}},
            "axisTick": {"show": False},
            "splitLine": {"length": 15, "lineStyle": {"width": 2, "color": "#999"}},
            "axisLabel": {"page": "distance", "distance": 25, "color": "#999", "fontSize": 14},
            "anchor": {"show": False},
            "title": {"show": True, "offsetCenter": [0, "-20%"], "fontSize": 16},
            "detail": {
                "valueAnimation": True,
                "formatter": "{value}%",
                "offsetCenter": [0, "30%"],
                "fontSize": 30,
                "fontWeight": "bold"
            },
            "data": [{"value": metric_value, "name": "System Health"}],
        }
    ],
}

# 3. Render the gauge chart with custom height
st_echarts(options=options, height="400px")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Corporate Budget Target Tracker")

# 1. Construct the source DataFrame table
data = {
    "Department": ["Marketing", "Engineering", "Sales", "Operations", "Human Resources"],
    "Current Spend ($)": [42000, 89000, 115000, 61000, 23000],
    "Total Budget ($)": [60000, 100000, 120000, 80000, 25000],
}
df = pd.DataFrame(data)

# Calculate percentage utilization directly on the dataframe
df["Utilization (%)"] = ((df["Current Spend ($)"] / df["Total Budget ($)"]) * 100).round(1)

# 2. Display the source data table to the user
st.subheader("Departmental Budget Ledger")
st.dataframe(df, use_container_width=True, hide_index=True)

# 3. Dropdown selector to extract row data from the DataFrame
st.subheader("Gauge Performance Analysis")
selected_dept = st.selectbox("Select a Department to Audit:", df["Department"])

# Extract specific metrics for the chosen department row
row = df[df["Department"] == selected_dept].iloc[0]
current_spend = row["Current Spend ($)"]
total_budget = row["Total Budget ($)"]
utilization = row["Utilization (%)"]

# 4. Construct a clean circular ring gauge (Non-Speedometer)
fig = go.Figure(go.Indicator(
    mode = "number+gauge",
    value = utilization,
    number = {
        'suffix': "%", 
        'font': {'size': 60, 'color': '#1f77b4'}
    },
    title = {
        'text': f"<b>{selected_dept}</b><br><span style='font-size:0.8em;color:gray'>Budget Consumed</span>",
        'font': {'size': 20}
    },
    gauge = {
        'shape': "angular",
        'axis': {'range': [0, 100], 'ticksuffix': "%"},
        'bar': {'color': "#1f77b4", 'thickness': 1.0}, # Solid block fill style
        'bgcolor': "#e5ecf6",
        'borderwidth': 0
    }
))

# Clean layout frame adjustments
fig.update_layout(
    height=300,
    margin=dict(l=10, r=10, t=50, b=10)
)

# 5. Render side-by-side metrics and the gauge plot
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.metric(label="Funds Expended", value=f"${current_spend:,}")
    st.metric(label="Allocated Limit", value=f"${total_budget:,}")

with col2:
    st.plotly_chart(fig, use_container_width=True)
