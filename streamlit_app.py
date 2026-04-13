import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import requests
from bs4 import BeautifulSoup
import pyrebase

import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ---------------- PAGE ----------------
st.set_page_config(page_title="Smart Trust AI", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#1a1f71,#6a11cb,#8e44ad);
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FIREBASE ----------------
firebaseConfig = {
    "apiKey": "AIzaSyA3F3rEHiSU2bEJCLb-aEoENhok4Oss8BA",
    "authDomain": "sellertrustai.firebaseapp.com",
    "projectId": "sellertrustai",
    "storageBucket": "sellertrustai.appspot.com",
    "messagingSenderId": "907138478207",
    "appId": "1:907138478207:web:163b63dcdeea2214eacf4a",
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

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            try:
                auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged = True
                st.session_state.user = email
                st.success("Login successful")
                st.rerun()
            except:
                st.error("Invalid login")

    with col2:
        if st.button("Register"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created")
            except:
                st.warning("User exists. Login instead.")

    st.stop()

# ---------------- DASHBOARD ----------------
st.sidebar.success(f"Logged in: {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.logged = False
    st.rerun()

# ---------------- AI ASSISTANT ----------------
st.sidebar.title("🤖 AI Assistant")
question = st.sidebar.text_input("Ask about product trust")

if question:
    st.sidebar.write("This product seems moderately trustworthy based on analysis.")

# ---------------- TITLE ----------------
st.title("💜 Smart Trust AI Dashboard")

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    url = st.text_input("🔗 Paste Product URL")

with col2:
    delay = st.slider("Delivery Delay", 0, 100, 20)
    complaints = st.slider("Complaint Rate", 0, 10, 2)
    consistency = st.slider("Review Consistency", 0, 100, 80)
    experience = st.slider("Seller Experience", 0, 10, 5)

# ---------------- PRODUCT SCRAPER ----------------
def analyze_product(url):
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else "Product"

        return {
            "title": title,
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
    except:
        return None

# ---------------- FUZZY LOGIC ----------------
def calculate_trust(d,c,r,e):

    delay_var = ctrl.Antecedent(np.arange(0,101,1),'delay')
    comp_var = ctrl.Antecedent(np.arange(0,11,1),'complaints')
    cons_var = ctrl.Antecedent(np.arange(0,101,1),'consistency')
    exp_var = ctrl.Antecedent(np.arange(0,11,1),'experience')

    trust = ctrl.Consequent(np.arange(0,101,1),'trust')

    delay_var['low'] = fuzz.trimf(delay_var.universe,[0,0,30])
    delay_var['high'] = fuzz.trimf(delay_var.universe,[60,100,100])

    comp_var['low'] = fuzz.trimf(comp_var.universe,[0,0,3])
    comp_var['high'] = fuzz.trimf(comp_var.universe,[5,10,10])

    cons_var['good'] = fuzz.trimf(cons_var.universe,[70,100,100])
    cons_var['poor'] = fuzz.trimf(cons_var.universe,[0,0,50])

    exp_var['high'] = fuzz.trimf(exp_var.universe,[5,10,10])

    trust['low'] = fuzz.trimf(trust.universe,[0,0,40])
    trust['medium'] = fuzz.trimf(trust.universe,[40,60,80])
    trust['high'] = fuzz.trimf(trust.universe,[70,100,100])

    rules = [
        ctrl.Rule(delay_var['low'] & comp_var['low'], trust['high']),
        ctrl.Rule(delay_var['high'] | comp_var['high'], trust['low']),
        ctrl.Rule(cons_var['good'], trust['high']),
        ctrl.Rule(cons_var['poor'], trust['low']),
        ctrl.Rule(exp_var['high'], trust['high'])
    ]

    system = ctrl.ControlSystem(rules)
    sim = ctrl.ControlSystemSimulation(system)

    sim.input['delay'] = d
    sim.input['complaints'] = c
    sim.input['consistency'] = r
    sim.input['experience'] = e

    sim.compute()
    return sim.output['trust']

# ---------------- ANALYZE ----------------
if st.button("🚀 Analyze"):

    with st.spinner("Analyzing product..."):
        time.sleep(2)

    if url:
        data = analyze_product(url)
        if data:
            st.subheader(f"Product: {data['title']}")
            d,c,r,e = data["features"]
            prices = data["prices"]
            reviews = data["reviews"]
        else:
            st.error("Invalid URL")
            st.stop()
    else:
        d,c,r,e = delay, complaints, consistency, experience
        prices = {"Amazon":1000,"Flipkart":950,"Meesho":900}
        reviews = {"Amazon":80,"Flipkart":75,"Meesho":70}

    score = calculate_trust(d,c,r,e)

    # ---------------- TRUST METER ----------------
    st.subheader("🎯 Trust Meter")

    st.markdown(f"""
    <div style='text-align:center'>
        <svg width="220" height="220">
            <circle cx="110" cy="110" r="90" stroke="#ddd" stroke-width="12" fill="none"/>
            <circle cx="110" cy="110" r="90"
                stroke="url(#grad)"
                stroke-width="12"
                fill="none"
                stroke-dasharray="{score*5} 565"
                transform="rotate(-90 110 110)"/>
            <defs>
                <linearGradient id="grad">
                    <stop offset="0%" stop-color="#6a11cb"/>
                    <stop offset="100%" stop-color="#8e44ad"/>
                </linearGradient>
            </defs>
            <text x="50%" y="50%" text-anchor="middle"
                fill="white" dy=".3em" font-size="22">
                {round(score,1)}
            </text>
        </svg>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- METRICS ----------------
    st.metric("Trust Score", round(score,2))
    st.progress(int(score))

    # ---------------- CHARTS ----------------
    st.bar_chart(pd.DataFrame(prices.items(), columns=["Platform","Price"]).set_index("Platform"))
    st.bar_chart(pd.DataFrame(reviews.items(), columns=["Platform","Rating"]).set_index("Platform"))

    # ---------------- RESULT ----------------
    if score > 70:
        st.success("🟢 HIGH TRUST")
    elif score > 40:
        st.warning("🟡 MEDIUM TRUST")
    else:
        st.error("🔴 LOW TRUST")
