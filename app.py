import streamlit as st
import pandas as pd

# Title of the app
st.title("CSV File Viewer")

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file into a DataFrame
    df = pd.read_csv(uploaded_file)
    
    # Display the DataFrame as a table
    st.write("### CSV File Contents")
    st.dataframe(df)
    
    # Optionally, display some basic statistics
    st.write("### Basic Statistics")
    st.write(df.describe())
else:
    st.write("Please upload a CSV file to get started.")
