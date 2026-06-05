import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Page config
st.set_page_config(
    page_title="Knowledge Base Health Dashboard",
    page_icon="📚",
    layout="wide"
)

# Get Snowflake session
session = get_active_session()

# Title
st.title("📚 Knowledge Base Health Dashboard")
st.markdown("Monitor knowledge base readiness, content coverage, and article freshness across accounts and brands.")

# Sidebar for region selection
st.sidebar.header("Filters")
region = st.sidebar.selectbox(
    "Select Region",
    options=["AMER", "EMEA"],
    help="Choose which regional database to query"
)

# Map region to database
database_map = {
    "AMER": "CLEANSED",
    "EMEA": "CLEANSED"
}

selected_database = database_map[region]

# Query to get latest metrics aggregated by account
@st.cache_data(ttl=3600)
def get_account_summary(_session, database):
    query = f"""
    WITH latest_metrics AS (
        SELECT
            instance_account_id,
            instance_brand_id,
            metric_id,
            value_amount,
            trend_change_amount,
            created_at
        FROM {database}.PRODUCT_ML_SCIENCE.KNOWLEDGE_HEALTH_METRICS
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY instance_account_id, instance_brand_id, metric_id
            ORDER BY created_at DESC
        ) = 1
    ),
    account_metrics AS (
        SELECT
            instance_account_id,
            COUNT(DISTINCT instance_brand_id) as brand_count,
            AVG(CASE WHEN metric_id = 'article_ai_readiness' THEN value_amount END) as article_ai_readiness_value,
            AVG(CASE WHEN metric_id = 'article_ai_readiness' THEN trend_change_amount END) as article_ai_readiness_trend,
            AVG(CASE WHEN metric_id = 'content_coverage' THEN value_amount END) as content_coverage_value,
            AVG(CASE WHEN metric_id = 'content_coverage' THEN trend_change_amount END) as content_coverage_trend,
            AVG(CASE WHEN metric_id = 'article_freshness' THEN value_amount END) as article_freshness_value,
            AVG(CASE WHEN metric_id = 'article_freshness' THEN trend_change_amount END) as article_freshness_trend,
            MAX(created_at) as last_updated
        FROM latest_metrics
        GROUP BY instance_account_id
    )
    SELECT * FROM account_metrics
    ORDER BY instance_account_id
    """
    return _session.sql(query).to_pandas()

# Query to get brand-level detail for a specific account
@st.cache_data(ttl=3600)
def get_brand_detail(_session, database, account_id):
    query = f"""
    WITH latest_metrics AS (
        SELECT
            instance_account_id,
            instance_brand_id,
            metric_id,
            value_amount,
            trend_change_amount,
            created_at
        FROM {database}.PRODUCT_ML_SCIENCE.KNOWLEDGE_HEALTH_METRICS
        WHERE instance_account_id = {account_id}
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY instance_account_id, instance_brand_id, metric_id
            ORDER BY created_at DESC
        ) = 1
    )
    SELECT
        instance_brand_id,
        MAX(CASE WHEN metric_id = 'article_ai_readiness' THEN value_amount END) as article_ai_readiness_value,
        MAX(CASE WHEN metric_id = 'article_ai_readiness' THEN trend_change_amount END) as article_ai_readiness_trend,
        MAX(CASE WHEN metric_id = 'content_coverage' THEN value_amount END) as content_coverage_value,
        MAX(CASE WHEN metric_id = 'content_coverage' THEN trend_change_amount END) as content_coverage_trend,
        MAX(CASE WHEN metric_id = 'article_freshness' THEN value_amount END) as article_freshness_value,
        MAX(CASE WHEN metric_id = 'article_freshness' THEN trend_change_amount END) as article_freshness_trend,
        MAX(created_at) as last_updated
    FROM latest_metrics
    GROUP BY instance_brand_id
    ORDER BY instance_brand_id
    """
    return _session.sql(query).to_pandas()

# Load account summary data
with st.spinner(f"Loading {region} account data..."):
    df_accounts = get_account_summary(session, selected_database)

# Display summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Accounts", f"{len(df_accounts):,}")
with col2:
    avg_readiness = df_accounts['ARTICLE_AI_READINESS_VALUE'].mean()
    st.metric("Avg AI Readiness", f"{avg_readiness:.1f}%")
with col3:
    avg_coverage = df_accounts['CONTENT_COVERAGE_VALUE'].mean()
    st.metric("Avg Content Coverage", f"{avg_coverage:.1f}%")
with col4:
    avg_freshness = df_accounts['ARTICLE_FRESHNESS_VALUE'].mean()
    st.metric("Avg Article Freshness", f"{avg_freshness:.1f}%")

st.markdown("---")

# Account-level table with search and selection
st.subheader("Account Summary")

# Add search box
search_term = st.text_input("🔍 Search by Account ID", "")

# Filter accounts based on search
if search_term:
    df_filtered = df_accounts[df_accounts['INSTANCE_ACCOUNT_ID'].astype(str).str.contains(search_term)]
else:
    df_filtered = df_accounts

# Format the dataframe for display
df_display = df_filtered.copy()
df_display['ARTICLE_AI_READINESS_VALUE'] = df_display['ARTICLE_AI_READINESS_VALUE'].round(1)
df_display['CONTENT_COVERAGE_VALUE'] = df_display['CONTENT_COVERAGE_VALUE'].round(1)
df_display['ARTICLE_FRESHNESS_VALUE'] = df_display['ARTICLE_FRESHNESS_VALUE'].round(1)

# Display the table
st.dataframe(
    df_display,
    column_config={
        "INSTANCE_ACCOUNT_ID": st.column_config.NumberColumn("Account ID", format="%d"),
        "BRAND_COUNT": st.column_config.NumberColumn("# Brands", format="%d"),
        "ARTICLE_AI_READINESS_VALUE": st.column_config.NumberColumn("AI Readiness %", format="%.1f"),
        "ARTICLE_AI_READINESS_TREND": st.column_config.NumberColumn("AI Readiness Trend", format="%.2f"),
        "CONTENT_COVERAGE_VALUE": st.column_config.NumberColumn("Content Coverage %", format="%.1f"),
        "CONTENT_COVERAGE_TREND": st.column_config.NumberColumn("Coverage Trend", format="%.2f"),
        "ARTICLE_FRESHNESS_VALUE": st.column_config.NumberColumn("Article Freshness %", format="%.1f"),
        "ARTICLE_FRESHNESS_TREND": st.column_config.NumberColumn("Freshness Trend", format="%.2f"),
        "LAST_UPDATED": st.column_config.DatetimeColumn("Last Updated", format="YYYY-MM-DD HH:mm")
    },
    use_container_width=True,
    height=400
)

st.markdown("---")

# Brand drill-down section
st.subheader("Brand-Level Detail")

selected_account = st.selectbox(
    "Select an account to view brand details:",
    options=df_filtered['INSTANCE_ACCOUNT_ID'].tolist(),
    format_func=lambda x: f"Account {x} ({df_filtered[df_filtered['INSTANCE_ACCOUNT_ID']==x]['BRAND_COUNT'].values[0]} brands)"
)

if selected_account:
    with st.spinner(f"Loading brands for account {selected_account}..."):
        df_brands = get_brand_detail(session, selected_database, selected_account)

    # Display brand-level metrics
    st.markdown(f"### Account {selected_account} - Brand Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### AI Readiness by Brand")
        chart_data = df_brands[['INSTANCE_BRAND_ID', 'ARTICLE_AI_READINESS_VALUE']].copy()
        chart_data.columns = ['Brand ID', 'AI Readiness %']
        st.bar_chart(chart_data.set_index('Brand ID'))

    with col2:
        st.markdown("#### Content Coverage by Brand")
        chart_data = df_brands[['INSTANCE_BRAND_ID', 'CONTENT_COVERAGE_VALUE']].copy()
        chart_data.columns = ['Brand ID', 'Content Coverage %']
        st.bar_chart(chart_data.set_index('Brand ID'))

    # Detailed brand table
    st.markdown("#### Detailed Brand Metrics")

    df_brands_display = df_brands.copy()
    df_brands_display['ARTICLE_AI_READINESS_VALUE'] = df_brands_display['ARTICLE_AI_READINESS_VALUE'].round(1)
    df_brands_display['CONTENT_COVERAGE_VALUE'] = df_brands_display['CONTENT_COVERAGE_VALUE'].round(1)
    df_brands_display['ARTICLE_FRESHNESS_VALUE'] = df_brands_display['ARTICLE_FRESHNESS_VALUE'].round(1)

    st.dataframe(
        df_brands_display,
        column_config={
            "INSTANCE_BRAND_ID": st.column_config.NumberColumn("Brand ID", format="%d"),
            "ARTICLE_AI_READINESS_VALUE": st.column_config.NumberColumn("AI Readiness %", format="%.1f"),
            "ARTICLE_AI_READINESS_TREND": st.column_config.NumberColumn("AI Readiness Trend", format="%.2f"),
            "CONTENT_COVERAGE_VALUE": st.column_config.NumberColumn("Content Coverage %", format="%.1f"),
            "CONTENT_COVERAGE_TREND": st.column_config.NumberColumn("Coverage Trend", format="%.2f"),
            "ARTICLE_FRESHNESS_VALUE": st.column_config.NumberColumn("Article Freshness %", format="%.1f"),
            "ARTICLE_FRESHNESS_TREND": st.column_config.NumberColumn("Freshness Trend", format="%.2f"),
            "LAST_UPDATED": st.column_config.DatetimeColumn("Last Updated", format="YYYY-MM-DD HH:mm")
        },
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption(f"Data source: {region} region | Last refreshed: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
