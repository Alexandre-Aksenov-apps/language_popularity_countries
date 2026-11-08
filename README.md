**Python popularity by country.**

This app aims to specialize the data of [TIOBE "Language popularity index"](https://www.tiobe.com/tiobe-index/) to its most popular language, Python, and to countries.

The app shows data for France (`FR`), then prompts its user to write the code of a country.

The data is collected and analyzed in real time. The data comes from Google Trends. Analysis is quite basic: the importance of seasonal trend is estimated, and the data is plotted with an X-tick at the month of September of each year. This analysis shows the influence of school in the IT ecosystem of each country.
The results show that France is close to Belgium and shows higher seasonality than most "Western" countries!

Other examples of questions showing the importance of school in the professional activity are welcome!

**Deployment**

The app is deployed at:
https://pythonpopularitycountries.streamlit.app/

**Known issue:** 

The app depends on the ability of Streamlit to connect to Google servers. It has been observed to be more stable in the morning (CEST).