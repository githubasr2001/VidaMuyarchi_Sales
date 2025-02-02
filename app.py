import streamlit as st
import pandas as pd

# Title of the app
st.title("Theatre Shows Data Viewer")

# Raw URL of the CSV file hosted on GitHub
csv_url = "https://raw.githubusercontent.com/githubasr2001/VidaMuyarchi_Sales/main/theatre_shows_2025-02-03.csv"

# Load the CSV file into a DataFrame
@st.cache_data  # Cache the data to improve performance
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data(csv_url)

# Display the DataFrame as a table
st.write("### Theatre Shows Data")
st.dataframe(df)

# Optionally, display some basic statistics
st.write("### Basic Statistics")
st.write(df.describe())
