import streamlit as st
import pandas as pd
from PIL import Image

# Load the logo
logo = Image.open("logo.jpg")

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
page = st.sidebar.radio("Go to:", ["🚘 Car Price Insights Hub", "🔍 Predict Your Car’s Value"])


# Display logo and title together
col1, col2 = st.columns([1, 8])  # Adjust column ratio for logo and title

with col1:
    st.image(logo, width=80)  # Adjust logo width as needed

with col2:
    st.markdown("<h1 style='margin: 0; font-size: 2rem;'>Your Ultimate Auto Price Guide</h1>", unsafe_allow_html=True)

st.markdown("### Find out the price range for your desired car.")
st.markdown("---")

if page == "🚘 Car Price Insights Hub":
    # Summary Statistics Page
    st.title("🚘 Car Price Insights Hub")
    st.markdown("### Explore car prices and filter data by brand, model, and year")

    # Filters for brand, model, and year (above table)
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

    year_filter = st.slider(
        "Filter by Manufacturing Year:",
        min_year,
        max_year,
        (min_year, max_year)
    )

    # Apply filters to the table
    filtered_table = df.copy()
    if table_brand_filter != "All":
        filtered_table = filtered_table[filtered_table["Car Brand"] == table_brand_filter]
    if table_model_filter != "All":
        filtered_table = filtered_table[filtered_table["Car Model"] == table_model_filter]
    filtered_table = filtered_table[
        (filtered_table["Manufacturing Year"] >= year_filter[0]) & 
        (filtered_table["Manufacturing Year"] <= year_filter[1])
    ]

    filtered_table=filtered_table[
                [
                    "Car Brand", 
                    "Car Model", 
                    "Manufacturing Year", 
                    "Average Price (KDW)", 
                    "Minimum Price (KDW)", 
                    "Maximum Price (KDW)"
                ]
            ].round()
    # Format table with styling
    if not filtered_table.empty:

        styled_table = filtered_table.style.format({
            "Average Price (KDW)": "{:.0f}",
            "Minimum Price (KDW)": "{:.0f}",
            "Maximum Price (KDW)": "{:.0f}",
        }).set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'center')]},  # Center align column headers
            {'selector': 'td', 'props': [('text-align', 'center'), ('width', '10px')]},  # Limit column width
        ]).background_gradient(
            subset=["Average Price (KDW)", "Minimum Price (KDW)", "Maximum Price (KDW)"],
            cmap="Blues"
        )

        st.dataframe(styled_table, use_container_width=False)
        # Download button for filtered data
        csv = filtered_table.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_car_prices.csv",
            mime="text/csv",
        )
    else:
        st.warning("No data matches the selected filters.")
elif page == "🔍 Predict Your Car’s Value":
    # Price Look-Up Page
    st.title("🔍 Predict Your Car’s Value")
    st.markdown("### Find the price range for a specific car based on filters")

    # Sidebar filters for the price look-up
    brand = st.sidebar.selectbox(
        "Select Car Brand", 
        options=["Select..."] + list(df["Car Brand"].unique()), 
        help="Choose the manufacturer of the car."
    )

    # Ensure the user selects a brand before showing the model dropdown
    if brand != "Select...":
        model = st.sidebar.selectbox(
            "Select Car Model",
            options=["Select..."] + list(df[df["Car Brand"] == brand]["Car Model"].unique()),
            help="Choose the model of the car based on the selected brand."
        )
    else:
        model = None

    # Show the year input only if both brand and model are selected
    if brand != "Select..." and model != "Select...":
        year_input = st.sidebar.number_input(
            "Enter the car's year:",
            min_value=min_year,
            max_value=max_year,
            step=1,
            help="Specify the year of the car for price lookup."
        )
    else:
        year_input = None

    # Display search results only if all filters are selected
    if brand != "Select..." and model != "Select..." and year_input:
        st.subheader(f"Search Results for {brand} {model} ({year_input})")
        st.write("Here are the results based on the selected filters and nearby years:")

        filtered_df = df[
            (df["Car Brand"] == brand) & 
            (df["Car Model"] == model) & 
            (df["Manufacturing Year"] == year_input)
        ]

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
            if not filtered_df.empty:
                average_price = filtered_df["Average Price (KDW)"].mean()
                lower_bound = filtered_df["Minimum Price (KDW)"].mean()
                upper_bound = filtered_df["Maximum Price (KDW)"].mean()

                st.success(f"**Average Price:** {average_price:.0f} KDW")
                st.info(
                    f"💰 **Price Range:** {lower_bound:.0f} KDW - {upper_bound:.0f} KDW"
                )
            else:
                st.error("⚠️ No data available for the selected year or nearby years.")
    else:
        st.warning("Please select a car brand, model, and year to view the price range.")
