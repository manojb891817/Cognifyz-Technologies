import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- PAGE SETUP ---
st.set_page_config(page_title="Top Cuisines Analysis", layout="centered")
st.title("🍽️ Task 1 - Top 3 Cuisines Analysis")
st.markdown("#### Cognifyz Data Analyst Internship | Level 1")

# --- LOAD DATA ---
uploaded_file = st.file_uploader("📂 Upload your dataset (CSV file)", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # --- CLEANING & PROCESSING ---
    df.dropna(subset=['Cuisines'], inplace=True)
    df['Cuisines'] = df['Cuisines'].str.split(',')
    df = df.explode('Cuisines')
    df['Cuisines'] = df['Cuisines'].str.strip()

    # --- CALCULATION ---
    cuisine_counts = df['Cuisines'].value_counts()
    top3 = cuisine_counts.head(3)
    total_restaurants = df['Restaurant Name'].nunique()
    percentage = (top3 / total_restaurants) * 100

    # --- RESULT TABLE ---
    result = pd.DataFrame({
        'Cuisine': top3.index,
        'Count': top3.values,
        'Percentage (%)': percentage.round(2)
    })

    st.subheader("📊 Top 3 Most Common Cuisines")
    st.dataframe(result)

    # --- VISUALIZATION ---
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(result['Cuisine'], result['Percentage (%)'], color=['#FF6B6B', '#FFD93D', '#6BCB77'])
    ax.set_title("Top 3 Cuisines by Percentage of Restaurants")
    ax.set_ylabel("Percentage (%)")
    ax.set_xlabel("Cuisine Type")
    st.pyplot(fig)

    # --- INSIGHTS ---
    st.markdown("### 🔍 Key Insights")
    st.write(f"- The most popular cuisine is **{result.iloc[0, 0]}**, served by **{result.iloc[0, 2]}%** of restaurants.")
    st.write(f"- Followed by **{result.iloc[1, 0]}** and **{result.iloc[2, 0]}**.")
    st.success("✅ Task 1 (Level 1) Completed Successfully!")

else:
    st.info("👆 Please upload your dataset CSV file to start analysis.")
