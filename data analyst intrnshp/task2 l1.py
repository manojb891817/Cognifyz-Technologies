import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit page setup
st.set_page_config(page_title="Task 2 - City Analysis", layout="wide")

# Title and header
st.title("🏙️ City Analysis - Cognifyz Data Analytics Internship")
st.markdown("### Level 1 - Task 2")
st.write("Analyze restaurant distribution and ratings by city using interactive visualizations.")

# File upload section
uploaded_file = st.file_uploader("📂 Upload your restaurant dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")

    # Display a preview
    st.subheader("📋 Dataset Preview")
    st.dataframe(df.head())

    # Ensure necessary columns exist
    required_columns = ['City', 'Restaurant Name', 'Aggregate rating']
    if all(col in df.columns for col in required_columns):

        # 1️⃣ City with highest number of restaurants
        city_counts = df['City'].value_counts().reset_index()
        city_counts.columns = ['City', 'Restaurant Count']

        top_city = city_counts.iloc[0]
        st.subheader("🏆 City with the Most Restaurants")
        st.metric(label="City", value=top_city['City'])
        st.metric(label="Number of Restaurants", value=int(top_city['Restaurant Count']))

        # Bar chart for restaurant count per city
        st.markdown("### 🍴 Number of Restaurants per City")
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(x="Restaurant Count", y="City", data=city_counts.head(10), ax=ax1, palette="coolwarm")
        st.pyplot(fig1)

        # 2️⃣ Average rating for each city
        avg_ratings = df.groupby('City')['Aggregate rating'].mean().reset_index()
        avg_ratings = avg_ratings.sort_values(by='Aggregate rating', ascending=False)

        st.markdown("### ⭐ Average Ratings by City")
        st.dataframe(avg_ratings.style.background_gradient(cmap="YlGnBu"))

        # 3️⃣ City with highest average rating
        best_city = avg_ratings.iloc[0]
        st.subheader("🌟 City with the Highest Average Rating")
        st.metric(label="City", value=best_city['City'])
        st.metric(label="Average Rating", value=round(best_city['Aggregate rating'], 2))

        # Visualization of average ratings
        st.markdown("### 📊 Top 10 Cities by Average Rating")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.barplot(x="Aggregate rating", y="City", data=avg_ratings.head(10), ax=ax2, palette="viridis")
        st.pyplot(fig2)

    else:
        st.error("❌ Missing required columns. Please ensure your dataset contains 'City', 'Restaurant Name', and 'Aggregate rating' columns.")
else:
    st.info("👆 Upload a CSV file to begin analysis.")
