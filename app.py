import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Supplier Bid Optimization Engine", layout="wide")

# Safety check for the logo image
if os.path.exists("skf.png"):
    st.image("skf.png", width=200)
else:
    st.warning("Logo 'skf.png' not found. Please ensure it is in the same directory.")

st.header("Supplier Bid Optimization Engine")
st.markdown("Evaluate raw material suppliers based on Total Cost of Ownership (TCO), factoring in hidden risks like defects and lead times.")


# Initialize tabs
tab1, tab2, tab3 = st.tabs(["Home", "Dashboard", "About"])

# ==========================================
# 2. THE CORE ENGINE (From Phase 1)
# ==========================================
def calculate_tco(df, target_item, quantity, cost_per_defect, penalty_per_day):
    bids = df[df["description"] == target_item].copy()
    
    if bids.empty:
        return bids # Return empty dataframe if no match

    bids["Base_Cost"] = bids["unit_price_inr"] * quantity
    bids["Defect_Cost"] = (bids["defect_rate_pct"] / 100) * quantity * cost_per_defect
    bids["Lead_Time_Penalty"] = bids["lead_time_days"] * penalty_per_day

    bids["TCO"] = (
        bids["Base_Cost"] +
        bids["logistics_cost_inr"] +
        bids["Defect_Cost"] +
        bids["Lead_Time_Penalty"]
    )

    bids = bids.sort_values(by='TCO', ascending=True).reset_index(drop=True)
    bids['Rank'] = bids.index + 1
    return bids

# ==========================================
# 3. LOAD DATA 
# ==========================================
# st.cache_data prevents the app from reloading the CSV every time you move a slider
@st.cache_data
def load_data():
    return pd.read_csv("Dataset.csv")

try:
    raw_bids = load_data()
except FileNotFoundError:
    st.error("Error: Could not find 'Dataset.csv'. Please ensure it is in the same folder as app.py.")
    st.stop()

# ==========================================
# 4. SIDEBAR USER INTERFACE (The "What-If" Sliders)
# ==========================================
st.sidebar.title("Scenario Parameters")

# Dynamically pull all unique items from your CSV for the dropdown
available_items = raw_bids["description"].unique()
target_item = st.sidebar.selectbox("Select Item Description:", available_items)

# Sliders for dynamic scenario modeling
order_quantity = st.sidebar.number_input("Order Quantity", min_value=100, max_value=100000, value=1000, step=100)
cost_per_defect = st.sidebar.slider("Cost per Defect (INR)", min_value=0.0, max_value=500.0, value=50.0, step=10.0)
penalty_per_day = st.sidebar.slider("Lead Time Penalty / Day (INR)", min_value=0.0, max_value=1000.0, value=100.0, step=50.0)
st.sidebar.info(f"Total Defect Cost: ₹{order_quantity * cost_per_defect:,.2f}")

# ==========================================
# 5. EXECUTION & VISUALIZATION
# ==========================================
optimized_bids = calculate_tco(raw_bids, target_item, order_quantity, cost_per_defect, penalty_per_day)

# --- TAB 1: HOME ---
with tab1:
    if not optimized_bids.empty:
        st.write(f"**Item Description:** {target_item}")
        
        # Display the winning supplier prominently
        winner = optimized_bids.iloc[0]
        st.success(f"🏆 **Recommended Supplier:** {winner['supplier_name']} (TCO: ₹{winner['TCO']:,.2f})")

        st.markdown("**Top 10 Bid Analysis**")
        # Display the dataframe cleanly
        display_cols = ['Rank', 'supplier_name', 'Base_Cost', 'TCO']
        st.dataframe(optimized_bids[display_cols].head(10), hide_index=True)

        st.markdown("**Cost Breakdown by Supplier (Base Cost vs TCO)**")
        # Prepare data for a clean bar chart
        chart_data = optimized_bids.set_index('supplier_name')[['Base_Cost', 'TCO']]
        st.bar_chart(chart_data)
            
    else:
        st.warning("No data found for this item.")

# --- TAB 2: DASHBOARD ---
with tab2:
    st.info("You can add additional analytical charts or data here in the future.")

# --- TAB 3: ABOUT ---
with tab3:
    st.info("You can add your project methodology, TCO formula explanations, or your portfolio links here.")