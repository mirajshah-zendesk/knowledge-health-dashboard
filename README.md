# Knowledge Base Health Dashboard

A Streamlit dashboard for monitoring knowledge base health metrics across Zendesk accounts and brands in regional databases (AMER and EMEA).

## Features

- **Region Selection**: Toggle between AMER and EMEA regions
- **Account-Level Summary**: View aggregated metrics across all accounts
  - AI Readiness %
  - Content Coverage %
  - Article Freshness %
  - Brand count per account
- **Brand-Level Drill-Down**: Select an account to view detailed metrics for each brand
- **Search & Filter**: Quickly find accounts by ID
- **Visual Charts**: Bar charts for brand-level metric comparisons
- **Trend Indicators**: See how metrics are trending over time

## Data Source

The dashboard queries `CLEANSED.PRODUCT_ML_SCIENCE.KNOWLEDGE_HEALTH_METRICS` table which contains:
- `article_ai_readiness`: Percentage of articles ready for AI usage
- `content_coverage`: Coverage of content across the knowledge base
- `article_freshness`: Freshness/recency of articles

## Deployment

This app is designed to be deployed in Snowflake Streamlit (Streamlit in Snowflake).

### Prerequisites
- Access to ZENDESK-AMER or ZENDESK-EMEA Snowflake accounts
- Permissions to read from `CLEANSED.PRODUCT_ML_SCIENCE.KNOWLEDGE_HEALTH_METRICS`

### Deploy to Snowflake

1. Navigate to Snowsight in your regional Snowflake account (AMER or EMEA)
2. Go to Streamlit Apps
3. Create a new Streamlit app
4. Upload `app.py` and set the appropriate database and schema
5. The app will automatically use the active Snowflake session

## Local Development

To run locally (requires Snowflake connection):

```bash
pip install -r requirements.txt
streamlit run app.py
```

Note: Local development requires configuring Snowflake connection credentials.

## Table Structure

The source table has the following grain:
- Primary Key: `(instance_account_id, instance_brand_id, metric_id, created_at)`
- Multiple snapshots per account/brand/metric combination
- Dashboard uses `ROW_NUMBER()` with `QUALIFY` to get the latest snapshot

## Version History

- v1.0 (2026-06-05): Initial release with account and brand-level views
