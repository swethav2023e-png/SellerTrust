# ---------------- IMPORTS ----------------
import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pyrebase

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Trust AI", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#1a1f71,#6a11cb,#8e44ad);
}
.stButton button {
    background: linear-gradient(90deg,#6a11cb,#8e44ad);
    color:white;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FIREBASE CONFIG ----------------
firebaseConfig = {
    "apiKey": "AIzaSyA3F3rEHiSU2bEJCLb-aEoENhok4Oss8BA",
    "authDomain": "sellertrustai.firebaseapp.com",
    "projectId": "sellertrustai",
    "storageBucket": "sellertrustai.firebasestorage.app",
    "messagingSenderId": "907138478207",
    "appId": "1:907138478207:web:163b63dcdeea2214eacf4a",
    "measurementId": "G-YG0BGFM7RV",

    # 🔥 ADD THIS LINE (IMPORTANT)
    "databaseURL": ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ---------------- SESSION ----------------
if "logged" not in st.session_state:
    st.session_state.logged = False

# ---------------- LOGIN ----------------
if not st.session_state.logged:

    st.title("🔐 Smart Trust AI Login")

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    col1, col2 = st.columns(2)

    # LOGIN BUTTON
    with col1:
        if st.button("Login"):
            try:
                auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged = True
                st.success("Login successful")
                st.rerun()
            except:
                st.error("Invalid email or password")

    # REGISTER BUTTON
    with col2:
        if st.button("Register"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created! Please login.")
            except:
                st.error("User exists or weak password")

    st.stop()
    

# ---------------- LOGOUT ----------------
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged = False
    st.rerun()

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- FAKE PRODUCT ANALYSIS ----------------
def analyze_product(url):
    return {
        "prices": {
            "Amazon": random.randint(800,1500),
            "Flipkart": random.randint(700,1400),
            "Meesho": random.randint(600,1300)
        },
        "reviews": {
            "Amazon": random.randint(70,95),
            "Flipkart": random.randint(60,90),
            "Meesho": random.randint(50,85)
        },
        "features": (
            random.randint(10,70),
            random.randint(0,10),
            random.randint(60,95),
            random.randint(3,10)
        )
    }

# ---------------- FUZZY LOGIC ----------------
def calculate_trust(d,c,r,e):

    delay = ctrl.Antecedent(np.arange(0,101,1),'delay')
    complaints = ctrl.Antecedent(np.arange(0,11,1),'complaints')
    consistency = ctrl.Antecedent(np.arange(0,101,1),'consistency')
    experience = ctrl.Antecedent(np.arange(0,11,1),'experience')

    trust = ctrl.Consequent(np.arange(0,101,1),'trust')

    delay['low'] = fuzz.trimf(delay.universe,[0,0,30])
    delay['high'] = fuzz.trimf(delay.universe,[60,100,100])

    complaints['low'] = fuzz.trimf(complaints.universe,[0,0,3])
    complaints['high'] = fuzz.trimf(complaints.universe,[5,10,10])

    consistency['good'] = fuzz.trimf(consistency.universe,[70,100,100])
    consistency['poor'] = fuzz.trimf(consistency.universe,[0,0,50])

    experience['high'] = fuzz.trimf(experience.universe,[5,10,10])

    trust['low'] = fuzz.trimf(trust.universe,[0,0,40])
    trust['medium'] = fuzz.trimf(trust.universe,[40,60,80])
    trust['high'] = fuzz.trimf(trust.universe,[70,100,100])

    rules = [
        ctrl.Rule(delay['low'] & complaints['low'], trust['high']),
        ctrl.Rule(delay['high'] | complaints['high'], trust['low']),
        ctrl.Rule(consistency['good'], trust['high']),
        ctrl.Rule(consistency['poor'], trust['low']),
        ctrl.Rule(experience['high'], trust['high'])
    ]

    system = ctrl.ControlSystem(rules)
    sim = ctrl.ControlSystemSimulation(system)

    sim.input['delay'] = d
    sim.input['complaints'] = c
    sim.input['consistency'] = r
    sim.input['experience'] = e

    sim.compute()

    return sim.output['trust']

# ---------------- MAIN UI ----------------
st.title("💜 Smart Trust AI Dashboard")

col1, col2 = st.columns(2)

with col1:
    url = st.text_input("🔗 Paste Product URL")

with col2:
    delay = st.slider("Delivery Delay", 0, 100, 20)
    complaints = st.slider("Complaints", 0, 10, 1)
    consistency = st.slider("Consistency", 0, 100, 80)
    experience = st.slider("Experience", 0, 10, 5)

# ---------------- ANALYZE ----------------
if st.button("🚀 Analyze Product"):

    with st.spinner("Analyzing product..."):
        time.sleep(2)

    if url:
        data = analyze_product(url)
        d, c, r, e = data["features"]
        prices = data["prices"]
        reviews = data["reviews"]
    else:
        d, c, r, e = delay, complaints, consistency, experience
        prices = {"Amazon":1000,"Flipkart":950,"Meesho":900}
        reviews = {"Amazon":80,"Flipkart":75,"Meesho":70}

    score = calculate_trust(d,c,r,e)

    # Save history
    st.session_state.history.append({
        "Score": round(score,2),
        "Complaints": c
    })

    # ---------------- RESULTS ----------------
    st.subheader("📊 Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Trust Score", round(score,2))
    c2.metric("Consistency", r)
    c3.metric("Complaints", c)

    st.progress(int(score))

    # ---------------- CIRCULAR METER ----------------
    st.subheader("🎯 Trust Meter")

    st.markdown(f"""
    <div style='text-align:center'>
        <svg width="200" height="200">
            <circle cx="100" cy="100" r="80" stroke="#ddd" stroke-width="10" fill="none"/>
            <circle cx="100" cy="100" r="80" stroke="#8e44ad" stroke-width="10"
            fill="none"
            stroke-dasharray="{score*5} 500"
            transform="rotate(-90 100 100)"/>
            <text x="50%" y="50%" text-anchor="middle" fill="white" dy=".3em" font-size="20">
                {round(score,1)}
            </text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- PRICE ----------------
    st.subheader("💰 Price Comparison")
    df_price = pd.DataFrame(prices.items(), columns=["Platform","Price"])
    st.bar_chart(df_price.set_index("Platform"))

    # ---------------- REVIEWS ----------------
    st.subheader("⭐ Reviews Comparison")
    df_reviews = pd.DataFrame(reviews.items(), columns=["Platform","Rating"])
    st.bar_chart(df_reviews.set_index("Platform"))

    # ---------------- INSIGHT ----------------
    st.subheader("🧠 AI Insight")

    if score > 70:
        st.success("Highly Trustworthy Product")
    elif score > 40:
        st.warning("Moderate Trust - Check reviews")
    else:
        st.error("Low Trust - Risky purchase")

# ---------------- HISTORY ----------------
st.subheader("📜 History")

if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history))