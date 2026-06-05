# Deployment Instructions for Knowledge Health Dashboard

## Deploying Streamlit Apps to Snowflake

Snowflake Streamlit apps must be deployed through **Snowsight UI** or **Snowflake CLI**. They cannot be created via SQL commands through the Python connector.

## Option 1: Deploy via Snowsight UI (Recommended)

### For AMER Account:

1. **Open Snowsight**: Navigate to your AMER Snowflake account in a web browser
   - URL format: `https://app.snowflake.com/REGION/ACCOUNT_LOCATOR`

2. **Navigate to Streamlit**:
   - Click on "Streamlit" in the left sidebar
   - Click "+ Streamlit App" button

3. **Configure the App**:
   - **Name**: `KNOWLEDGE_HEALTH_DASHBOARD`
   - **Warehouse**: `PUBLIC_ZENDESK_XS` (or appropriate warehouse)
   - **App location**: 
     - Database: `_SANDBOX_ENTERPRISE_METRICS_STREAMLIT` or `PRESENTATION`
     - Schema: `PUBLIC`

4. **Add the Code**:
   - Copy the entire contents of `app.py`
   - Paste into the Streamlit editor

5. **Run the App**:
   - Click the "Run" button in the top right
   - The app should load and connect to your data

6. **Share** (optional):
   - Click the "Share" button to grant access to other users
   - Set appropriate permissions

### For EMEA Account:

Repeat the same steps in the EMEA Snowflake account.

---

## Option 2: Deploy via Snowflake CLI

### Prerequisites:
```bash
# Install Snowflake CLI
pip install snowflake-cli-labs

# Configure connection
snow connection add amer
```

### Deploy Command:
```bash
cd ~/knowledge-health-dashboard

# Deploy to AMER
snow streamlit deploy \
  --connection amer \
  --database _SANDBOX_ENTERPRISE_METRICS_STREAMLIT \
  --schema PUBLIC \
  --name KNOWLEDGE_HEALTH_DASHBOARD \
  --file app.py \
  --warehouse PUBLIC_ZENDESK_XS

# Deploy to EMEA
snow streamlit deploy \
  --connection emea \
  --database _SANDBOX_ENTERPRISE_METRICS_STREAMLIT \
  --schema PUBLIC \
  --name KNOWLEDGE_HEALTH_DASHBOARD \
  --file app.py \
  --warehouse PUBLIC_ZENDESK_XS
```

---

## Post-Deployment

### Access URLs:
After deployment, your app will be accessible at:
- **AMER**: `https://app.snowflake.com/REGION/ACCOUNT/#/streamlit-apps/KNOWLEDGE_HEALTH_DASHBOARD`
- **EMEA**: `https://app.snowflake.com/REGION/ACCOUNT/#/streamlit-apps/KNOWLEDGE_HEALTH_DASHBOARD`

### Permissions:
Grant access to users/roles:
```sql
GRANT USAGE ON STREAMLIT KNOWLEDGE_HEALTH_DASHBOARD TO ROLE <ROLE_NAME>;
```

### Required Permissions:
The app requires:
- `SELECT` on `CLEANSED.PRODUCT_ML_SCIENCE.KNOWLEDGE_HEALTH_METRICS`
- `USAGE` on `CLEANSED` database and `PRODUCT_ML_SCIENCE` schema
- `USAGE` on the warehouse

---

## Troubleshooting

### If the app doesn't load:
1. Check that you have permissions on the source table
2. Verify the warehouse is running
3. Check the Streamlit logs in Snowsight

### If queries are slow:
1. Consider using a larger warehouse
2. Add indexes or materialized views if needed
3. Adjust the `ttl` in `@st.cache_data` decorators

### If you see authentication errors:
1. Ensure `get_active_session()` is being used (not manual connection)
2. Verify your role has access to the data

---

## Manual Deployment via Snowsight

Since programmatic deployment requires special CLI tools or API access that may not be available, the **Snowsight UI method (Option 1) is the most straightforward approach**.

The app code is ready to go in `app.py` - simply copy and paste it into the Streamlit editor in Snowsight.
