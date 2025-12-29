import streamlit as st
import pandas as pd
import pickle
import time

# --------------------------
# Page Config
# --------------------------
st.set_page_config(page_title="SafeClaim AI", page_icon="🚛", layout="wide")

# --------------------------
# Professional CSS Styling
# --------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        color: #ff6f61;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Session State Initialization
# --------------------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "menu_option" not in st.session_state:
    st.session_state.menu_option = "🏠 Home"
if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------
# Load Model with Caching (Unique Improvement)
# --------------------------
@st.cache_resource
def load_assets():
    try:
        m = pickle.load(open("best_model.pkl", "rb"))
        s = pickle.load(open("scaler.pkl", "rb"))
        f = pickle.load(open("feature_names.pkl", "rb"))
        return m, s, f
    except:
        return None, None, None

model, scaler, feature_names = load_assets()

# --------------------------
# Authentication UI
# --------------------------
def auth_gate():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🛡️ SafeClaim AI")
        mode = st.tabs(["Login", "Sign Up"])
        with mode[0]:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("Access Portal", use_container_width=True):
                if u in st.session_state.users and st.session_state.users[u] == p:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
        with mode[1]:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Register Now", use_container_width=True):
                st.session_state.users[nu] = np
                st.success("Registration Successful! Please switch to Login.")

# --------------------------
# Main Application Content
# --------------------------
if not st.session_state.logged_in:
    auth_gate()
else:
    # Sidebar
    st.sidebar.title("🧭 Control Center")
    menu_list = ["🏠 Home", "🔮 Predict Claim", "📊 Analytics", "📞 Contact", "🚪 Logout"]
    st.session_state.menu_option = st.sidebar.radio("Go to:", menu_list, index=menu_list.index(st.session_state.menu_option))

    # --- Home Page ---
    if st.session_state.menu_option == "🏠 Home":
        st.title("Vehicle Insurance Intelligence Dashboard")
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Current User", st.session_state.get('login_u', 'User'))
        c2.metric("System Health", "Optimal")
        c3.metric("Predictions Today", len(st.session_state.history))
        
        st.write("## Get started with a new analysis")
        if st.button("🚀 Start Predict Claim", use_container_width=True):
            st.session_state.menu_option = "🔮 Predict Claim"
            st.rerun()

    # --- Prediction Page ---
    elif st.session_state.menu_option == "🔮 Predict Claim":
        st.title("🔮 Claim Forecasting Engine")
        
        with st.form("input_form"):
            st.markdown("### Step 1: Input Customer & Vehicle Data")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                age = st.slider("Driver Age", 18, 100, 30)
                income = st.number_input("Annual Income (₹)", 10000, 1000000, 50000)
            
            with col2:
                premium = st.number_input("Monthly Premium (₹)", 50, 5000, 150)
                dependents = st.selectbox("Number of Dependents", [0, 1, 2, 3, 4, 5])
            
            with col3:
                gender = st.selectbox("Driver Gender", ["Male", "Female"])
                # ADDED 6, 8, 12 WHEELERS HERE
                v_type = st.selectbox("Vehicle Category", [
                    "2-Wheeler", "Sedan", "SUV", "Hatchback", "Luxury", 
                    "6 Wheeler (Truck/Bus)", "8 Wheeler (Heavy)", "12 Wheeler (Commercial)",
                    "Electric", "Pickup"
                ])

            predict_btn = st.form_submit_button("Generate Prediction Report")

        if predict_btn:
            with st.spinner("Analyzing insurance risk factors..."):
                time.sleep(1) # Visual effect
                
                # Logic: Prep data
                input_df = pd.DataFrame({
                    "Age": [age], "Income": [income], "Monthly.Premium.Auto": [premium],
                    "Dependents": [dependents], "Gender": [gender], "Vehicle_Type": [v_type]
                })
                input_df = pd.get_dummies(input_df, drop_first=True)
                for col in feature_names:
                    if col not in input_df.columns: input_df[col] = 0
                input_df = input_df[feature_names]
                
                # Predict
                result = model.predict(scaler.transform(input_df))[0]
                
                # Unique Result Display
                st.markdown("---")
                st.metric(label="Estimated Claim Amount", value=f"₹ {result:,.2f}")
                st.progress(min(result/10000, 1.0)) # Visual Gauge
                
                # Save to History
                st.session_state.history.append({"Vehicle": v_type, "Claim": result, "Date": time.strftime("%H:%M")})
                st.balloons()

    # --- Analytics Page ---
    elif st.session_state.menu_option == "📊 Analytics":
        st.title("📊 Data Insights & History")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            st.subheader("Claim Trends (Current Session)")
            st.line_chart(df.set_index("Date")["Claim"])
            st.subheader("Historical Log")
            st.table(df)
        else:
            st.info("No prediction data available yet. Please complete a prediction first.")

    # --- Contact Page ---
    elif st.session_state.menu_option == "📞 Contact":
        st.title("📞 Contact Support")
        st.success("Lead Developer: **Bhoomika Sairigapu**")
        st.write("📱 **Phone:** +91 7815873045")
        st.write("📧 **Email:** bhoomikasairigapu@gmail.com")
        st.info("Available for technical consultation and model fine-tuning.")

    # --- Logout ---
    elif st.session_state.menu_option == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.menu_option = "🏠 Home"
        st.rerun()