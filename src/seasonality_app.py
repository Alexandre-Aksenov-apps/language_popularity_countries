"""
Extract the Time Series for "Python" from Google Trends data.
Compute the standard deviation of the periodic component
/ that of the time series.

Version 1. Runs on the local machine in Command Line.
Version 2. Runs as a local Streamlit server.
"""

# import polars as pl
# import numpy as np

from functions.part_std_periodic import part_std_periodic
from functions.fetch_google_trends_2010_2025 import fetch_google_trends_polars
from functions.code_opt_country_name import code2opt_name

import streamlit as st
import json

# For plotting the data
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


st.set_page_config(
    page_title="Seasonal trend in Python searches per country",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
* Data.

This app shows the seasonal trend in Python searches per country.
It is based on Google Trends data from 2010 to 2025,
therefore the data can reflect IT activity only in the countries, where Google
is the predominant search engine.

* Part of seasonality.
    * It is estimated on basis of the seasonal decomposition of the time series.
    * The ratio of the standard deviation of the seasonal component 
    to the total standard deviation of the time series is computed and shown.

How to use the app:
* Enter the 2-letter code of a country in the text input field.
* The app will show the part of seasonality in Python searches for the country.
* It also plots the number of searches per month normalized to the maximum,
shown as 100.
    * The ticks on X-axis show September of each year,
to make start of the school-year visible. 
""")

code_country = st.text_input("Code of a country", "FR", max_chars=2)

if code_country and len(code_country) == 2:
    # switch to uppercase
    code_country = code_country.upper()

    # Try to extract the name
    country_name = code2opt_name(code_country)

    if country_name:
        # Load the data
        try:
            df = fetch_google_trends_polars(geo=code_country)

            if df is not None:
                data_column = "search_interest"
                ratio = part_std_periodic(df[data_column])
                st.write(f"Part of seasonality in Py searches for {country_name}: {ratio:.2f}")

                # Plot
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.plot(df["date"], df["search_interest"], label="Python")

                ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=9))

                # Format the tick labels, e.g. "Sep 2020" or "2020-09"
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

                # Rotate and align date tick labels nicely
                fig.autofmt_xdate(rotation=45)

                ax.set_xlabel("Time")
                ax.set_ylabel("Popularity")
                ax.grid(True, linestyle="--", alpha=0.5)

                st.pyplot(fig)

            else:
                st.write("Could not connect to Google Trends. Please, try again later.")
        except json.decoder.JSONDecodeError:  # can occur at 'fetch_google_trends_polars'
            st.write("Could not decode the reply of Google Trends. Please, file an issue to the author.")
    else:
        st.write("This country has not been found.")
else:
    st.write("Please enter a valid country code.")

# if __name__ == "__main__":
#     main()

st.markdown("""
-----
Some results in Western Europe and North America.

High seasonality:

| Country | Ratio |
|---------|-------|
| FR      | 0.23  |
| BE      | 0.25  |
| CZ      | 0.29  |

Low seasonality:

| Country | Ratio |
|---------|-------|
| DE      | 0.11  |

Most values are located between 0.15 and 0.20:

| Country | Ratio |
|---------|-------|
| PL      | 0.16  |
| CH      | 0.17  |
| NL      | 0.17  |
| IT      | 0.18  |
| US      | 0.18  |
| CA      | 0.19  |
| GB      | 0.20  |
| ES      | 0.20  |
""")
