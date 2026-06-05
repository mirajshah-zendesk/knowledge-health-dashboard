# Deployment Summary

## ✅ Successfully Deployed to Snowflake!

The Knowledge Base Health Dashboard has been successfully deployed to both regional Snowflake accounts.

### Deployment Details

| Region | Status | URL |
|--------|--------|-----|
| **AMER** | ✅ Deployed | https://app.snowflake.com/ZENDESK/amer/#/streamlit-apps/_SANDBOX_ENTERPRISE_METRICS_STREAMLIT.PUBLIC.KNOWLEDGE_HEALTH_DASHBOARD |
| **EMEA** | ✅ Deployed | https://app.snowflake.com/ZENDESK/emea/#/streamlit-apps/_SANDBOX_ENTERPRISE_METRICS_STREAMLIT.PUBLIC.KNOWLEDGE_HEALTH_DASHBOARD |

### Database Configuration

- **Database**: `_SANDBOX_ENTERPRISE_METRICS_STREAMLIT`
- **Schema**: `PUBLIC`
- **Role**: `_SANDBOX_ENTERPRISE_METRICS_STREAMLIT_ROLE`
- **Warehouse**: `PUBLIC_ZENDESK_XS`

### Source Code

- **GitHub Repository**: https://github.com/mirajshah-zendesk/knowledge-health-dashboard
- **Main File**: `app.py`
- **Config**: `snowflake.yml`

## Features Deployed

✅ **Region Selection** - Toggle between AMER and EMEA data  
✅ **Account-Level Summary** - Aggregated metrics across all accounts  
✅ **Search & Filter** - Find accounts by ID  
✅ **Brand Drill-Down** - View detailed metrics for each brand within an account  
✅ **Visual Charts** - Bar charts for brand-level comparisons  
✅ **Trend Indicators** - See how metrics change over time  

## Data Source

The dashboard queries: `CLEANSED.PRODUCT_ML_SCIENCE.KNOWLEDGE_HEALTH_METRICS`

**Metrics:**
- **AI Readiness**: Percentage of articles ready for AI usage
- **Content Coverage**: Coverage of content across the knowledge base  
- **Article Freshness**: Recency/freshness of articles

## How to Access

1. Navigate to one of the URLs above
2. Log in with your Zendesk Snowflake credentials (SSO)
3. The dashboard will load automatically

## Updating the Dashboard

To update the deployed app:

```bash
cd ~/knowledge-health-dashboard

# Make your changes to app.py

# Deploy to AMER
snow streamlit deploy --connection ZENDESK-AMER --replace

# Deploy to EMEA
snow streamlit deploy --connection ZENDESK-EMEA --replace

# Commit and push to GitHub
git add -A
git commit -m "Your update message"
git push
```

## Permissions

Users need:
- Access to the ZENDESK-AMER or ZENDESK-EMEA Snowflake account
- `SELECT` permissions on `CLEANSED.PRODUCT_ML_SCIENCE.KNOWLEDGE_HEALTH_METRICS`
- Access to the Streamlit app (granted via role permissions)

## Next Steps

Consider:
- Adding filters for specific date ranges
- Exporting capabilities for reports
- Email/Slack notifications for threshold alerts
- Historical trend charts over time
- Comparison views between AMER and EMEA

## Support

For issues or feature requests:
- GitHub Issues: https://github.com/mirajshah-zendesk/knowledge-health-dashboard/issues
- Contact: miraj.shah@zendesk.com
