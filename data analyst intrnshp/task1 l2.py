import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit setup
st.set_page_config(
    page_title="Restaurant Ratings Analysis", 
    layout="wide",
    page_icon="🍽️"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem !important;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🍽️ Restaurant Ratings Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Level 2 - Task 1: Analyze restaurant ratings distribution and average votes</p>', unsafe_allow_html=True)

# File uploader in a container
with st.container():
    st.markdown("### 📁 Data Upload")
    uploaded_file = st.file_uploader("Upload your restaurant dataset (CSV format)", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Dataset loaded successfully!")
        
        # Dataset preview
        with st.expander("📋 Dataset Preview (First 10 rows)", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")

        # Check required columns
        if 'Aggregate rating' in df.columns and 'Votes' in df.columns:
            
            # Create two main columns
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Histogram of Aggregate Ratings
                st.markdown("### 📊 Ratings Distribution")
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(df['Aggregate rating'], bins=15, kde=True, color='#1f77b4', alpha=0.7, ax=ax)
                ax.set_xlabel("Aggregate Rating", fontsize=12)
                ax.set_ylabel("Number of Restaurants", fontsize=12)
                ax.set_title("Distribution of Restaurant Ratings", fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig, use_container_width=True)
                
                # Bar chart of ratings count
                st.markdown("### 📈 Restaurant Count by Rating")
                rating_counts = df['Aggregate rating'].value_counts().sort_index().reset_index()
                rating_counts.columns = ['Rating', 'Count']
                
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                sns.barplot(x='Rating', y='Count', data=rating_counts, palette="viridis", ax=ax2)
                ax2.set_xlabel("Rating", fontsize=12)
                ax2.set_ylabel("Number of Restaurants", fontsize=12)
                ax2.set_title("Restaurant Count by Rating", fontsize=14, fontweight='bold')
                ax2.tick_params(axis='x', rotation=45)
                st.pyplot(fig2, use_container_width=True)

            with col2:
                # Key metrics
                st.markdown("### 📊 Key Metrics")
                
                # Most common rating
                most_common_rating = df['Aggregate rating'].mode()[0]
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🏆 Most Common Rating</h4>
                    <h2>{most_common_rating}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")  # Spacer
                
                # Average votes
                avg_votes = df['Votes'].mean()
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🗳️ Average Votes</h4>
                    <h2>{avg_votes:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")  # Spacer
                
                # Additional stats
                total_restaurants = len(df)
                unique_ratings = df['Aggregate rating'].nunique()
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📈 Additional Stats</h4>
                    <p><strong>Total Restaurants:</strong> {total_restaurants:,}</p>
                    <p><strong>Unique Ratings:</strong> {unique_ratings}</p>
                    <p><strong>Rating Range:</strong> {df['Aggregate rating'].min():.1f} - {df['Aggregate rating'].max():.1f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Pie chart
                st.markdown("### 🥧 Ratings Percentage")
                rating_counts['Percentage'] = (rating_counts['Count'] / rating_counts['Count'].sum() * 100).round(1)
                
                # Filter out very small percentages for better visualization
                pie_data = rating_counts[rating_counts['Percentage'] >= 1]
                
                fig3, ax3 = plt.subplots(figsize=(8, 8))
                colors = sns.color_palette("viridis", len(pie_data))
                wedges, texts, autotexts = ax3.pie(
                    pie_data['Percentage'], 
                    labels=pie_data['Rating'], 
                    autopct='%1.1f%%', 
                    startangle=90,
                    colors=colors,
                    textprops={'fontsize': 10}
                )
                
                # Improve autotext appearance
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                
                ax3.set_title("Restaurant Ratings Distribution", fontsize=12, fontweight='bold')
                st.pyplot(fig3, use_container_width=True)

            # Data summary at the bottom
            st.markdown("---")
            st.markdown("### 📋 Data Summary")
            col3, col4, col5 = st.columns(3)
            
            with col3:
                st.metric("Mean Rating", f"{df['Aggregate rating'].mean():.2f}")
            with col4:
                st.metric("Median Rating", f"{df['Aggregate rating'].median():.2f}")
            with col5:
                st.metric("Standard Deviation", f"{df['Aggregate rating'].std():.2f}")

        else:
            st.error("❌ Required columns 'Aggregate rating' and/or 'Votes' not found in the dataset.")
            st.info("Please upload a dataset that contains both 'Aggregate rating' and 'Votes' columns.")

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
else:
    # Welcome message when no file is uploaded
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 10px;'>
            <h3>🚀 Get Started</h3>
            <p>Upload a CSV file containing restaurant data with 'Aggregate rating' and 'Votes' columns to begin your analysis.</p>
        </div>
        """, unsafe_allow_html=True)