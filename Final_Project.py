"""
CS230-8
Paulina Shilova
November 11th, 2025
New York Housing Data

This app allows users to look at New York Housing with different filters, graphs, and a map.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------- LOADING THE DATA ---------------------- #

def get_data():
    return pd.read_csv('NY-House-Dataset.csv')

df = get_data()

# ---------------------- CLEANING ---------------------- #

# [FUNC2P]
def clean_house_type(house_type, default=None):

    # formats the house types to remove extra types and "for sale" at the end of the types
    t = str(house_type).lower()

    if "townhouse" in t:
        return 'Townhouse'
    if "condop" in t:
        return 'Condop'
    if "condo" in t:
        return 'Condo'
    if "mobile house" in t:
        return 'Mobile house'
    if "multi-family" in t:
        return 'Multi-family'
    if "co-op" in t:
        return 'Co-op'
    if "house" in t:
        return 'House'

    return default # removes "for sale, land, pending, etc."

# applies the cleaning function to the TYPE column
df["CLEAN_TYPE"] = df["TYPE"].apply(clean_house_type)

# keeps only rows with valid house types
df_clean = df[df["CLEAN_TYPE"].notna()]

# [COLUMNS]
# scales the price into $1,000,000s units, makes it easier for visuals/filters
df_clean["PRICE_SCALED"] = df_clean["PRICE"] / 1000000

# [FUNCRETURN2]
def get_price(df_clean):
    min_price = df_clean["PRICE"].min()
    max_price = df_clean["PRICE"].max()
    return min_price, max_price

# sorted and unique sublocalities and house types
sublocalities = sorted(df_clean["SUBLOCALITY"].dropna().unique())
house_types = sorted(df_clean["CLEAN_TYPE"].dropna().unique())

# ---------------------- APP HEADER ---------------------- #

# [ST3]
st.sidebar.title("New York Housing Market")
st.sidebar.markdown("Welcome to the **New York Housing Market App**! "
            "This app allows you to explore the housing market in New York with different kind of filters and visuals."
)

# ---------------------- MAP ---------------------- #

st.subheader("Map of New York Listings")

st.markdown("Below is a map of **all** of the listings and their location.")

# [MAP]
# drops the missing latitude or longitude rows
map_df = df.dropna(subset=["LATITUDE", "LONGITUDE"])

# creates the map of all the listings
st.map(map_df[["LATITUDE", "LONGITUDE"]])

# ---------------------- QUERY 1 ---------------------- #

st.subheader("Query 1: Average Price by Sublocality")

# [ST1]
select_sublocality = st.selectbox("Select a sublocality:", sublocalities)
select_house_type = st.radio("Select a house type:", house_types, key="house_type_q1")

# [LISTCOMP]
# creates a short list of house types
simple_house_types = [t for t in house_types if len(t) < 10]

# [FILTER2]
# filters rows that match users selections
query1_df = df_clean[
    (df_clean["SUBLOCALITY"] == select_sublocality) &
    (df_clean["CLEAN_TYPE"] == select_house_type)
]

# [MAXMIN]
# displays the average price with the filters and displays low and high price
if len(query1_df) > 0:
    avg_price_selected = query1_df["PRICE"].mean()
    st.write(f"Average price for a {select_house_type} in {select_sublocality}: **${avg_price_selected:,.0f}**")

    # [FUNCCALL2]
    low_price, high_price = get_price(query1_df)
    st.write(f"Lowest price: ${low_price:,.0f}")
    st.write(f"Highest price: ${high_price:,.0f}")

# displays a message if no listings match filters
else:
    st.write("No listings found for this filter.")

# --------------- BAR CHART --------------- #

st.subheader(f"Average Price (in millions) of {select_house_type} Across Available Neighborhoods")

# [CHART1]
# creates a bar chart showing average price per neighborhood for selected house type
def bar_chart_average_prices(df, house_type):

    # filter by the selected house type
    filtered_df = df[df["CLEAN_TYPE"] == house_type]

    # [SORT]
    # calculate the average price by the neighborhood
    average_price = (filtered_df.groupby("SUBLOCALITY")["PRICE"]
                     .mean().sort_values(ascending=False))

    # creates the figure
    fig, axes = plt.subplots(figsize=(10, 4))

    # plots the bars
    axes.bar(average_price.index, average_price.values)

    # formats and sets different axes labels and title
    axes.set_xticklabels(average_price.index, rotation=45, ha="right")
    axes.set_title(f"Average Price of {house_type}s Across Neighborhoods")
    axes.set_ylabel("Average Price ($)")
    axes.set_xlabel("Neighborhood")

    return fig

# displaying bar chart
st.pyplot(bar_chart_average_prices(df_clean, select_house_type))

# ---------------------- QUERY 2 (Find all house types that have a specific # of bedrooms and bathrooms) ---------------------- #

st.subheader("Query 2: Comparing house types and # of bedrooms and bathrooms with price")

# radio for selecting house type
query2_type_select = st.radio("Select a house type:", house_types, key="house_type_q2")

#[MAXMIN]
# slider for the number of bedroom selection
min_bedrooms = int(df_clean["BEDS"].min())
max_bedrooms = int(df_clean["BEDS"].max())

# [ST2]
select_bedrooms = st.slider("Select a number of bedrooms:", min_bedrooms, max_bedrooms, min_bedrooms)

# [ST2]
# slider to select number of bathrooms
min_bathrooms = int(df_clean["BATH"].min())
max_bathrooms = int(df_clean["BATH"].max())
select_bathrooms = st.slider("Select a number of bathrooms:", min_bathrooms, max_bathrooms, min_bathrooms)

# [FILTER1]
# filtering the data for what the user selected
filter_df_q2 = df_clean[
    (df_clean["CLEAN_TYPE"] == query2_type_select) &
    (df_clean["BEDS"] <= select_bedrooms) &
    (df_clean["BATH"] <= select_bathrooms)]

# --------------- SCATTERPLOT --------------- #

st.subheader("Scatterplot:")

# [CHART2]
# creates a scatterplot for bedrooms vs bathrooms, bubble sizes corresponds to price
def scatterplot_beds_baths(df):

    fig, axes = plt.subplots(figsize=(10, 6))

    # scaled the price for better visibility in color and size
    price_scaled_down = df["PRICE"] / 1000000

    scatter = axes.scatter(
        df["BEDS"],
        df["BATH"],
        s=price_scaled_down * 30,  # bubble size
        c=price_scaled_down,  # bubble color
        alpha=0.6
    )

    axes.set_title(f"Bedrooms vs Bathrooms by Price", fontsize=16, fontweight="bold")
    axes.set_ylabel("Number of Bedrooms", fontsize=14)
    axes.set_xlabel("Number of Bathrooms", fontsize=14)
    axes.grid(True)

    # adding color bars to show price in millions
    cbar = fig.colorbar(scatter)
    cbar.set_label("Price ($, in millions)")

    return fig

# displaying chart
st.pyplot(scatterplot_beds_baths(filter_df_q2))

st.markdown("Each point on the chart represents a home. Larger bubbles and changes in color indicate higher prices.")

# ---------------------- QUERY 3 (Find homes under a specific price in sublocality) ---------------------- #

st.subheader("Query 3: Find homes under a specific price in sublocality")

# [ST1]
# creates multiselect for neighborhoods
query3_sublocality = st.multiselect("Select neighborhoods:", sublocalities)

# creates selectbox for house type
query3_type = st.selectbox("Select a house type:", house_types, key="house_type_q3")

# [MAXMIN]
# gets minimum and maximum price for slider
min_price = float(df_clean["PRICE_SCALED"].min())
max_price = float(df_clean["PRICE_SCALED"].max())

# slider to select the max price in millions
select_price = st.slider(
    f"Select maximum price (in $1,000,000s):",
    min_price,
    max_price,
    min_price,
)

st.write(f"Showing homes under **${select_price * 1000000:,.0f}**")

# filter based on house type and price
query3_df = df_clean[
    (df_clean["CLEAN_TYPE"] == query3_type) &
    (df_clean["PRICE_SCALED"] <= select_price)
]

# [FUNCCALL2]
query3_min_price, query3_max_price = get_price(query3_df)

# filter by selected sublocalities
if query3_sublocality:
    query3_df = query3_df[query3_df["SUBLOCALITY"].isin(query3_sublocality)]

# --------------- UPDATES MAP BASED ON QUERY 3 FILTERS --------------- #

st.subheader("Map of Filtered Homes")

# drops the rows with missing latitude nad longitude
map_filtered = query3_df.dropna(subset=["LATITUDE", "LONGITUDE"])

# displays the map with the filters
st.map(map_filtered[["LATITUDE", "LONGITUDE"]])

# --------------- TABLE --------------- #

st.subheader("Matching listings")
st.write(f"Showing **{len(query3_df)}** properties:")

# copy and format the price column for the table
display_price = query3_df.copy()

# [LAMBDA]
display_price["PRICE"] = display_price["PRICE"].apply(lambda x: f"{x:,.0f}")

# displays the dataframe with the columns selected below
st.dataframe(display_price[[
    f"PRICE",
    "BEDS",
    "BATH",
    "CLEAN_TYPE",
    "SUBLOCALITY",
    "ADDRESS"
]])