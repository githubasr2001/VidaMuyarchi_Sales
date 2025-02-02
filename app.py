import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta

# Define cities
cities = {
    "hyderabad": {
        "regionCode": "HYD",
        "subRegionCode": "HYD",
        "regionSlug": "hyderabad",
        "latitude": "17.385044",
        "longitude": "78.486671"
    },
    "mumbai": {
        "regionCode": "MUMBAI",
        "subRegionCode": "MUMBAI",
        "regionSlug": "mumbai",
        "latitude": "19.076",
        "longitude": "72.8777"
    },
    "bengaluru": {
        "regionCode": "BANG",
        "subRegionCode": "BANG",
        "regionSlug": "bengaluru",
        "latitude": "12.971599",
        "longitude": "77.594563"
    },
   
    "chennai": {
        "regionCode": "CHEN",
        "subRegionCode": "CHEN",
        "regionSlug": "chennai",
        "latitude": "13.056",
        "longitude": "80.206"
    }
    
}

@st.cache_data(ttl=1800)
def fetch_showtimes(city):
    date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"https://in.bookmyshow.com/api/movies-data/showtimes-by-event?appCode=MOBAND2&appVersion=14304&language=en&eventCode=ET00408788&regionCode={city['regionCode']}&subRegion={city['subRegionCode']}&bmsId=1.21345445.1703250084656&token=67x1xa33b4x422b361ba&lat={city['latitude']}&lon={city['longitude']}&query=&date={date}"

    headers = {
        "Host": "in.bookmyshow.com",
        "x-bms-id": "1.21345445.1703250084656",
        "x-region-code": city['regionCode'],
        "x-subregion-code": city['subRegionCode'],
        "x-region-slug": city['regionSlug'],
        "x-platform": "AND",
        "x-platform-code": "ANDROID",
        "x-app-code": "MOBAND2",
        "x-device-make": "Google-Pixel XL",
        "x-screen-height": "2392",
        "x-screen-width": "1440",
        "x-screen-density": "3.5",
        "x-app-version": "14.3.4",
        "x-app-version-code": "14304",
        "x-network": "Android | WIFI",
        "x-latitude": city['latitude'],
        "x-longitude": city['longitude'],
        "x-ab-testing": "adtechHPSlug=default",
        "x-location-selection": "manual",
        "x-location-shared": "false",
        "lang": "en",
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel XL Build/SP2A.220505.008)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def process_showtime_data(data):
    if not data or not data.get("ShowDetails"):
        return [], 0, 0, 0, "0.00", "0.00", "0.00%"

    results = []
    grand_total_max_seats = grand_total_seats_available = grand_total_booked_tickets = 0
    grand_total_gross = grand_booked_gross = 0
    total_shows = fast_filling_shows = sold_out_shows = 0

    for show_detail in data["ShowDetails"]:
        for venue in show_detail["Venues"]:
            for show_time in venue["ShowTimes"]:
                total_shows += 1
                total_max_seats = total_seats_available = total_booked_tickets = 0
                total_gross = booked_gross = 0

                for category in show_time["Categories"]:
                    max_seats = int(category.get("MaxSeats", 0))
                    seats_avail = int(category.get("SeatsAvail", 0))
                    booked_tickets = max_seats - seats_avail
                    current_price = float(category.get("CurPrice", 0))

                    total_max_seats += max_seats
                    total_seats_available += seats_avail
                    total_booked_tickets += booked_tickets
                    total_gross += max_seats * current_price
                    booked_gross += booked_tickets * current_price

                if total_seats_available == 0:
                    sold_out_shows += 1
                elif (total_max_seats - total_seats_available) / total_max_seats >= 0.5:
                    fast_filling_shows += 1

                grand_total_max_seats += total_max_seats
                grand_total_seats_available += total_seats_available
                grand_total_booked_tickets += total_booked_tickets
                grand_total_gross += total_gross
                grand_booked_gross += booked_gross

                results.append({
                    "Venue Name": venue["VenueName"],
                    "Show Time": show_time["ShowTime"],
                    "Max Seats": total_max_seats,
                    "Seats Available": total_seats_available,
                    "Booked Tickets": total_booked_tickets,
                    "Occupancy": f"{(total_booked_tickets / total_max_seats) * 100:.2f}%",
                    "Total Gross": f"{total_gross:.2f}",
                    "Booked Gross": f"{booked_gross:.2f}"
                })

    total_occupancy = f"{(grand_total_booked_tickets / grand_total_max_seats) * 100:.2f}%" if grand_total_max_seats else "0.00%"
    return results, total_shows, fast_filling_shows, sold_out_shows, f"{grand_booked_gross:.2f}", f"{grand_total_gross:.2f}", total_occupancy

# Streamlit App
st.title("BMS Dashboard")
st.sidebar.title("Filters")

city_name = st.sidebar.selectbox("Select City", list(cities.keys()), format_func=lambda x: x.capitalize())
city = cities[city_name]

st.sidebar.markdown("---")

# Fetch and process data
data = fetch_showtimes(city)
show_results, total_shows, fast_filling_shows, sold_out_shows, booked_gross, total_gross, total_occupancy = process_showtime_data(data)

# Display metrics
st.header(f"Metrics for {city_name.capitalize()}")
col1, col2, col3 = st.columns(3)
col1.metric("Total Shows", total_shows)
col2.metric("Fast Filling Shows", fast_filling_shows)
col3.metric("Sold Out Shows", sold_out_shows)

col1, col2 = st.columns(2)
col1.metric("Total Gross (INR)", total_gross)
col2.metric("Booked Gross (INR)", booked_gross)

st.metric("Total Occupancy", total_occupancy)

# Display detailed show data
st.subheader("Show Details")
if show_results:
    st.dataframe(pd.DataFrame(show_results))
else:
    st.write("No shows available for the selected city.")

st.caption("Data updates every 30 minutes.")
