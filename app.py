
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Nassau Candy Profitability Dashboard", layout="wide")

# Data load karo
@st.cache_data
def load_data():
    df = pd.read_csv("Nassau Candy Distributor (3) (1).csv")
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d-%m-%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d-%m-%Y')
    df['Gross Margin %'] = (df['Gross Profit'] / df['Sales']) * 100
    df['Profit per Unit'] = df['Gross Profit'] / df['Units']
    return df

df = load_data()

st.title("🍬 Nassau Candy Distributor — Profitability Dashboard")

st.sidebar.header("Filters")

# Date range filter
min_date = df['Order Date'].min()
max_date = df['Order Date'].max()
date_range = st.sidebar.date_input("Order Date Range", [min_date, max_date])

# Division filter
divisions = st.sidebar.multiselect("Division", options=df['Division'].unique(), default=df['Division'].unique())

# Margin threshold slider
margin_threshold = st.sidebar.slider("Minimum Gross Margin %", 0, 100, 0)

# Product search
search_term = st.sidebar.text_input("Search Product Name")

# Filters apply karo
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1])) &
    (df['Division'].isin(divisions)) &
    (df['Gross Margin %'] >= margin_threshold)
]

if search_term:
    filtered_df = filtered_df[filtered_df['Product Name'].str.contains(search_term, case=False)]

tab1, tab2, tab3, tab4 = st.tabs([
    "Product Profitability",
    "Division Performance",
    "Cost vs Margin Diagnostics",
    "Profit Concentration (Pareto)"
])

with tab1:
    st.subheader("Product-Level Profitability")

    product_summary = filtered_df.groupby('Product Name').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Total_Units=('Units', 'sum')
    ).reset_index()
    product_summary['Gross Margin %'] = (product_summary['Total_Profit'] / product_summary['Total_Sales']) * 100
    product_summary = product_summary.sort_values('Total_Profit', ascending=False)

    st.dataframe(product_summary)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=product_summary, x='Product Name', y='Total_Profit', ax=ax)
    plt.xticks(rotation=90)
    st.pyplot(fig)

with tab2:
    st.subheader("Division-Level Performance")

    division_summary = filtered_df.groupby('Division').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Profit=('Gross Profit', 'sum')
    ).reset_index()
    division_summary['Gross Margin %'] = (division_summary['Total_Profit'] / division_summary['Total_Sales']) * 100

    st.dataframe(division_summary)

    fig, ax = plt.subplots(figsize=(8, 5))
    division_summary.set_index('Division')[['Total_Sales', 'Total_Profit']].plot(kind='bar', ax=ax)
    st.pyplot(fig)

with tab3:
    st.subheader("Cost vs Margin Diagnostics")

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=product_summary, x='Total_Sales', y='Gross Margin %', hue='Product Name', s=100, ax=ax)
    st.pyplot(fig)

    st.write("Margin-risk products (below 50% margin):")
    st.dataframe(product_summary[product_summary['Gross Margin %'] < 50])

with tab4:
    st.subheader("Profit Concentration (Pareto Analysis)")

    pareto = product_summary.sort_values('Total_Profit', ascending=False).copy()
    pareto['Cumulative Profit %'] = (pareto['Total_Profit'].cumsum() / pareto['Total_Profit'].sum()) * 100

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.bar(pareto['Product Name'], pareto['Total_Profit'])
    plt.xticks(rotation=90)

    ax2 = ax1.twinx()
    ax2.plot(pareto['Product Name'], pareto['Cumulative Profit %'], color='red', marker='o')
    ax2.axhline(80, color='green', linestyle='--')

    st.pyplot(fig)