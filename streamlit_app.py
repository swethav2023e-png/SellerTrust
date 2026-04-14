st.sidebar.title("📊 Dashboard Mode")

mode = st.sidebar.radio(
    "Choose Mode",
    ["Manual Prediction", "URL Analysis"]
)

# ---------------- MANUAL ----------------
if mode == "Manual Prediction":

    st.title("🧠 Manual Trust Prediction")

    col1, col2 = st.columns(2)

    with col1:
        delay = st.slider("Delivery Delay", 0, 100, 20)
        complaints = st.slider("Complaint Rate", 0, 10, 2)

    with col2:
        consistency = st.slider("Review Consistency", 0, 100, 80)
        experience = st.slider("Seller Experience", 0, 10, 5)

    if st.button("🚀 Predict Trust"):
        score = calculate_trust(delay, complaints, consistency, experience)

        st.metric("Trust Score", round(score,2))
        st.progress(int(score))

        if score > 70:
            st.success("🟢 HIGH TRUST")
        elif score > 40:
            st.warning("🟡 MEDIUM TRUST")
        else:
            st.error("🔴 LOW TRUST")

# ---------------- URL ----------------
elif mode == "URL Analysis":

    st.title("🔗 Product URL Analysis")

    url = st.text_input("Paste Product URL")

    if st.button("🚀 Analyze Product"):

        data = analyze_product(url)

        if data:
            st.subheader(f"Product: {data['title']}")

            d,c,r,e = data["features"]
            score = calculate_trust(d,c,r,e)

            st.metric("Trust Score", round(score,2))
            st.progress(int(score))

            if score > 70:
                st.success("🟢 HIGH TRUST")
            elif score > 40:
                st.warning("🟡 MEDIUM TRUST")
            else:
                st.error("🔴 LOW TRUST")

        else:
            st.error("Invalid URL")
