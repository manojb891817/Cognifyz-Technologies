import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- Streamlit setup ----------------
st.set_page_config(page_title="Task 3 - Price Range Distribution", layout="centered")
st.title("💰 Price Range Distribution")
st.markdown("### Level 1 - Task 3")
st.write("Visualize how restaurants are distributed across different price ranges.")

# ---------------- File uploader ----------------
uploaded_file = st.file_uploader("📂 Upload your restaurant dataset (CSV)", type=["csv"])

if uploaded_file is not None:
    # Load CSV
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")

    # Show column names
    st.write("Columns in CSV:", df.columns.tolist())

    # ---------------- Detect price column ----------------
    price_col = None
    for col in df.columns:
        if 'price' in col.lower():  # check for any column containing 'price'
            price_col = col
            break

    if price_col:
        st.success(f"✅ Found price column: {price_col}")

        # 1️⃣ Count number of restaurants in each price range
        price_counts = df[price_col].value_counts().reset_index()
        price_counts.columns = ['Price Range', 'Count']

        # 2️⃣ Calculate percentage
        total = price_counts['Count'].sum()
        price_counts['Percentage'] = (price_counts['Count'] / total) * 100
        price_counts['Percentage'] = price_counts['Percentage'].round(2)

        # Display table
        st.subheader("📊 Price Range Distribution Table")
        st.dataframe(price_counts.style.background_gradient(cmap="Purples"))

        # 3️⃣ Visualization (bar chart)
        st.subheader("📈 Price Range Distribution")
        fig, ax = plt.subplots(figsize=(6, 4))  # smaller figure
        sns.barplot(x="Price Range", y="Count", data=price_counts, palette="mako", ax=ax)
        ax.set_title("Distribution of Price Ranges", fontsize=12)
        ax.set_xlabel("Price Range", fontsize=10)
        ax.set_ylabel("Number of Restaurants", fontsize=10)
        ax.tick_params(axis='x', rotation=0)
        ax.tick_params(axis='y', labelsize=9)
        st.pyplot(fig)

        # 4️⃣ Pie chart
        st.subheader("🥧 Price Range Percentage")
        fig2, ax2 = plt.subplots(figsize=(4, 4))  # smaller figure
        ax2.pie(price_counts['Percentage'], labels=price_counts['Price Range'],
                autopct='%1.1f%%', startangle=90,
                colors=sns.color_palette("mako", len(price_counts)))
        ax2.set_title("Percentage of Restaurants by Price Range", fontsize=12)
        st.pyplot(fig2)

    else:
        st.error("❌ No column related to price found in your CSV. Please check the file.")
else:
    st.info("👆 Upload a CSV file to begin the analysis.")
