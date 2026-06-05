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

# Query to get latest metrics aggregated by account with customer context
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
    SELECT
        am.*,
        pcu.INSTANCE_ACCOUNT_SUBDOMAIN,
        pcu.CRM_ACCOUNT_NAME,
        pcu.CRM_NET_ARR_USD,
        pcu.CRM_ARR_BAND_BROAD,
        pcu.CRM_REGION,
        pcu.CRM_TERRITORY_COUNTRY,
        pcu.CRM_MARKET_SEGMENT,
        pcu.CRM_INDUSTRY,
        pcu.SEATS_CAPACITY,
        pcu.SEATS_OCCUPIED,
        pcu.PRODUCT_MIX,
        pcu.CORE_BASE_PLAN,
        pcu.TOP_3000_FLAG,
        pcu.IS_LIVE
    FROM account_metrics am
    LEFT JOIN PROPAGATED_PRESENTATION.PRODUCT_ANALYTICS.PAID_CUSTOMER_UNIVERSE_DAILY_SNAPSHOT pcu
        ON am.instance_account_id = pcu.INSTANCE_ACCOUNT_ID
        AND pcu.IS_LATEST_DATE = TRUE
    ORDER BY am.instance_account_id
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

# Add filters in sidebar
st.sidebar.header("Filters")
arr_bands = ['All'] + sorted(df_accounts['CRM_ARR_BAND_BROAD'].dropna().unique().tolist())
selected_arr_band = st.sidebar.selectbox("ARR Band", arr_bands)

market_segments = ['All'] + sorted(df_accounts['CRM_MARKET_SEGMENT'].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox("Market Segment", market_segments)

industries = ['All'] + sorted(df_accounts['CRM_INDUSTRY'].dropna().unique().tolist())
selected_industry = st.sidebar.selectbox("Industry", industries)

# Add search box
search_term = st.text_input("🔍 Search by Account ID, Name, or Subdomain", "")

# Filter accounts based on search and filters
df_filtered = df_accounts.copy()

if search_term:
    df_filtered = df_filtered[
        df_filtered['INSTANCE_ACCOUNT_ID'].astype(str).str.contains(search_term, case=False, na=False) |
        df_filtered['CRM_ACCOUNT_NAME'].astype(str).str.contains(search_term, case=False, na=False) |
        df_filtered['INSTANCE_ACCOUNT_SUBDOMAIN'].astype(str).str.contains(search_term, case=False, na=False)
    ]

if selected_arr_band != 'All':
    df_filtered = df_filtered[df_filtered['CRM_ARR_BAND_BROAD'] == selected_arr_band]

if selected_segment != 'All':
    df_filtered = df_filtered[df_filtered['CRM_MARKET_SEGMENT'] == selected_segment]

if selected_industry != 'All':
    df_filtered = df_filtered[df_filtered['CRM_INDUSTRY'] == selected_industry]

# Format the dataframe for display
df_display = df_filtered.copy()
df_display['ARTICLE_AI_READINESS_VALUE'] = df_display['ARTICLE_AI_READINESS_VALUE'].round(1)
df_display['CONTENT_COVERAGE_VALUE'] = df_display['CONTENT_COVERAGE_VALUE'].round(1)
df_display['ARTICLE_FRESHNESS_VALUE'] = df_display['ARTICLE_FRESHNESS_VALUE'].round(1)
df_display['CRM_NET_ARR_USD'] = df_display['CRM_NET_ARR_USD'].round(0)
df_display['SEATS_CAPACITY'] = df_display['SEATS_CAPACITY'].round(0)
df_display['SEATS_OCCUPIED'] = df_display['SEATS_OCCUPIED'].round(0)

# Select and reorder columns for display
df_display = df_display[[
    'INSTANCE_ACCOUNT_ID',
    'CRM_ACCOUNT_NAME',
    'INSTANCE_ACCOUNT_SUBDOMAIN',
    'CRM_ARR_BAND_BROAD',
    'CRM_NET_ARR_USD',
    'CRM_MARKET_SEGMENT',
    'CRM_INDUSTRY',
    'CRM_TERRITORY_COUNTRY',
    'PRODUCT_MIX',
    'SEATS_CAPACITY',
    'BRAND_COUNT',
    'ARTICLE_AI_READINESS_VALUE',
    'CONTENT_COVERAGE_VALUE',
    'ARTICLE_FRESHNESS_VALUE',
    'TOP_3000_FLAG',
    'IS_LIVE'
]]

# Rename columns for better display
df_display = df_display.rename(columns={
    'INSTANCE_ACCOUNT_ID': 'Account ID',
    'CRM_ACCOUNT_NAME': 'Company Name',
    'INSTANCE_ACCOUNT_SUBDOMAIN': 'Subdomain',
    'CRM_ARR_BAND_BROAD': 'ARR Band',
    'CRM_NET_ARR_USD': 'ARR ($)',
    'CRM_MARKET_SEGMENT': 'Segment',
    'CRM_INDUSTRY': 'Industry',
    'CRM_TERRITORY_COUNTRY': 'Country',
    'PRODUCT_MIX': 'Product Mix',
    'SEATS_CAPACITY': 'Seats',
    'BRAND_COUNT': '# Brands',
    'ARTICLE_AI_READINESS_VALUE': 'AI Readiness %',
    'CONTENT_COVERAGE_VALUE': 'Coverage %',
    'ARTICLE_FRESHNESS_VALUE': 'Freshness %',
    'TOP_3000_FLAG': 'Top 3000',
    'IS_LIVE': 'Live'
})

# Display the table
st.dataframe(df_display, use_container_width=True, height=400)

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
    df_brands_display['ARTICLE_AI_READINESS_TREND'] = df_brands_display['ARTICLE_AI_READINESS_TREND'].round(2)
    df_brands_display['CONTENT_COVERAGE_TREND'] = df_brands_display['CONTENT_COVERAGE_TREND'].round(2)
    df_brands_display['ARTICLE_FRESHNESS_TREND'] = df_brands_display['ARTICLE_FRESHNESS_TREND'].round(2)

    # Rename columns for better display
    df_brands_display = df_brands_display.rename(columns={
        'INSTANCE_BRAND_ID': 'Brand ID',
        'ARTICLE_AI_READINESS_VALUE': 'AI Readiness %',
        'ARTICLE_AI_READINESS_TREND': 'AI Readiness Trend',
        'CONTENT_COVERAGE_VALUE': 'Content Coverage %',
        'CONTENT_COVERAGE_TREND': 'Coverage Trend',
        'ARTICLE_FRESHNESS_VALUE': 'Article Freshness %',
        'ARTICLE_FRESHNESS_TREND': 'Freshness Trend',
        'LAST_UPDATED': 'Last Updated'
    })

    st.dataframe(df_brands_display, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"Data source: {region} region | Last refreshed: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
