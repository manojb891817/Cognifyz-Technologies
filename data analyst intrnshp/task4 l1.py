import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 🎯 Streamlit setup
st.set_page_config(page_title="Task 4 - Online Delivery", layout="wide")
st.title("🚚 Online Delivery Analysis")
st.markdown("Analyze online delivery options and compare ratings of restaurants with and without online delivery.")

# 📂 File uploader
uploaded_file = st.file_uploader("Upload your restaurant dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")

    # 🧾 Preview (smaller table)
    with st.expander("📋 Dataset Preview (First 5 rows)"):
        st.dataframe(df.head(), height=150)

    # ✅ Check columns
    if 'Has Online delivery' in df.columns and 'Aggregate rating' in df.columns:

        # ===============================
        # 1️⃣ Online Delivery Distribution - Compact layout
        # ===============================
        st.subheader("📊 Online Delivery Distribution")
        
        delivery_counts = df['Has Online delivery'].value_counts().reset_index()
        delivery_counts.columns = ['Online Delivery', 'Count']
        total = delivery_counts['Count'].sum()
        delivery_counts['Percentage'] = (delivery_counts['Count'] / total * 100).round(2)

        # Three columns for compact layout
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.markdown("**Data Summary**")
            st.dataframe(delivery_counts, height=130, use_container_width=True)

        with col2:
            st.markdown("**Bar Chart**")
            fig, ax = plt.subplots(figsize=(3, 2.5))
            sns.barplot(x='Online Delivery', y='Count', data=delivery_counts, palette="Blues", ax=ax)
            ax.set_xlabel("Online Delivery")
            ax.set_ylabel("Count")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig, use_container_width=True)

        with col3:
            st.markdown("**Pie Chart**")
            fig2, ax2 = plt.subplots(figsize=(3, 2.5))
            ax2.pie(
                delivery_counts['Count'],
                labels=delivery_counts['Online Delivery'],
                autopct='%1.1f%%',
                startangle=90,
                colors=sns.color_palette("Blues", len(delivery_counts)),
                textprops={'fontsize': 8}
            )
            st.pyplot(fig2, use_container_width=True)

        # ===============================
        # 2️⃣ Average Ratings Comparison - Compact layout
        # ===============================
        st.markdown("---")
        st.subheader("⭐ Average Ratings Comparison")
        
        rating_comparison = (
            df.groupby('Has Online delivery')['Aggregate rating']
            .mean()
            .reset_index()
            .round(2)
        )

        col4, col5 = st.columns([1, 1])

        with col4:
            st.markdown("**Rating Summary**")
            st.dataframe(rating_comparison, height=130, use_container_width=True)

        with col5:
            st.markdown("**Rating Comparison**")
            fig3, ax3 = plt.subplots(figsize=(3, 2.5))
            sns.barplot(
                x='Has Online delivery',
                y='Aggregate rating',
                data=rating_comparison,
                palette="Greens",
                ax=ax3
            )
            ax3.set_xlabel("Online Delivery")
            ax3.set_ylabel("Avg Rating")
            ax3.tick_params(axis='x', rotation=45)
            st.pyplot(fig3, use_container_width=True)

        # ===============================
        # 3️⃣ Additional Compact Stats
        # ===============================
        st.markdown("---")
        st.subheader("📈 Quick Statistics")
        
        col6, col7, col8, col9 = st.columns(4)
        
        with col6:
            total_restaurants = len(df)
            st.metric("Total Restaurants", total_restaurants)
            
        with col7:
            with_delivery = len(df[df['Has Online delivery'] == 'Yes'])
            st.metric("With Online Delivery", with_delivery)
            
        with col8:
            avg_rating_all = df['Aggregate rating'].mean().round(2)
            st.metric("Overall Avg Rating", avg_rating_all)
            
        with col9:
            if 'Votes' in df.columns:
                total_votes = df['Votes'].sum()
                st.metric("Total Votes", f"{total_votes:,}")

    else:
        st.error("❌ Dataset must contain 'Has Online delivery' and 'Aggregate rating' columns.")
        
        # Show available columns to help user
        if uploaded_file is not None:
            st.write("**Available columns in your dataset:**")
            st.write(list(df.columns))
else:
    st.info("👆 Upload a CSV file to begin the analysis.")

# Add some custom CSS for better spacing
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)