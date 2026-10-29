import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Configuration ---
st.set_page_config(
    page_title="Enterprise Sales & Revenue Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Professional Styling & CSS ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    div.stMetric {
        background-color: #FFFFFF;
        padding: 18px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
    }
    div.stMetric label { font-weight: 600 !important; color: #475569 !important; font-size: 0.9rem !important; }
    div.stMetric div[data-testid="stMetricValue"] { color: #0F172A !important; font-size: 1.8rem !important; font-weight: 700 !important; }
    h1, h2, h3 { color: #1E293B; font-family: 'Inter', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #1E293B; color: #FFFFFF; }
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] .stMarkdown { color: #F1F5F9 !important; }
    </style>
""", unsafe_allow_html=True)

# --- Load and Cache Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data file: {e}. Please ensure 'sales_data.csv' is in the project directory.")
    st.stop()

# --- Sidebar Controls & Filters ---
st.sidebar.markdown("## 🎛️ Dashboard Controls")

all_regions = sorted(df["Region"].unique().tolist())
region_filter = st.sidebar.multiselect("Select Region(s):", options=all_regions, default=all_regions)

all_categories = sorted(df["Category"].unique().tolist())
category_filter = st.sidebar.multiselect("Select Category(s):", options=all_categories, default=all_categories)

all_customers = sorted(df["CustomerType"].unique().tolist())
customer_filter = st.sidebar.multiselect("Customer Segment:", options=all_customers, default=all_customers)

filtered_df = df[
    (df["Region"].isin(region_filter)) & 
    (df["Category"].isin(category_filter)) &
    (df["CustomerType"].isin(customer_filter))
]

st.sidebar.markdown("---")
st.sidebar.info(f"Showing **{len(filtered_df):,}** of **{len(df):,}** transactions.")

# --- Main Dashboard Header ---
st.title("📈 Enterprise Sales & Revenue Intelligence Dashboard")
st.markdown("Comprehensive analysis of revenue performance, profitability, and regional distribution.")
st.markdown("---")

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filter combination.")
else:
    # KPIs
    total_revenue = filtered_df["TotalSales"].sum()
    total_profit = filtered_df["Profit"].sum()
    total_orders = filtered_df["OrderID"].nunique()
    avg_order_value = filtered_df["TotalSales"].mean() if total_orders > 0 else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2: st.metric("Total Profit", f"${total_profit:,.2f}")
    with col3: st.metric("Profit Margin", f"{profit_margin:.1f}%")
    with col4: st.metric("Total Orders", f"{total_orders:,}")
    with col5: st.metric("Avg Order Value", f"${avg_order_value:,.2f}")

    st.markdown("---")

    # Charts Row 1
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("📅 Monthly Revenue Trend")
        monthly_sales = filtered_df.groupby('MonthYear')['TotalSales'].sum().reset_index()
        fig_trend = px.line(monthly_sales, x='MonthYear', y='TotalSales', markers=True, template='plotly_white')
        fig_trend.update_traces(line=dict(color='#2563EB', width=3))
        st.plotly_chart(fig_trend, use_container_width=True)

    with chart_col2:
        st.subheader("🍩 Revenue Share by Category")
        category_sales = filtered_df.groupby('Category')['TotalSales'].sum().reset_index()
        fig_cat = px.pie(category_sales, values='TotalSales', names='Category', hole=0.5, template='plotly_white', color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig_cat, use_container_width=True)

    # Charts Row 2
    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.subheader("🏆 Top 5 Performing Products")
        top_products = filtered_df.groupby('Product')['TotalSales'].sum().nlargest(5).reset_index().sort_values('TotalSales', ascending=True)
        fig_products = px.bar(top_products, x='TotalSales', y='Product', orientation='h', template='plotly_white', color='TotalSales', color_continuous_scale='Blues')
        fig_products.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_products, use_container_width=True)

    with chart_col4:
        st.subheader("🌍 Regional Performance & Profitability")
        region_perf = filtered_df.groupby('Region')[['TotalSales', 'Profit']].sum().reset_index()
        fig_region = go.Figure(data=[
            go.Bar(name='Revenue', x=region_perf['Region'], y=region_perf['TotalSales'], marker_color='#3B82F6'),
            go.Bar(name='Profit', x=region_perf['Region'], y=region_perf['Profit'], marker_color='#10B981')
        ])
        fig_region.update_layout(barmode='group', template='plotly_white')
        st.plotly_chart(fig_region, use_container_width=True)

    # Raw Data Table
    st.markdown("---")
    with st.expander("🔍 Explore Granular Transaction Data"):
        st.dataframe(filtered_df, use_container_width=True)
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Filtered Data as CSV", data=csv_data, file_name="filtered_sales_report.csv", mime="text/csv")