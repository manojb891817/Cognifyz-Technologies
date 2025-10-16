import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import DBSCAN
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster

# Streamlit setup
st.set_page_config(
    page_title="Geographic Analysis", 
    layout="wide",
    page_icon="🌍"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #2e7d32;
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
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2e7d32;
        margin-bottom: 1rem;
    }
    .cluster-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #ff9800;
        margin: 1rem 0;
    }
    .stats-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #2196f3;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🌍 Restaurant Geographic Analysis</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Level 2 - Task 3: Analyze restaurant locations and identify spatial patterns</p>', unsafe_allow_html=True)

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
        required_cols = ['Longitude', 'Latitude']
        optional_cols = ['Aggregate rating', 'Restaurant Name', 'Cuisines', 'City', 'Country Code']
        
        if all(col in df.columns for col in required_cols):
            
            # Data preprocessing
            st.markdown("---")
            st.markdown("### 🔧 Data Preprocessing")
            
            # Handle missing values
            initial_count = len(df)
            df_clean = df.dropna(subset=['Longitude', 'Latitude']).copy()
            
            # Remove invalid coordinates (out of bounds)
            valid_coords = (
                (df_clean['Longitude'].between(-180, 180)) & 
                (df_clean['Latitude'].between(-90, 90))
            )
            df_clean = df_clean[valid_coords]
            cleaned_count = len(df_clean)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Restaurants", initial_count)
            with col2:
                st.metric("After Cleaning", cleaned_count)
            with col3:
                st.metric("Data Loss", f"{((initial_count - cleaned_count) / initial_count * 100):.1f}%")
            with col4:
                st.metric("Valid Locations", f"{cleaned_count}")
            
            if cleaned_count == 0:
                st.error("❌ No valid geographic data remaining after cleaning. Please check your dataset.")
                st.stop()
            
            # Geographic statistics
            st.markdown("### 📊 Geographic Coverage")
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            
            with col_stats1:
                st.markdown(f"""
                <div class="stats-box">
                    <h4>🌐 Coverage</h4>
                    <p>Latitude: {df_clean['Latitude'].min():.2f}° to {df_clean['Latitude'].max():.2f}°</p>
                    <p>Longitude: {df_clean['Longitude'].min():.2f}° to {df_clean['Longitude'].max():.2f}°</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stats2:
                # Calculate approximate area coverage
                lat_range = df_clean['Latitude'].max() - df_clean['Latitude'].min()
                lon_range = df_clean['Longitude'].max() - df_clean['Longitude'].min()
                st.markdown(f"""
                <div class="stats-box">
                    <h4>📏 Span</h4>
                    <p>Latitude Range: {lat_range:.2f}°</p>
                    <p>Longitude Range: {lon_range:.2f}°</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stats3:
                center_lat = df_clean['Latitude'].mean()
                center_lon = df_clean['Longitude'].mean()
                st.markdown(f"""
                <div class="stats-box">
                    <h4>🎯 Center Point</h4>
                    <p>Lat: {center_lat:.4f}°</p>
                    <p>Lon: {center_lon:.4f}°</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stats4:
                if 'City' in df_clean.columns:
                    unique_cities = df_clean['City'].nunique()
                    st.markdown(f"""
                    <div class="stats-box">
                        <h4>🏙️ Cities</h4>
                        <p>Unique Cities: {unique_cities}</p>
                        <p>Most common: {df_clean['City'].mode()[0] if not df_clean['City'].mode().empty else 'N/A'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="stats-box">
                        <h4>📍 Locations</h4>
                        <p>Total valid locations: {cleaned_count}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Main analysis section
            st.markdown("---")
            st.markdown("## 🗺️ Interactive Map Analysis")
            
            # Map configuration
            st.markdown("### ⚙️ Map Configuration")
            map_col1, map_col2, map_col3 = st.columns(3)
            
            with map_col1:
                map_type = st.selectbox(
                    "Choose Map Type",
                    ["Cluster Map", "Heat Map", "Point Map", "Rating Map"],
                    help="Cluster: Groups nearby restaurants. Heat: Shows density. Point: Individual markers. Rating: Color by rating."
                )
            
            with map_col2:
                cluster_radius = st.slider("Cluster Radius (meters)", 50, 500, 100)
                zoom_level = st.slider("Initial Zoom Level", 1, 18, 10)
            
            with map_col3:
                show_restaurant_names = st.checkbox("Show Restaurant Names", value=True)
                if 'Aggregate rating' in df_clean.columns:
                    color_by_rating = st.checkbox("Color by Rating", value=True)
                else:
                    color_by_rating = False
            
            # Create the map
            st.markdown("### 🗺️ Restaurant Locations Map")
            
            # Calculate center of the data
            center_lat = df_clean['Latitude'].mean()
            center_lon = df_clean['Longitude'].mean()
            
            # Create base map
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=zoom_level,
                tiles='OpenStreetMap'
            )
            
            # Prepare data for mapping
            if map_type == "Heat Map":
                # Heat Map
                heat_data = [[row['Latitude'], row['Longitude']] for _, row in df_clean.iterrows()]
                HeatMap(heat_data, radius=15, blur=10, gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}).add_to(m)
                
            elif map_type == "Cluster Map":
                # Marker Cluster
                marker_cluster = MarkerCluster().add_to(m)
                
                for _, row in df_clean.iterrows():
                    # Determine marker color based on rating if available
                    color = 'blue'
                    if color_by_rating and 'Aggregate rating' in df_clean.columns:
                        rating = row['Aggregate rating']
                        if rating >= 4.0:
                            color = 'green'
                        elif rating >= 3.0:
                            color = 'orange'
                        else:
                            color = 'red'
                    
                    popup_text = f"<b>{row.get('Restaurant Name', 'Unknown')}</b>"
                    if 'Aggregate rating' in df_clean.columns:
                        popup_text += f"<br>Rating: {row['Aggregate rating']}"
                    if 'Cuisines' in df_clean.columns:
                        popup_text += f"<br>Cuisines: {row['Cuisines']}"
                    
                    folium.Marker(
                        [row['Latitude'], row['Longitude']],
                        popup=popup_text,
                        tooltip=row.get('Restaurant Name', 'Unknown'),
                        icon=folium.Icon(color=color, icon='cutlery', prefix='fa')
                    ).add_to(marker_cluster)
                    
            else:  # Point Map or Rating Map
                for _, row in df_clean.iterrows():
                    # Determine marker color
                    color = 'blue'
                    if (map_type == "Rating Map" or color_by_rating) and 'Aggregate rating' in df_clean.columns:
                        rating = row['Aggregate rating']
                        if rating >= 4.0:
                            color = 'green'
                        elif rating >= 3.0:
                            color = 'orange'
                        else:
                            color = 'red'
                    
                    popup_text = f"<b>{row.get('Restaurant Name', 'Unknown')}</b>"
                    if 'Aggregate rating' in df_clean.columns:
                        popup_text += f"<br>Rating: {row['Aggregate rating']}"
                    if 'Cuisines' in df_clean.columns:
                        popup_text += f"<br>Cuisines: {row['Cuisines']}"
                    
                    folium.Marker(
                        [row['Latitude'], row['Longitude']],
                        popup=popup_text,
                        tooltip=row.get('Restaurant Name', 'Unknown'),
                        icon=folium.Icon(color=color, icon='cutlery', prefix='fa')
                    ).add_to(m)
            
            # Display the map
            map_data = st_folium(m, width=1200, height=500)
            
            # Cluster Analysis Section
            st.markdown("---")
            st.markdown("## 🔍 Cluster Analysis")
            
            # Perform DBSCAN clustering
            st.markdown("### 📊 Spatial Clustering using DBSCAN")
            
            col_cluster1, col_cluster2 = st.columns(2)
            
            with col_cluster1:
                eps_value = st.slider("Cluster Radius (epsilon in degrees)", 0.001, 0.1, 0.01, 0.001,
                                    help="Smaller values = more clusters, larger values = fewer clusters")
            
            with col_cluster2:
                min_samples_value = st.slider("Minimum samples per cluster", 2, 20, 5,
                                            help="Minimum number of restaurants to form a cluster")
            
            # Apply DBSCAN clustering
            coords = df_clean[['Latitude', 'Longitude']].values
            clustering = DBSCAN(eps=eps_value, min_samples=min_samples_value).fit(coords)
            
            # Add cluster labels to dataframe
            df_clean['Cluster'] = clustering.labels_
            
            # Cluster statistics
            n_clusters = len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0)
            n_noise = list(clustering.labels_).count(-1)
            
            col_cluster_stats1, col_cluster_stats2, col_cluster_stats3 = st.columns(3)
            
            with col_cluster_stats1:
                st.metric("Number of Clusters", n_clusters)
            with col_cluster_stats2:
                st.metric("Clustered Restaurants", len(df_clean) - n_noise)
            with col_cluster_stats3:
                st.metric("Noise Points (Isolated)", n_noise)
            
            # Display cluster information
            if n_clusters > 0:
                st.markdown("### 🎯 Cluster Details")
                
                # Calculate cluster centers and sizes
                cluster_info = []
                for cluster_id in range(n_clusters):
                    cluster_data = df_clean[df_clean['Cluster'] == cluster_id]
                    cluster_size = len(cluster_data)
                    center_lat = cluster_data['Latitude'].mean()
                    center_lon = cluster_data['Longitude'].mean()
                    
                    # Calculate cluster bounds
                    lat_min = cluster_data['Latitude'].min()
                    lat_max = cluster_data['Latitude'].max()
                    lon_min = cluster_data['Longitude'].min()
                    lon_max = cluster_data['Longitude'].max()
                    
                    cluster_info.append({
                        'Cluster ID': cluster_id,
                        'Size': cluster_size,
                        'Center Lat': center_lat,
                        'Center Lon': center_lon,
                        'Lat Range': f"{lat_min:.4f}° to {lat_max:.4f}°",
                        'Lon Range': f"{lon_min:.4f}° to {lon_max:.4f}°"
                    })
                
                cluster_df = pd.DataFrame(cluster_info)
                
                # Display cluster table
                col_table, col_viz = st.columns([1, 1])
                
                with col_table:
                    st.dataframe(cluster_df, use_container_width=True)
                
                with col_viz:
                    # Cluster size distribution
                    fig, ax = plt.subplots(figsize=(10, 6))
                    cluster_sizes = [info['Size'] for info in cluster_info]
                    clusters = [f'Cluster {info["Cluster ID"]}' for info in cluster_info]
                    
                    bars = ax.bar(clusters, cluster_sizes, color=plt.cm.Set3(np.linspace(0, 1, len(clusters))))
                    ax.set_xlabel('Cluster ID')
                    ax.set_ylabel('Number of Restaurants')
                    ax.set_title('Restaurant Distribution Across Clusters')
                    ax.tick_params(axis='x', rotation=45)
                    
                    # Add value labels on bars
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                                f'{int(height)}', ha='center', va='bottom')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                
                # Create cluster map
                st.markdown("### 🗺️ Cluster Visualization Map")
                
                # Create cluster map with different colors for each cluster
                cluster_map = folium.Map(
                    location=[center_lat, center_lon],
                    zoom_start=zoom_level
                )
                
                # Color palette for clusters
                colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 
                         'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple']
                
                for _, row in df_clean.iterrows():
                    cluster_id = row['Cluster']
                    if cluster_id == -1:
                        color = 'gray'  # Noise points
                        size = 4
                    else:
                        color = colors[cluster_id % len(colors)]
                        size = 8
                    
                    folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=size,
                        popup=f"Cluster: {cluster_id}",
                        color=color,
                        fill=True,
                        fillColor=color
                    ).add_to(cluster_map)
                
                # Add cluster centers
                for cluster_id in range(n_clusters):
                    cluster_data = df_clean[df_clean['Cluster'] == cluster_id]
                    center_lat = cluster_data['Latitude'].mean()
                    center_lon = cluster_data['Longitude'].mean()
                    
                    folium.Marker(
                        [center_lat, center_lon],
                        popup=f'Cluster {cluster_id} Center\n{len(cluster_data)} restaurants',
                        icon=folium.Icon(color=colors[cluster_id % len(colors)], icon='star')
                    ).add_to(cluster_map)
                
                st_folium(cluster_map, width=1200, height=500)
            
            # Density Analysis
            st.markdown("---")
            st.markdown("## 📈 Spatial Density Analysis")
            
            col_density1, col_density2 = st.columns(2)
            
            with col_density1:
                # Create density heatmap using matplotlib
                st.markdown("### 🔥 Restaurant Density Heatmap")
                
                fig, ax = plt.subplots(figsize=(10, 8))
                
                # Create 2D histogram
                h = ax.hist2d(df_clean['Longitude'], df_clean['Latitude'], 
                             bins=50, cmap='YlOrRd', alpha=0.8)
                
                ax.set_xlabel('Longitude')
                ax.set_ylabel('Latitude')
                ax.set_title('Restaurant Density Heatmap')
                plt.colorbar(h[3], ax=ax, label='Number of Restaurants')
                
                # Add data points
                ax.scatter(df_clean['Longitude'], df_clean['Latitude'], 
                          alpha=0.3, s=1, color='black')
                
                plt.tight_layout()
                st.pyplot(fig)
            
            with col_density2:
                # Geographic distribution by coordinates
                st.markdown("### 📊 Coordinate Distribution")
                
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                
                # Latitude distribution
                ax1.hist(df_clean['Latitude'], bins=30, color='skyblue', alpha=0.7, edgecolor='black')
                ax1.set_xlabel('Latitude')
                ax1.set_ylabel('Number of Restaurants')
                ax1.set_title('Distribution by Latitude')
                ax1.grid(True, alpha=0.3)
                
                # Longitude distribution
                ax2.hist(df_clean['Longitude'], bins=30, color='lightcoral', alpha=0.7, edgecolor='black')
                ax2.set_xlabel('Longitude')
                ax2.set_ylabel('Number of Restaurants')
                ax2.set_title('Distribution by Longitude')
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
            
            # Key Insights
            st.markdown("---")
            st.markdown("## 💡 Key Geographic Insights")
            
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
                # Most dense area
                if n_clusters > 0:
                    largest_cluster = cluster_df.loc[cluster_df['Size'].idxmax()]
                    st.markdown(f"""
                    <div class="cluster-box">
                        <h4>🏙️ Largest Restaurant Cluster</h4>
                        <p><strong>Cluster {largest_cluster['Cluster ID']}</strong> with {largest_cluster['Size']} restaurants</p>
                        <p><strong>Center:</strong> {largest_cluster['Center Lat']:.4f}°N, {largest_cluster['Center Lon']:.4f}°E</p>
                        <p>This area represents a major restaurant hub</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Geographic spread
                area_covered = (df_clean['Latitude'].max() - df_clean['Latitude'].min()) * \
                              (df_clean['Longitude'].max() - df_clean['Longitude'].min())
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📐 Geographic Coverage Area</h4>
                    <p>Approximate area: {area_covered:.2f} square degrees</p>
                    <p>Restaurant density: {len(df_clean)/area_covered:.1f} restaurants/sq degree</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_insight2:
                # Rating by location insights
                if 'Aggregate rating' in df_clean.columns:
                    # Check if ratings vary by cluster
                    if n_clusters > 0:
                        cluster_ratings = []
                        for cluster_id in range(n_clusters):
                            cluster_rating = df_clean[df_clean['Cluster'] == cluster_id]['Aggregate rating'].mean()
                            cluster_ratings.append(cluster_rating)
                        
                        best_cluster_idx = np.argmax(cluster_ratings)
                        best_cluster_rating = cluster_ratings[best_cluster_idx]
                        
                        st.markdown(f"""
                        <div class="cluster-box">
                            <h4>⭐ Highest Rated Area</h4>
                            <p><strong>Cluster {best_cluster_idx}</strong> has the highest average rating</p>
                            <p>Average Rating: <strong>{best_cluster_rating:.2f}</strong></p>
                            <p>Contains {cluster_df.iloc[best_cluster_idx]['Size']} restaurants</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Overall rating distribution
                    avg_rating = df_clean['Aggregate rating'].mean()
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>📈 Rating Overview</h4>
                        <p>Average rating across all locations: <strong>{avg_rating:.2f}</strong></p>
                        <p>Rating range: {df_clean['Aggregate rating'].min():.1f} to {df_clean['Aggregate rating'].max():.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            st.error(f"❌ Required columns 'Longitude' and 'Latitude' not found in the dataset.")
            st.info("Please upload a dataset that contains both geographic coordinate columns.")

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please check that your CSV file contains valid geographic data.")
else:
    # Welcome message
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background-color: #e8f5e9; border-radius: 10px;'>
            <h3>🚀 Explore Restaurant Geography</h3>
            <p>Upload a CSV file containing restaurant data with longitude and latitude coordinates to analyze:</p>
            <ul style='text-align: left; display: inline-block;'>
                <li>Interactive maps with different visualization types</li>
                <li>Spatial clustering analysis</li>
                <li>Density heatmaps and distribution charts</li>
                <li>Geographic patterns and restaurant hubs</li>
                <li>Rating-based geographic insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)