import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# -------------------------
# CONFIGURATION
# -------------------------
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="PocketFlow", layout="wide")

# -------------------------
# SESSION STATE
# -------------------------
if "token" not in st.session_state:
    st.session_state["token"] = None

# -------------------------
# AUTH FUNCTIONS (UNTOUCHED)
# -------------------------
def login():
    st.title("🔒 Login to PocketFlow")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        data = {"username": username, "password": password}
        try:
            res = requests.post(f"{API_URL}/token", data=data)
            if res.status_code == 200:
                st.session_state["token"] = res.json()["access_token"]
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
        except Exception as e:
            st.error(f"Could not connect to server: {e}")

def register():
    st.title("📝 Create Account")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    
    if st.button("Register"):
        try:
            res = requests.post(f"{API_URL}/register", json={"username": new_user, "hashed_password": new_pass})
            if res.status_code == 200:
                st.success("Account created! Please go to Login.")
            else:
                st.error("Username already taken.")
        except Exception as e:
            st.error(f"Could not connect to server: {e}")

# -------------------------
# MAIN APP (UPGRADED)
# -------------------------
def main_app():
    # 1. HEADER & LOGOUT
    col1, col2 = st.columns([9, 1])
    col1.title("💸 PocketFlow Dashboard")
    if col2.button("Logout"):
        st.session_state["token"] = None
        st.rerun()

    auth_headers = {"Authorization": f"Bearer {st.session_state['token']}"}

    # 2. FETCH DATA (Get everything first, filter later)
    try:
        trans_res = requests.get(f"{API_URL}/transactions/", headers=auth_headers)
        trans_data = trans_res.json()
        df = pd.DataFrame(trans_data)
    except Exception:
        st.error("Failed to connect to the server.")
        st.stop()

    # -------------------------
    # 3. SIDEBAR CONTROLS
    # -------------------------
    st.sidebar.header("🕹️ Filters")
    
    # A. Date Filter
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])  # Convert to proper datetime
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        
        date_range = st.sidebar.date_input(
            "Filter by Date", 
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # B. Category Filter
    selected_categories = st.sidebar.multiselect(
        "Filter by Category", 
        options=["Food", "Travel", "Education", "Salary", "Entertainment"],
        default=[] # Empty means "Show All"
    )

    st.sidebar.divider()

    # C. ADD TRANSACTION (Moved to Expander to save space)
    with st.sidebar.expander("➕ Add Transaction", expanded=False):
        with st.form("add_form"):
            title = st.text_input("Title")
            amount = st.number_input("Amount", min_value=1.0)
            category = st.selectbox("Category", ["Food", "Travel", "Education", "Salary", "Entertainment"])
            t_type = st.selectbox("Type", ["expense", "income"])
            if st.form_submit_button("Add"):
                new_data = {"title": title, "amount": amount, "category": category, "type": t_type}
                requests.post(f"{API_URL}/transactions/", json=new_data, headers=auth_headers)
                st.rerun()

    # D. DELETE TRANSACTION (Moved to Expander)
    with st.sidebar.expander("🗑️ Delete Transaction", expanded=False):
        del_id = st.number_input("ID to Delete", min_value=1, step=1)
        if st.button("Delete"):
            res = requests.delete(f"{API_URL}/transactions/{del_id}", headers=auth_headers)
            if res.status_code == 200:
                st.sidebar.success(f"ID {del_id} deleted!")
                st.rerun()
            else:
                st.sidebar.error("ID not found.")

    # -------------------------
    # 4. FILTERING LOGIC
    # -------------------------
    if not df.empty:
        # Filter by Date
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
            df = df.loc[mask]

        # Filter by Category
        if selected_categories:
            df = df[df["category"].isin(selected_categories)]

    # -------------------------
    # 5. DYNAMIC DASHBOARD
    # -------------------------
    if not df.empty:
        # Calculate Metrics based on FILTERED data
        total_income = df[df["type"] == "income"]["amount"].sum()
        total_expense = df[df["type"] == "expense"]["amount"].sum()
        current_balance = total_income - total_expense

        # Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Net Balance", f"₹{current_balance:,.0f}")
        m2.metric("Total Income", f"₹{total_income:,.0f}", delta="Income")
        m3.metric("Total Expense", f"₹{total_expense:,.0f}", delta="-Expense", delta_color="inverse")

        # Main Layout: Charts & Table
        st.divider()
        c1, c2 = st.columns([6, 4])
        
        with c1:
            st.subheader("📊 Spending Analysis")
            expenses = df[df["type"] == "expense"]
            if not expenses.empty:
                fig = px.pie(expenses, values="amount", names="category", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                # Custom Tooltip: Bold Label + Rupee Amount
                fig.update_traces(hovertemplate="<b>%{label}</b><br>₹%{value:,}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expenses in this date range.")

        with c2:
            st.subheader("📜 Recent Transactions")
            # Showing ID so you know what to delete
            st.dataframe(
                df[["id", "date", "title", "amount", "type"]].sort_values(by="date", ascending=False), 
                use_container_width=True,
                hide_index=True
            )
            
            # CSV Export Button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Filtered Data",
                data=csv,
                file_name="pocketflow_data.csv",
                mime="text/csv",
            )

    else:
        st.info("No transactions found. Add one in the sidebar!")

# -------------------------
# ROUTING
# -------------------------
if __name__ == "__main__":
    if st.session_state["token"]:
        main_app()
    else:
        choice = st.sidebar.radio("Menu", ["Login", "Register"])
        if choice == "Login":
            login()
        else:
            register()


# run with-->  " streamlit run dashboard.py " 