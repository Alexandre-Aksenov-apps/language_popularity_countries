# trends.google.com -> CSV file using `requests`.
# Fixed from suggestion by Junie .
# This function is adapted to Google API of 31/10/2026

import json
import urllib.parse
import polars as pl
import requests


def gtrends_url(keyword: str = "/m/05z1_",
                geo: str = "FR",
                time_range: str = "2010-01-01 2025-12-31",
                hl: str = "en-US") -> str:
    # 2. Query the explore endpoint to get widget tokens
    req_payload = {
        "comparisonItem": [{"keyword": keyword, "geo": geo, "time": time_range}],
        "category": 0,
        "property": "",
    }

    explore_params = {
        "hl": hl,
        "req": json.dumps(req_payload),
        "tz": "-60",
    }

    explore_url = f"https://trends.google.com/trends/api/explore?{urllib.parse.urlencode(explore_params)}"
    return explore_url


def fetch_google_trends_csv(
    keyword: str = "/m/05z1_",
    # Google Knowledge Graph entity for Python (Programming Language)
    geo: str = "FR",
    time_range: str = "2010-01-01 2025-12-31",  # e.g., "all", "today 5-y", "today 12-m"
    hl: str = "en-US",
) -> str | None:
    """
    Fetch Google Trends CSV data for a given keyword, region, time range,
    and language.

    :param keyword: The keyword to search for.
    :param geo: The geographic location to search for.
    :param time_range: The time range to search for.
    :param hl: The language to search for.

    :return: The CSV data as a string,
    or None if an error on the side of connection to Google Trends occurred.

    Raises:
    json.decoder.JSONDecodeError if the prefix of Google Trends response
        is not as expected.

    """
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    # 1. Warm up session / cookies
    session.get("https://trends.google.com/?geo=" + geo)

    explore_url = gtrends_url(keyword, geo, time_range, hl)

    try:
        response = session.get(explore_url)
        response.raise_for_status()  # can fail in case of issue at Google Trends

        # Google Trends prefixes JSON responses with ")]}'\n" to avoid XSSI
        raw_text = response.text

        # Arbitrary data from Google API. Google may change this prefix.
        if raw_text.startswith(")]}"):
            raw_text = raw_text.split("\n", 1)[1]

        data = json.loads(raw_text)
        # This panics if JSON has not been correctly extracted from 'response':

        # JSONDecodeError("Expecting value", s, err.value) from None
        # json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

        # 3. Locate the 'TIMESERIES' widget token and request payload
        timeseries_widget = None
        for widget in data.get("widgets", []):
            if widget.get("id") == "TIMESERIES":
                timeseries_widget = widget
                break

        if not timeseries_widget:
            raise ValueError("Could not find TIMESERIES widget in Google Trends response.")

        token = timeseries_widget["token"]
        widget_req = json.dumps(timeseries_widget["request"])

        # 4. Fetch the CSV directly
        csv_params = {
            "hl": hl,
            "req": widget_req,
            "token": token,
            "tz": "-60",
        }
        csv_url = f"https://trends.google.com/trends/api/widgetdata/multiline/csv?{urllib.parse.urlencode(csv_params)}"
        csv_response = session.get(csv_url)
        csv_response.raise_for_status()

        return csv_response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google Trends data: {e}")
        return None


def load_trends_to_polars(csv_text: str) -> pl.DataFrame:
    """
    Google Trends CSVs contain header metadata lines
    (e.g., 'Category: All categories')
    Use skip_rows to skip metadata before the column header row
    (typically line 2 or 3)
    """
    df_result = pl.read_csv(
        csv_text.encode("utf-8"),
        skip_rows=2,
    )

    # Clean and cast columns:
    # 1. First column (Month) parsed as Date
    # 2. Second column (Score) cleaned for any '<1' values and cast to Int64
    date_col = df_result.columns[0]
    score_col = df_result.columns[1]

    df_result = df_result.with_columns(
        [
            pl.col(date_col).str.to_date("%Y-%m").alias("date"),
            pl.col(score_col)
            .cast(pl.Utf8)
            .str.replace("<1", "0")
            .cast(pl.Int64, strict=False)
            .alias("search_interest"),
        ]
    ).select(["date", "search_interest"])

    return df_result


def fetch_google_trends_polars(
    keyword: str = "/m/05z1_",
    # Google Knowledge Graph entity for Python (Programming Language)
    geo: str = "FR",
    time_range: str = "2010-01-01 2025-12-31",
) -> pl.DataFrame | None:
    csv_content = fetch_google_trends_csv(
        keyword,
        geo,
        # time_range="all"
        time_range
    )

    if csv_content is None:
        return None
    df = load_trends_to_polars(csv_content)
    return df


if __name__ == "__main__":
    csv_content = fetch_google_trends_csv(
        keyword="/m/05z1_",
        geo="FR",
        # time_range="all"
        time_range="2010-01-01 2025-12-31"
    )

    if csv_content is None:
        print("Failed to fetch Google Trends data.")
        exit(1)

    df = load_trends_to_polars(csv_content)
    print(df)
