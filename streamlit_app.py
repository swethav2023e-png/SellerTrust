elif mode == "URL Analysis":

    st.title("🔗 Product URL Analysis")

    url = st.text_input("Paste Product URL")

    if st.button("🚀 Analyze Product"):

        with st.spinner("Analyzing..."):
            time.sleep(2)

        data = analyze_product(url)

        if data:
            st.subheader(f"Product: {data['title']}")

            d,c,r,e = data["features"]
            prices = data["prices"]
            reviews = data["reviews"]

            score = calculate_trust(d,c,r,e)

            st.metric("Trust Score", round(score,2))
            st.progress(int(score))

            # Trust Meter
            st.subheader("🎯 Trust Meter")

            st.markdown(f"""
            <div style='text-align:center'>
                <svg width="220" height="220">
                    <circle cx="110" cy="110" r="90" stroke="#ddd" stroke-width="12" fill="none"/>
                    <circle cx="110" cy="110" r="90"
                        stroke="#6a11cb"
                        stroke-width="12"
                        fill="none"
                        stroke-dasharray="{score*5} 565"
                        transform="rotate(-90 110 110)"/>
                    <text x="50%" y="50%" text-anchor="middle"
                        fill="white" dy=".3em" font-size="22">
                        {round(score,1)}
                    </text>
                </svg>
            </div>
            """, unsafe_allow_html=True)

            st.bar_chart(pd.DataFrame(prices.items(), columns=["Platform","Price"]).set_index("Platform"))
            st.bar_chart(pd.DataFrame(reviews.items(), columns=["Platform","Rating"]).set_index("Platform"))

            if score > 70:
                st.success("🟢 HIGH TRUST")
            elif score > 40:
                st.warning("🟡 MEDIUM TRUST")
            else:
                st.error("🔴 LOW TRUST")

        else:
            st.error("Invalid URL")
