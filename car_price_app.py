import streamlit as st
import pandas as pd

# Load the dataset
df = pd.read_csv("cars.csv")
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df.dropna()
df['Year'] = df['Year'].astype(int)

# Rename columns for consistency
df.rename(
    columns={
        "car_brand": "Car Brand",
        "car_model": "Car Model",
        "Year": "Manufacturing Year",
        "average_price": "Average Price (KDW)",
        "percentile_0": "Minimum Price (KDW)",
        "percentile_100": "Maximum Price (KDW)"
    },
    inplace=True
)

# Check the minimum and maximum years
min_year = int(df['Manufacturing Year'].min())
max_year = int(df['Manufacturing Year'].max())

# Set up page selection
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["📊 Summary Statistics", "🔍 Price Look-Up"])

# Display the logo on each page
# Display company logo and title on both pages
st.image("logo.jpg", width=150)  # Replace with your logo path
st.title("4Sale. 🚗 Car Price Lookup")
st.markdown("### Find out the price range for your desired car 🚘")
st.markdown("---")

if page == "📊 Summary Statistics":
    # Summary Statistics Page
    st.title("📊 Summary Statistics for Car Prices")
    st.markdown("### Explore car prices and filter data by brand and model")

    # Filters for brand and model (above table)
    table_brand_filter = st.selectbox(
        "Filter by Car Brand:", 
        options=["All"] + list(df["Car Brand"].unique())
    )

    if table_brand_filter != "All":
        table_model_filter = st.selectbox(
            "Filter by Car Model:", 
            options=["All"] + list(df[df["Car Brand"] == table_brand_filter]["Car Model"].unique())
        )
    else:
        table_model_filter = st.selectbox(
            "Filter by Car Model:", 
            options=["All"] + list(df["Car Model"].unique())
        )

    # Apply filters to the table
    filtered_table = df.copy()
    if table_brand_filter != "All":
        filtered_table = filtered_table[filtered_table["Car Brand"] == table_brand_filter]
    if table_model_filter != "All":
        filtered_table = filtered_table[filtered_table["Car Model"] == table_model_filter]

    # Display the filtered or default table
    st.write(filtered_table[
        [
            "Car Brand", 
            "Car Model", 
            "Manufacturing Year", 
            "Average Price (KDW)", 
            "Minimum Price (KDW)", 
            "Maximum Price (KDW)"
        ]
    ].round())

elif page == "🔍 Price Look-Up":
    # Price Look-Up Page
    st.title("🔍 Car Price Look-Up")
    st.markdown("### Find the price range for a specific car based on filters")

    # Sidebar filters for the price look-up
    brand = st.sidebar.selectbox(
        "Select Car Brand", 
        options=df["Car Brand"].unique(), 
        help="Choose the manufacturer of the car."
    )
    model = st.sidebar.selectbox(
        "Select Car Model",
        options=df[df["Car Brand"] == brand]["Car Model"].unique(),
        help="Choose the model of the car based on the selected brand."
    )
    year_input = st.sidebar.number_input(
        "Enter the car's year:",
        min_value=min_year,
        max_value=max_year,
        step=1,
        help="Specify the year of the car for price lookup."
    )

    # Display search results
    st.subheader(f"Search Results for {brand} {model} ({year_input})")
    st.write("Here are the results based on the selected filters and nearby years:")

    filtered_df = df[(df["Car Brand"] == brand) & (df["Car Model"] == model) & (df["Manufacturing Year"] == year_input)]

    # Calculate average price and price range
    if not filtered_df.empty:
        average_price = filtered_df["Average Price (KDW)"].mean()
        lower_bound = filtered_df["Minimum Price (KDW)"].mean()
        upper_bound = filtered_df["Maximum Price (KDW)"].mean()

        st.success(f"**Average Price:** {average_price:.0f} KDW")
        st.info(
            f"💰 **Price Range:** {lower_bound:.0f} KDW - {upper_bound:.0f} KDW"
        )
    else:
        above_year = year_input + 1
        below_year = year_input - 1
        filtered_df = df[
            (df["Car Brand"] == brand) & 
            (df["Car Model"] == model) & 
            (df["Manufacturing Year"].between(below_year, above_year))
        ]
        if filtered_df.shape[0] == 2:
            average_price = filtered_df["Average Price (KDW)"].mean()
            lower_bound = filtered_df["Minimum Price (KDW)"].mean()
            upper_bound = filtered_df["Maximum Price (KDW)"].mean()

            st.success(f"**Average Price:** {average_price:.0f} KDW")
            st.info(
                f"💰 **Price Range:** {lower_bound:.0f} KDW - {upper_bound:.0f} KDW"
            )
        else:
            st.error("⚠️ No data available for the selected year or nearby years.")