import streamlit as st
import pandas as pd
import pickle
import os
import time

# --------------------------
# 1. PERMANENT DATABASE SETUP
# --------------------------
DB_FILE = "user_data.pkl"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            return pickle.load(f)
    return {"admin": "admin123"}

def save_to_db(username, password):
    db = load_db()
    db[username] = password
    with open(DB_FILE, "wb") as f:
        pickle.dump(db, f)

# --------------------------
# 2. SESSION INITIALIZATION
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "history" not in st.session_state:
    st.session_state.history = []
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

# --------------------------
# 3. PERMANENT CSS STYLING
# --------------------------
st.markdown("""
    <style>
    /* Professional Light Mode Gradient */
    .stApp { 
        background: linear-gradient(to bottom, #d9e2ec 0%, #f0f4f8 100%); 
        color: #334155; 
    }
    
    /* Fixed Floating Navigation Bar (Bottom Right) */
    .fixed-nav {
        position: fixed;
        bottom: 30px;
        right: 30px;
        display: flex;
        gap: 15px;
        z-index: 1000;
        background: #ffffff;
        padding: 10px 20px;
        border-radius: 50px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        border: 1px solid #cbd5e1;
    }

    /* Form Container Styling */
    [data-testid="stForm"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }

    /* Professional Button Styling */
    button[kind="secondary"], button[kind="primary"], .stButton > button, .stDownloadButton > button {
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    /* Global Typography */
    h1, h2, h3, p, label { color: #334155 !important; }
    </style>
""", unsafe_allow_html=True)

# --------------------------
# 4. AUTHENTICATION UI
# --------------------------
if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🛡️ SafeClaim AI</h1>", unsafe_allow_html=True)
        auth_tab = st.tabs(["🔒 Login", "📝 Sign Up"])
        with auth_tab[0]:
            u = st.text_input("Username", key="auth_u")
            p = st.text_input("Password", type="password", key="auth_p")
            if st.button("Access Portal", use_container_width=True):
                users = load_db()
                if u in users and users[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
        with auth_tab[1]:
            nu = st.text_input("New Username", key="reg_u")
            np = st.text_input("New Password", type="password", key="reg_p")
            if st.button("Register Account", use_container_width=True):
                if nu and np:
                    save_to_db(nu, np)
                    st.success("Account saved permanently! Please Login.")

# --------------------------
# 5. MAIN PORTAL CONTENT
# --------------------------
else:
    nav_options = ["🏠 Home", "🔮 Predict Claim", "📊 Monitor", "📞 Support"]
    
    # Sidebar
    st.sidebar.title(f"👤 {st.session_state.current_user}")
    menu = st.sidebar.radio("Navigation", nav_options, index=st.session_state.page_index)
    st.session_state.page_index = nav_options.index(menu)

    # Permanent Logout Button at Sidebar Bottom
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.page_index = 0
        st.rerun()

    # --- FLOATING NAV (Bottom Right) ---
    st.markdown('<div class="fixed-nav">', unsafe_allow_html=True)
    c_back, c_next = st.columns(2)
    with c_back:
        if st.button("⬅️ Back") and st.session_state.page_index > 0:
            st.session_state.page_index -= 1
            st.rerun()
    with c_next:
        if st.button("Next ➡️") and st.session_state.page_index < len(nav_options) - 1:
            st.session_state.page_index += 1
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- PAGES ---
    if menu == "🏠 Home":
        st.markdown("<h1 style='font-size: 40px;'>Welcome to SafeClaim AI</h1>", unsafe_allow_html=True)
        st.markdown("### Check, submit, and monitor your vehicle insurance claims with ease.")
        st.markdown("---")
        if st.button("🚀 Start Predict Claim Analysis", use_container_width=True):
            st.session_state.page_index = 1
            st.rerun()

    elif menu == "🔮 Predict Claim":
        st.markdown("<h1>🔮 Claim Forecasting Engine</h1>", unsafe_allow_html=True)
        with st.form("claim_form"):
            st.markdown("### Step 1: Input Customer & Vehicle Data")
            col1, col2, col3 = st.columns(3)
            with col1:
                age = st.slider("Driver Age", 18, 100, 36)
                income = st.number_input("Annual Income (₹)", value=60000)
            with col2:
                premium = st.number_input("Monthly Premium (₹)", value=150)
                dep = st.selectbox("Number of Dependents", [0,1,2,3,4,5], index=3)
            with col3:
                gen = st.selectbox("Driver Gender", ["Male", "Female", "Other"])
                v_list = ["2-Wheeler", "Cars", "Luxury Cars", "Bikes", "Trucks", "Electric Vehicles", "Aeroplanes"]
                v_type = st.selectbox("Vehicle Category", v_list)
            
            submit_btn = st.form_submit_button("Generate Prediction Report")

        if submit_btn:
            res = (premium * 1.5) + (income * 0.01)
            entry = {"Date": time.strftime("%H:%M"), "Vehicle": v_type, "Amount": f"₹{res:,.2f}"}
            st.session_state.history.append(entry)
            
            st.success(f"### Predicted Claim Amount: ₹{res:,.2f}")
            
            # Save & Print Buttons
            st.markdown("---")
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("💾 Save to History"):
                    st.toast("Claim Saved!")
            with b_col2:
                csv = pd.DataFrame([entry]).to_csv(index=False).encode('utf-8')
                st.download_button("🖨️ Print Receipt", csv, f"Receipt_{v_type}.csv", "text/csv")
            st.balloons()

    elif menu == "📊 Monitor":
        st.title("📊 Monitoring History")
        if st.session_state.history:
            st.table(pd.DataFrame(st.session_state.history))
        else:
            st.info("No claims recorded yet.")

    elif menu == "📞 Support":
        st.title("📞 Contact Support")
        st.write("Lead Developer: **Bhoomika Sairigapu**")
        st.write("📱 +91 7815873045 | 📧 bhoomikasairigapu@gmail.com")
