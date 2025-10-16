import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Streamlit setup
st.set_page_config(
    page_title="Restaurant Chains Analysis", 
    layout="wide",
    page_icon="🏪"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #9c27b0;
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
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #9c27b0;
        margin-bottom: 1rem;
    }
    .chain-box {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #4caf50;
        margin: 1rem 0;
    }
    .insight-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ff9800;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🏪 Restaurant Chains Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Level 2 - Task 4: Analyze restaurant chains performance and popularity</p>', unsafe_allow_html=True)

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
        required_cols = ['Restaurant Name']
        optional_cols = ['Aggregate rating', 'Votes', 'City', 'Country Code', 'Cuisines']
        
        if all(col in df.columns for col in required_cols):
            
            # Data preprocessing
            st.markdown("---")
            st.markdown("### 🔧 Data Preprocessing")
            
            # Handle missing values
            initial_count = len(df)
            df_clean = df.dropna(subset=['Restaurant Name']).copy()
            
            # Clean restaurant names
            df_clean['Restaurant Name Cleaned'] = df_clean['Restaurant Name'].str.strip().str.title()
            
            cleaned_count = len(df_clean)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Restaurants", initial_count)
            with col2:
                st.metric("After Cleaning", cleaned_count)
            with col3:
                st.metric("Data Loss", f"{((initial_count - cleaned_count) / initial_count * 100):.1f}%")
            
            if cleaned_count == 0:
                st.error("❌ No valid restaurant data remaining after cleaning. Please check your dataset.")
                st.stop()
            
            # Chain identification
            st.markdown("---")
            st.markdown("## 🔍 Chain Identification")
            
            # Find potential chains (restaurants with same name)
            chain_candidates = df_clean['Restaurant Name Cleaned'].value_counts()
            potential_chains = chain_candidates[chain_candidates > 1]
            
            st.markdown(f"### 📊 Found **{len(potential_chains)}** potential restaurant chains")
            
            # Chain analysis parameters
            st.markdown("### ⚙️ Chain Detection Parameters")
            col_param1, col_param2 = st.columns(2)
            
            with col_param1:
                min_locations = st.slider(
                    "Minimum locations to be considered a chain",
                    min_value=2,
                    max_value=20,
                    value=3,
                    help="Restaurants with fewer than this many locations will be excluded from chain analysis"
                )
            
            with col_param2:
                min_name_similarity = st.slider(
                    "Minimum name similarity score",
                    min_value=0.7,
                    max_value=1.0,
                    value=0.9,
                    step=0.05,
                    help="Higher values require more exact name matches"
                )
            
            # Filter chains by minimum locations
            confirmed_chains = potential_chains[potential_chains >= min_locations]
            
            col_chain1, col_chain2, col_chain3 = st.columns(3)
            
            with col_chain1:
                st.metric("Potential Chains", len(potential_chains))
            with col_chain2:
                st.metric("Confirmed Chains", len(confirmed_chains))
            with col_chain3:
                total_chain_restaurants = confirmed_chains.sum()
                st.metric("Chain Restaurants", f"{total_chain_restaurants} ({total_chain_restaurants/len(df_clean)*100:.1f}%)")
            
            if len(confirmed_chains) == 0:
                st.warning("No restaurant chains found with the current parameters. Try reducing the minimum locations requirement.")
                st.stop()
            
            # Main analysis section
            st.markdown("---")
            st.markdown("## 📈 Chain Performance Analysis")
            
            # Create chains dataframe
            chains_data = []
            for chain_name, location_count in confirmed_chains.items():
                chain_restaurants = df_clean[df_clean['Restaurant Name Cleaned'] == chain_name]
                
                chain_info = {
                    'Chain Name': chain_name,
                    'Location Count': location_count,
                    'Total Restaurants': len(chain_restaurants)
                }
                
                # Add rating statistics if available
                if 'Aggregate rating' in df_clean.columns:
                    chain_info.update({
                        'Average Rating': chain_restaurants['Aggregate rating'].mean(),
                        'Rating Std': chain_restaurants['Aggregate rating'].std(),
                        'Min Rating': chain_restaurants['Aggregate rating'].min(),
                        'Max Rating': chain_restaurants['Aggregate rating'].max(),
                        'Rating Range': chain_restaurants['Aggregate rating'].max() - chain_restaurants['Aggregate rating'].min()
                    })
                
                # Add votes statistics if available
                if 'Votes' in df_clean.columns:
                    chain_info.update({
                        'Total Votes': chain_restaurants['Votes'].sum(),
                        'Average Votes': chain_restaurants['Votes'].mean()
                    })
                
                # Add geographic spread if available
                if 'City' in df_clean.columns:
                    unique_cities = chain_restaurants['City'].nunique()
                    chain_info['Cities Covered'] = unique_cities
                    chain_info['City Diversity'] = unique_cities / location_count
                
                chains_data.append(chain_info)
            
            chains_df = pd.DataFrame(chains_data)
            
            # Display top chains
            st.markdown("### 🏆 Top Restaurant Chains by Locations")
            
            # Sort chains by location count
            top_chains_by_locations = chains_df.nlargest(15, 'Location Count')
            
            col_viz1, col_viz2 = st.columns([2, 1])
            
            with col_viz1:
                # Horizontal bar chart for top chains by locations
                fig, ax = plt.subplots(figsize=(12, 8))
                y_pos = np.arange(len(top_chains_by_locations))
                
                bars = ax.barh(y_pos, top_chains_by_locations['Location Count'], 
                              color=plt.cm.viridis(np.linspace(0, 1, len(top_chains_by_locations))))
                
                ax.set_yticks(y_pos)
                ax.set_yticklabels(top_chains_by_locations['Chain Name'])
                ax.set_xlabel('Number of Locations')
                ax.set_title('Top 15 Restaurant Chains by Number of Locations', fontweight='bold')
                ax.grid(axis='x', alpha=0.3)
                
                # Add value labels
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                           f'{int(width)}', ha='left', va='center', fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig)
            
            with col_viz2:
                # Quick stats
                st.markdown("#### 📊 Chain Statistics")
                st.metric("Largest Chain", top_chains_by_locations.iloc[0]['Chain Name'])
                st.metric("Max Locations", int(top_chains_by_locations.iloc[0]['Location Count']))
                st.metric("Average Chain Size", f"{chains_df['Location Count'].mean():.1f}")
                st.metric("Median Chain Size", f"{chains_df['Location Count'].median():.1f}")
            
            # Rating Analysis
            if 'Aggregate rating' in df_clean.columns:
                st.markdown("---")
                st.markdown("## ⭐ Chain Rating Analysis")
                
                # Filter chains with sufficient data for rating analysis
                rating_chains = chains_df.dropna(subset=['Average Rating'])
                
                col_rating1, col_rating2 = st.columns(2)
                
                with col_rating1:
                    st.markdown("### 🥇 Highest Rated Chains")
                    top_rated_chains = rating_chains.nlargest(10, 'Average Rating')
                    
                    fig2, ax2 = plt.subplots(figsize=(12, 6))
                    y_pos = np.arange(len(top_rated_chains))
                    
                    colors = ['gold' if x == top_rated_chains['Average Rating'].max() else 'lightblue' for x in top_rated_chains['Average Rating']]
                    
                    bars = ax2.barh(y_pos, top_rated_chains['Average Rating'], color=colors)
                    ax2.set_yticks(y_pos)
                    ax2.set_yticklabels(top_rated_chains['Chain Name'])
                    ax2.set_xlabel('Average Rating')
                    ax2.set_title('Top 10 Highest Rated Restaurant Chains', fontweight='bold')
                    ax2.set_xlim(0, 5)
                    ax2.grid(axis='x', alpha=0.3)
                    
                    # Add value labels
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        ax2.text(width + 0.05, bar.get_y() + bar.get_height()/2, 
                                f'{width:.2f}', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig2)
                
                with col_rating2:
                    st.markdown("### 📊 Rating Distribution")
                    
                    # Rating distribution across all chains
                    fig3, (ax3a, ax3b) = plt.subplots(2, 1, figsize=(10, 8))
                    
                    # Histogram of chain average ratings
                    ax3a.hist(rating_chains['Average Rating'], bins=15, color='lightcoral', alpha=0.7, edgecolor='black')
                    ax3a.set_xlabel('Average Rating')
                    ax3a.set_ylabel('Number of Chains')
                    ax3a.set_title('Distribution of Chain Average Ratings', fontweight='bold')
                    ax3a.grid(alpha=0.3)
                    
                    # Box plot of rating consistency
                    chain_ratings_data = []
                    chain_names = []
                    for chain_name in top_rated_chains['Chain Name'].head(8):
                        chain_data = df_clean[df_clean['Restaurant Name Cleaned'] == chain_name]['Aggregate rating']
                        chain_ratings_data.append(chain_data)
                        chain_names.append(chain_name)
                    
                    if chain_ratings_data:
                        ax3b.boxplot(chain_ratings_data, labels=chain_names)
                        ax3b.set_ylabel('Rating')
                        ax3b.set_title('Rating Consistency Across Top Chains', fontweight='bold')
                        ax3b.tick_params(axis='x', rotation=45)
                        ax3b.grid(alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig3)
            
            # Popularity Analysis (Votes)
            if 'Votes' in df_clean.columns:
                st.markdown("---")
                st.markdown("## 🔥 Chain Popularity Analysis")
                
                popularity_chains = chains_df.dropna(subset=['Total Votes'])
                
                col_pop1, col_pop2 = st.columns(2)
                
                with col_pop1:
                    st.markdown("### 🏆 Most Popular Chains by Total Votes")
                    popular_chains = popularity_chains.nlargest(10, 'Total Votes')
                    
                    fig4, ax4 = plt.subplots(figsize=(12, 6))
                    y_pos = np.arange(len(popular_chains))
                    
                    bars = ax4.barh(y_pos, popular_chains['Total Votes'], 
                                   color=plt.cm.plasma(np.linspace(0, 1, len(popular_chains))))
                    
                    ax4.set_yticks(y_pos)
                    ax4.set_yticklabels(popular_chains['Chain Name'])
                    ax4.set_xlabel('Total Votes')
                    ax4.set_title('Top 10 Most Popular Chains by Total Votes', fontweight='bold')
                    ax4.grid(axis='x', alpha=0.3)
                    
                    # Add value labels
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        ax4.text(width + max(popular_chains['Total Votes'])*0.01, 
                                bar.get_y() + bar.get_height()/2, 
                                f'{int(width):,}', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig4)
                
                with col_pop2:
                    st.markdown("### 📈 Votes per Location")
                    
                    # Calculate votes per location
                    popularity_chains['Votes per Location'] = popularity_chains['Total Votes'] / popularity_chains['Location Count']
                    efficient_chains = popularity_chains.nlargest(10, 'Votes per Location')
                    
                    fig5, ax5 = plt.subplots(figsize=(12, 6))
                    y_pos = np.arange(len(efficient_chains))
                    
                    bars = ax5.barh(y_pos, efficient_chains['Votes per Location'], 
                                   color=plt.cm.spring(np.linspace(0, 1, len(efficient_chains))))
                    
                    ax5.set_yticks(y_pos)
                    ax5.set_yticklabels(efficient_chains['Chain Name'])
                    ax5.set_xlabel('Average Votes per Location')
                    ax5.set_title('Top 10 Chains by Votes per Location', fontweight='bold')
                    ax5.grid(axis='x', alpha=0.3)
                    
                    # Add value labels
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        ax5.text(width + max(efficient_chains['Votes per Location'])*0.01, 
                                bar.get_y() + bar.get_height()/2, 
                                f'{width:.0f}', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig5)
            
            # Geographic Analysis
            if 'City' in df_clean.columns:
                st.markdown("---")
                st.markdown("## 🌍 Geographic Spread Analysis")
                
                col_geo1, col_geo2 = st.columns(2)
                
                with col_geo1:
                    st.markdown("### 🗺️ Most Widespread Chains")
                    widespread_chains = chains_df.nlargest(10, 'Cities Covered')
                    
                    fig6, ax6 = plt.subplots(figsize=(12, 6))
                    y_pos = np.arange(len(widespread_chains))
                    
                    bars = ax6.barh(y_pos, widespread_chains['Cities Covered'], 
                                   color=plt.cm.cool(np.linspace(0, 1, len(widespread_chains))))
                    
                    ax6.set_yticks(y_pos)
                    ax6.set_yticklabels(widespread_chains['Chain Name'])
                    ax6.set_xlabel('Number of Cities')
                    ax6.set_title('Top 10 Most Widespread Chains', fontweight='bold')
                    ax6.grid(axis='x', alpha=0.3)
                    
                    # Add value labels
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        ax6.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                                f'{int(width)}', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig6)
                
                with col_geo2:
                    st.markdown("### 🏙️ City Diversity Index")
                    # Chains with highest city-to-location ratio
                    diverse_chains = chains_df.nlargest(10, 'City Diversity')
                    
                    fig7, ax7 = plt.subplots(figsize=(12, 6))
                    y_pos = np.arange(len(diverse_chains))
                    
                    bars = ax7.barh(y_pos, diverse_chains['City Diversity'], 
                                   color=plt.cm.winter(np.linspace(0, 1, len(diverse_chains))))
                    
                    ax7.set_yticks(y_pos)
                    ax7.set_yticklabels(diverse_chains['Chain Name'])
                    ax7.set_xlabel('City Diversity (Cities per Location)')
                    ax7.set_title('Top 10 Chains by Geographic Diversity', fontweight='bold')
                    ax7.grid(axis='x', alpha=0.3)
                    
                    # Add value labels
                    for i, bar in enumerate(bars):
                        width = bar.get_width()
                        ax7.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                                f'{width:.2f}', ha='left', va='center', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig7)
            
            # Detailed Chain Comparison
            st.markdown("---")
            st.markdown("## 📊 Detailed Chain Comparison")
            
            # Let user select chains to compare
            st.markdown("### 🔄 Compare Specific Chains")
            selected_chains = st.multiselect(
                "Select chains to compare:",
                options=chains_df['Chain Name'].tolist(),
                default=chains_df.nlargest(5, 'Location Count')['Chain Name'].tolist()
            )
            
            if selected_chains:
                comparison_df = chains_df[chains_df['Chain Name'].isin(selected_chains)]
                
                # Create comparison visualization
                col_comp1, col_comp2 = st.columns(2)
                
                with col_comp1:
                    st.markdown("#### 📈 Performance Metrics")
                    
                    metrics_to_show = ['Location Count', 'Total Restaurants']
                    if 'Average Rating' in comparison_df.columns:
                        metrics_to_show.append('Average Rating')
                    if 'Total Votes' in comparison_df.columns:
                        metrics_to_show.append('Total Votes')
                    if 'Cities Covered' in comparison_df.columns:
                        metrics_to_show.append('Cities Covered')
                    
                    st.dataframe(
                        comparison_df[['Chain Name'] + metrics_to_show].set_index('Chain Name'),
                        use_container_width=True
                    )
                
                with col_comp2:
                    st.markdown("#### 🎯 Key Insights")
                    
                    for chain in selected_chains:
                        chain_data = comparison_df[comparison_df['Chain Name'] == chain].iloc[0]
                        
                        insights = []
                        insights.append(f"**{chain}**")
                        insights.append(f"• Locations: {chain_data['Location Count']}")
                        
                        if 'Average Rating' in chain_data and not pd.isna(chain_data['Average Rating']):
                            insights.append(f"• Average Rating: {chain_data['Average Rating']:.2f}")
                        
                        if 'Total Votes' in chain_data and not pd.isna(chain_data['Total Votes']):
                            insights.append(f"• Total Votes: {chain_data['Total Votes']:,}")
                        
                        if 'Cities Covered' in chain_data and not pd.isna(chain_data['Cities Covered']):
                            insights.append(f"• Cities: {chain_data['Cities Covered']}")
                        
                        st.markdown("<br>".join(insights))
                        st.markdown("---")
            
            # Key Insights Section
            st.markdown("---")
            st.markdown("## 💡 Strategic Insights")
            
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                # Largest chain insight
                largest_chain = chains_df.loc[chains_df['Location Count'].idxmax()]
                st.markdown(f"""
                <div class="chain-box">
                    <h4>🏆 Market Leader</h4>
                    <p><strong>{largest_chain['Chain Name']}</strong> dominates with {largest_chain['Location Count']} locations</p>
                    <p>This represents {largest_chain['Location Count']/len(confirmed_chains)*100:.1f}% of all chain locations</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Rating consistency insight
                if 'Rating Std' in chains_df.columns:
                    most_consistent = chains_df[chains_df['Location Count'] >= 5].loc[chains_df['Rating Std'].idxmin()]
                    least_consistent = chains_df[chains_df['Location Count'] >= 5].loc[chains_df['Rating Std'].idxmax()]
                    
                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>🎯 Quality Control</h4>
                        <p><strong>Most Consistent:</strong> {most_consistent['Chain Name']} (std: {most_consistent['Rating Std']:.2f})</p>
                        <p><strong>Least Consistent:</strong> {least_consistent['Chain Name']} (std: {least_consistent['Rating Std']:.2f})</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col_insight2:
                # Best rated chain insight
                if 'Average Rating' in chains_df.columns:
                    best_rated = chains_df.loc[chains_df['Average Rating'].idxmax()]
                    st.markdown(f"""
                    <div class="chain-box">
                        <h4>⭐ Customer Favorite</h4>
                        <p><strong>{best_rated['Chain Name']}</strong> has the highest average rating: {best_rated['Average Rating']:.2f}</p>
                        <p>Operating in {best_rated.get('Cities Covered', 'N/A')} cities with {best_rated['Location Count']} locations</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Growth potential insight
                if 'City Diversity' in chains_df.columns:
                    expansion_candidates = chains_df[chains_df['City Diversity'] < 0.5].nlargest(3, 'Location Count')
                    if len(expansion_candidates) > 0:
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>🚀 Expansion Opportunities</h4>
                            <p>Chains with high location concentration but low city diversity:</p>
                            <ul>
                                {"".join([f"<li>{row['Chain Name']} ({row['Location Count']} locs, {row.get('Cities Covered', 'N/A')} cities)</li>" 
                                         for _, row in expansion_candidates.iterrows()])}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Raw data export
            with st.expander("📥 Export Chain Data"):
                st.download_button(
                    label="Download Chains Analysis CSV",
                    data=chains_df.to_csv(index=False),
                    file_name="restaurant_chains_analysis.csv",
                    mime="text/csv"
                )
                st.dataframe(chains_df, use_container_width=True)

        else:
            st.error(f"❌ Required column 'Restaurant Name' not found in the dataset.")
            st.info("Please upload a dataset that contains restaurant name information.")

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
else:
    # Welcome message
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background-color: #f3e5f5; border-radius: 10px;'>
            <h3>🚀 Analyze Restaurant Chains</h3>
            <p>Upload a CSV file containing restaurant data to analyze chain performance:</p>
            <ul style='text-align: left; display: inline-block;'>
                <li>Identify restaurant chains and their market presence</li>
                <li>Compare ratings and popularity across chains</li>
                <li>Analyze geographic spread and expansion patterns</li>
                <li>Discover top-performing chains and strategic insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)