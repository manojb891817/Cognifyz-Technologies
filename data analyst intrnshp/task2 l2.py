import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from collections import Counter
import ast
import numpy as np

# Streamlit setup
st.set_page_config(
    page_title="Cuisine Combination Analysis", 
    layout="wide",
    page_icon="🍳"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #e65c00;
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
        background-color: #fff5e6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #e65c00;
        margin-bottom: 1rem;
    }
    .highlight-box {
        background-color: #fff0e6;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ff9933;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🍳 Cuisine Combination Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Level 2 - Task 2: Analyze cuisine combinations and their ratings</p>', unsafe_allow_html=True)

# File uploader
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
        required_cols = ['Cuisines', 'Aggregate rating']
        if all(col in df.columns for col in required_cols):
            
            # Data preprocessing
            st.markdown("---")
            st.markdown("### 🔧 Data Preprocessing")
            
            # Handle missing values
            initial_count = len(df)
            df_clean = df.dropna(subset=['Cuisines', 'Aggregate rating']).copy()
            cleaned_count = len(df_clean)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Restaurants", initial_count)
            with col2:
                st.metric("After Cleaning", cleaned_count)
            with col3:
                st.metric("Data Loss", f"{((initial_count - cleaned_count) / initial_count * 100):.1f}%")
            
            if cleaned_count == 0:
                st.error("❌ No valid data remaining after cleaning. Please check your dataset.")
                st.stop()
            
            # Cuisine processing function
            def process_cuisines(cuisine_string):
                """Convert cuisine string to list of individual cuisines"""
                if pd.isna(cuisine_string):
                    return []
                try:
                    # Try evaluating as list if it's stored as string representation
                    if isinstance(cuisine_string, str) and cuisine_string.startswith('['):
                        return [cuisine.strip().title() for cuisine in ast.literal_eval(cuisine_string)]
                    else:
                        # Split by comma and clean
                        return [cuisine.strip().title() for cuisine in cuisine_string.split(',')]
                except:
                    return [cuisine_string.strip().title()]
            
            # Apply cuisine processing
            df_clean['Cuisine_List'] = df_clean['Cuisines'].apply(process_cuisines)
            df_clean['Num_Cuisines'] = df_clean['Cuisine_List'].apply(len)
            
            # Filter out restaurants with no cuisines
            df_clean = df_clean[df_clean['Num_Cuisines'] > 0]
            
            # Main analysis section
            st.markdown("---")
            st.markdown("## 📊 Cuisine Combination Analysis")
            
            # Top row: Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                unique_cuisines = set()
                for cuisines in df_clean['Cuisine_List']:
                    unique_cuisines.update(cuisines)
                st.metric("Unique Cuisines", len(unique_cuisines))
            
            with col2:
                avg_cuisines_per_restaurant = df_clean['Num_Cuisines'].mean()
                st.metric("Avg Cuisines per Restaurant", f"{avg_cuisines_per_restaurant:.2f}")
            
            with col3:
                single_cuisine_count = len(df_clean[df_clean['Num_Cuisines'] == 1])
                st.metric("Single Cuisine Restaurants", single_cuisine_count)
            
            with col4:
                multi_cuisine_count = len(df_clean[df_clean['Num_Cuisines'] > 1])
                st.metric("Multi-Cuisine Restaurants", multi_cuisine_count)
            
            # Two main columns for analysis
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### 🥘 Most Common Cuisine Combinations")
                
                # Find all cuisine combinations
                all_combinations = []
                for cuisines in df_clean['Cuisine_List']:
                    if len(cuisines) >= 2:
                        # Get all possible pairs from the cuisine list
                        for combo in combinations(sorted(cuisines), 2):
                            all_combinations.append(combo)
                
                # Count combination frequencies
                combo_counter = Counter(all_combinations)
                top_combinations = combo_counter.most_common(10)
                
                if top_combinations:
                    # Create combination dataframe
                    combo_data = []
                    for combo, count in top_combinations:
                        combo_data.append({
                            'Cuisine 1': combo[0],
                            'Cuisine 2': combo[1],
                            'Frequency': count,
                            'Combination': f"{combo[0]} + {combo[1]}"
                        })
                    
                    combo_df = pd.DataFrame(combo_data)
                    
                    # Display top combinations
                    fig, ax = plt.subplots(figsize=(10, 6))
                    y_pos = np.arange(len(combo_df))
                    
                    bars = ax.barh(y_pos, combo_df['Frequency'], color='#ff9933', alpha=0.8)
                    ax.set_yticks(y_pos)
                    ax.set_yticklabels(combo_df['Combination'])
                    ax.set_xlabel('Number of Restaurants')
                    ax.set_title('Top 10 Most Common Cuisine Combinations', fontweight='bold')
                    
                    # Add value labels on bars
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                               f'{int(width)}', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Combination table
                    with st.expander("📋 View Detailed Combination Data"):
                        display_combo_df = combo_df[['Cuisine 1', 'Cuisine 2', 'Frequency']].copy()
                        display_combo_df = display_combo_df.reset_index(drop=True)
                        display_combo_df.index += 1
                        st.dataframe(display_combo_df, use_container_width=True)
                
                else:
                    st.info("No cuisine combinations found in the dataset.")
                
                # Single vs Multiple cuisines rating comparison
                st.markdown("### 📈 Single vs Multiple Cuisines Rating Comparison")
                
                single_cuisine_avg = df_clean[df_clean['Num_Cuisines'] == 1]['Aggregate rating'].mean()
                multi_cuisine_avg = df_clean[df_clean['Num_Cuisines'] > 1]['Aggregate rating'].mean()
                
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                categories = ['Single Cuisine', 'Multiple Cuisines']
                averages = [single_cuisine_avg, multi_cuisine_avg]
                colors = ['#3366cc', '#ff9933']
                
                bars = ax2.bar(categories, averages, color=colors, alpha=0.8)
                ax2.set_ylabel('Average Rating')
                ax2.set_title('Average Rating: Single vs Multiple Cuisines', fontweight='bold')
                ax2.grid(axis='y', alpha=0.3)
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                            f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig2)
            
            with col_right:
                st.markdown("### ⭐ Top Rated Cuisine Combinations")
                
                # Calculate average ratings for combinations
                combo_ratings = {}
                combo_counts = {}
                
                for idx, row in df_clean.iterrows():
                    cuisines = row['Cuisine_List']
                    rating = row['Aggregate rating']
                    
                    if len(cuisines) >= 2:
                        for combo in combinations(sorted(cuisines), 2):
                            combo_key = f"{combo[0]} + {combo[1]}"
                            if combo_key not in combo_ratings:
                                combo_ratings[combo_key] = []
                                combo_counts[combo_key] = 0
                            combo_ratings[combo_key].append(rating)
                            combo_counts[combo_key] += 1
                
                # Filter combinations with sufficient data (at least 5 occurrences)
                valid_combos = {k: v for k, v in combo_ratings.items() if len(v) >= 5}
                
                if valid_combos:
                    # Calculate average ratings
                    avg_ratings = {k: np.mean(v) for k, v in valid_combos.items()}
                    combo_counts_filtered = {k: combo_counts[k] for k in valid_combos.keys()}
                    
                    # Create rating dataframe
                    rating_data = []
                    for combo, avg_rating in sorted(avg_ratings.items(), key=lambda x: x[1], reverse=True)[:10]:
                        rating_data.append({
                            'Combination': combo,
                            'Average Rating': avg_rating,
                            'Number of Restaurants': combo_counts_filtered[combo]
                        })
                    
                    rating_df = pd.DataFrame(rating_data)
                    
                    # Display top rated combinations
                    fig3, ax3 = plt.subplots(figsize=(10, 6))
                    y_pos = np.arange(len(rating_df))
                    
                    # Color bars based on rating
                    colors = ['#ff4444' if x < 3.0 else '#ff9933' if x < 4.0 else '#44aa44' for x in rating_df['Average Rating']]
                    
                    bars = ax3.barh(y_pos, rating_df['Average Rating'], color=colors, alpha=0.8)
                    ax3.set_yticks(y_pos)
                    ax3.set_yticklabels(rating_df['Combination'])
                    ax3.set_xlabel('Average Rating')
                    ax3.set_title('Top 10 Highest Rated Cuisine Combinations\n(Min. 5 restaurants)', fontweight='bold')
                    ax3.set_xlim(0, 5)
                    
                    # Add value labels on bars
                    for bar in bars:
                        width = bar.get_width()
                        ax3.text(width + 0.05, bar.get_y() + bar.get_height()/2, 
                                f'{width:.2f}', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig3)
                    
                    # Rating table
                    with st.expander("📋 View Detailed Rating Data"):
                        display_rating_df = rating_df.copy()
                        display_rating_df = display_rating_df.reset_index(drop=True)
                        display_rating_df.index += 1
                        st.dataframe(display_rating_df, use_container_width=True)
                else:
                    st.info("Not enough data to analyze cuisine combination ratings (need at least 5 restaurants per combination).")
                
                # Number of cuisines vs rating analysis
                st.markdown("### 🔢 Number of Cuisines vs Rating")
                
                cuisine_count_stats = df_clean.groupby('Num_Cuisines').agg({
                    'Aggregate rating': ['mean', 'count', 'std']
                }).round(3)
                cuisine_count_stats.columns = ['Average Rating', 'Restaurant Count', 'Std Dev']
                cuisine_count_stats = cuisine_count_stats.reset_index()
                
                fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Scatter plot with trend line
                ax4a.scatter(cuisine_count_stats['Num_Cuisines'], cuisine_count_stats['Average Rating'], 
                           s=cuisine_count_stats['Restaurant Count']*10, alpha=0.6, color='#e65c00')
                ax4a.set_xlabel('Number of Cuisines')
                ax4a.set_ylabel('Average Rating')
                ax4a.set_title('Rating vs Number of Cuisines\n(Bubble size = restaurant count)')
                ax4a.grid(True, alpha=0.3)
                
                # Add trend line
                z = np.polyfit(cuisine_count_stats['Num_Cuisines'], cuisine_count_stats['Average Rating'], 1)
                p = np.poly1d(z)
                ax4a.plot(cuisine_count_stats['Num_Cuisines'], p(cuisine_count_stats['Num_Cuisines']), 
                         "r--", alpha=0.8, linewidth=2)
                
                # Bar chart of restaurant count by number of cuisines
                ax4b.bar(cuisine_count_stats['Num_Cuisines'], cuisine_count_stats['Restaurant Count'], 
                        color='#3366cc', alpha=0.7)
                ax4b.set_xlabel('Number of Cuisines')
                ax4b.set_ylabel('Number of Restaurants')
                ax4b.set_title('Restaurant Distribution by Number of Cuisines')
                ax4b.grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig4)
            
            # Key Insights Section
            st.markdown("---")
            st.markdown("## 💡 Key Insights")
            
            if valid_combos:
                best_combo = max(valid_combos.items(), key=lambda x: np.mean(x[1]))
                worst_combo = min(valid_combos.items(), key=lambda x: np.mean(x[1]))
                
                col_insight1, col_insight2 = st.columns(2)
                
                with col_insight1:
                    st.markdown(f"""
                    <div class="highlight-box">
                        <h4>🏆 Highest Rated Combination</h4>
                        <p><strong>{best_combo[0]}</strong></p>
                        <p>Average Rating: <strong>{np.mean(best_combo[1]):.2f}</strong></p>
                        <p>Based on {len(best_combo[1])} restaurants</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_insight2:
                    st.markdown(f"""
                    <div class="highlight-box">
                        <h4>📉 Lowest Rated Combination</h4>
                        <p><strong>{worst_combo[0]}</strong></p>
                        <p>Average Rating: <strong>{np.mean(worst_combo[1]):.2f}</strong></p>
                        <p>Based on {len(worst_combo[1])} restaurants</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Additional insights
            col_insight3, col_insight4 = st.columns(2)
            
            with col_insight3:
                rating_correlation = df_clean['Num_Cuisines'].corr(df_clean['Aggregate rating'])
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Correlation Analysis</h4>
                    <p>Correlation between number of cuisines and rating: <strong>{rating_correlation:.3f}</strong></p>
                    <p><small>{'Positive correlation' if rating_correlation > 0 else 'Negative correlation' if rating_correlation < 0 else 'No correlation'} between number of cuisines and ratings</small></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_insight4:
                most_common_single = df_clean[df_clean['Num_Cuisines'] == 1]['Cuisine_List'].explode().value_counts().index[0]
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🥇 Most Popular Single Cuisine</h4>
                    <p><strong>{most_common_single}</strong></p>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.error(f"❌ Required columns 'Cuisines' and 'Aggregate rating' not found in the dataset.")
            st.info("Please upload a dataset that contains both 'Cuisines' and 'Aggregate rating' columns.")

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
else:
    # Welcome message
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background-color: #fff5e6; border-radius: 10px;'>
            <h3>🚀 Get Started with Cuisine Analysis</h3>
            <p>Upload a CSV file containing restaurant data with 'Cuisines' and 'Aggregate rating' columns to analyze:</p>
            <ul style='text-align: left; display: inline-block;'>
                <li>Most common cuisine combinations</li>
                <li>Highest rated combinations</li>
                <li>Single vs multiple cuisine performance</li>
                <li>Correlation between cuisine variety and ratings</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)