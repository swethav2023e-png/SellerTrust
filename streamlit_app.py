import streamlit as st
import pandas as pd
import numpy as np
import time
import random

import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pyrebase

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
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT.firebaseapp.com",
    "projectId": "YOUR_PROJECT",
    "storageBucket": "YOUR_PROJECT.appspot.com",
    "messagingSenderId": "XXXX",
    "appId": "XXXX",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ---------------- SESSION ----------------
if "logged" not in st.session_state:
    st.session_state.logged = False

# ---------------- LOGIN SYSTEM ----------------
if not st.session_state.logged:

    st.title("🔐 Smart Trust AI Login")

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

    col1, col2 = st.columns(2)

    # LOGIN
    with col1:
        if st.button("Login"):
            if email == "" or password == "":
                st.warning("Enter email & password")
            else:
                try:
                    auth.sign_in_with_email_and_password(email, password)
                    st.session_state.logged = True
                    st.session_state.user = email
                    st.success("Login successful 🎉")
                    st.rerun()
                except Exception as e:
                    error = str(e)

                    if "EMAIL_NOT_FOUND" in error:
                        st.error("User not found. Register first.")
                    elif "INVALID_PASSWORD" in error:
                        st.error("Wrong password.")
                    else:
                        st.error("Login failed.")

    # REGISTER
    with col2:
        if st.button("Register"):
            if email == "" or password == "":
                st.warning("Enter email & password")
            elif len(password) < 6:
                st.warning("Password must be 6+ characters")
            else:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    st.success("Account created! Now login.")
                except Exception as e:
                    error = str(e)

                    if "EMAIL_EXISTS" in error:
                        st.warning("Account already exists. Login instead.")
                    else:
                        st.error("Registration failed.")

    st.stop()

# ---------------- DASHBOARD ----------------
st.sidebar.success(f"Logged in: {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.logged = False
    st.rerun()

st.title("💜 Smart Trust AI Dashboard")

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    delay = st.slider("Delivery Delay", 0, 100, 20)
    complaints = st.slider("Complaint Rate", 0, 10, 2)

with col2:
    consistency = st.slider("Review Consistency", 0, 100, 80)
    experience = st.slider("Seller Experience", 0, 10, 5)

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

    with st.spinner("Analyzing..."):
        time.sleep(2)

    score = calculate_trust(delay, complaints, consistency, experience)

    st.metric("Trust Score", round(score,2))
    st.progress(int(score))

    if score > 70:
        st.success("🟢 HIGH TRUST")
    elif score > 40:
        st.warning("🟡 MEDIUM TRUST")
    else:
        st.error("🔴 LOW TRUST")

    st.line_chart([score, 60, 80])
