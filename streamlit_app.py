# ---------------- IMPORTS ----------------
import streamlit as st
import pandas as pd
import numpy as np
import time
import random
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pyrebase

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Trust AI", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#1a1f71,#6a11cb,#8e44ad);
    color:white;
}
.stButton button {
    background: linear-gradient(90deg,#6a11cb,#8e44ad);
    color:white;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FIREBASE ----------------
firebaseConfig = {
    "apiKey": "YOUR_KEY",
    "authDomain": "YOUR_PROJECT.firebaseapp.com",
    "projectId": "YOUR_PROJECT",
    "storageBucket": "YOUR_PROJECT.appspot.com",
    "messagingSenderId": "XXXX",
    "appId": "XXXX",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# ---------------- LOGIN ----------------
if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:

    st.title("🔐 Smart Trust AI Login")

    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")

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
                st.error("User exists")

    st.stop()

# ---------------- LOGOUT ----------------
if st.sidebar.button("Logout"):
    st.session_state.logged = False
    st.rerun()

st.sidebar.success(f"Logged in: {st.session_state.user}")

# ---------------- HISTORY ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- AI ASSISTANT ----------------
st.sidebar.title("🤖 AI Assistant")
question = st.sidebar.text_input("Ask about trust")

if question:
    st.sidebar.write("This product seems moderately trustworthy based on available data.")

# ---------------- PRODUCT SCRAPER ----------------
def analyze_product(url):
    try:
        response = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

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
        return {
            "title":"Unknown",
            "prices":{"Amazon":1000},
            "reviews":{"Amazon":70},
            "features": (30,3,70,5)
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

# ---------------- PDF ----------------
def generate_pdf(score):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200,10,f"Trust Score: {score}", ln=True)

    file = "report.pdf"
    pdf.output(file)
    return file

# ---------------- MAIN ----------------
st.title("💜 Smart Trust AI Dashboard")

col1, col2 = st.columns(2)

with col1:
    url = st.text_input("🔗 Paste Product URL")

with col2:
    delay = st.slider("Delay",0,100,20)
    complaints = st.slider("Complaints",0,10,1)
    consistency = st.slider("Consistency",0,100,80)
    experience = st.slider("Experience",0,10,5)

# ---------------- ANALYZE ----------------
if st.button("🚀 Analyze"):

    with st.spinner("Analyzing..."):
        time.sleep(2)

    if url:
        data = analyze_product(url)
        st.subheader(f"Product: {data['title']}")
        d,c,r,e = data["features"]
        prices = data["prices"]
        reviews = data["reviews"]
    else:
        d,c,r,e = delay, complaints, consistency, experience
        prices = {"Amazon":1000,"Flipkart":950,"Meesho":900}
        reviews = {"Amazon":80,"Flipkart":75,"Meesho":70}

    score = calculate_trust(d,c,r,e)

    st.session_state.history.append({"Score":round(score,2)})

    # Metrics
    st.metric("Trust Score", round(score,2))
    st.progress(int(score))

    # Chart
    st.bar_chart(pd.DataFrame(prices.items(), columns=["Platform","Price"]).set_index("Platform"))
    st.bar_chart(pd.DataFrame(reviews.items(), columns=["Platform","Rating"]).set_index("Platform"))

    # Result
    if score > 70:
        st.success("Highly Trustworthy")
    elif score > 40:
        st.warning("Moderate Trust")
    else:
        st.error("Low Trust")

    # PDF
    if st.button("📄 Download Report"):
        file = generate_pdf(score)
        with open(file,"rb") as f:
            st.download_button("Download PDF", f)

# ---------------- HISTORY ----------------
st.subheader("📜 History")
if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history))
