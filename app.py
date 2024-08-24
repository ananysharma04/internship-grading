import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime

def convert_stipend(stipend):
    if pd.isna(stipend) or stipend.strip().lower() in ['nil', 'na', 'nill']:
        return np.nan
    stipend = stipend.replace(',', '').replace('Rs.', '').replace('Rs ', '').strip()
    try:
        return float(stipend)
    except ValueError:
        return np.nan

def calculate_duration_weeks(start_date, end_date):
    if pd.isna(start_date) or pd.isna(end_date):
        return np.nan
    try:
        start = datetime.strptime(start_date, '%m/%d/%Y')
        end = datetime.strptime(end_date, '%m/%d/%Y')
        return (end - start).days // 7
    except ValueError:
        return np.nan

def process_data(df):
    df['Grade'] = np.nan
    df['Total stipend amount in Rs.'] = df['Total stipend amount in Rs.'].apply(convert_stipend)
    highest_stipend = df['Total stipend amount in Rs.'].max()
    
    df.loc[df['Total stipend amount in Rs.'] == highest_stipend, 'Grade'] = 10
    df.loc[(df['Total stipend amount in Rs.'] > 0) & (df['Total stipend amount in Rs.'] != highest_stipend), 'Grade'] = 9
    
    df['Internship Duration Weeks'] = df['Duration of Internship'].str.extract(r'(\d+)').astype(float)
    
    df.loc[df['Total stipend amount in Rs.'].isna() & (df['Internship Duration Weeks'] >= 8), 'Grade'] = 8
    df.loc[df['Total stipend amount in Rs.'].isna() & (df['Internship Duration Weeks'] < 8), 'Grade'] = 7
    
    df['Course Duration Weeks'] = df.apply(lambda row: calculate_duration_weeks(row['Start date of course'], row['End date of course']), axis=1)
    
    max_course_duration = df['Course Duration Weeks'].max()
    df.loc[df['Total stipend amount in Rs.'].isna() & (df['Internship Duration Weeks'].isna()) &
           (df['Title of Course'].str.strip().str.lower() != 'na') &
           (df['Course Duration Weeks'] == max_course_duration), 'Grade'] = 7
    df.loc[df['Total stipend amount in Rs.'].isna() & (df['Internship Duration Weeks'].isna()) &
           (df['Title of Course'].str.strip().str.lower() != 'na'), 'Grade'] = 6
    
    df.loc[df['Total stipend amount in Rs.'].isna() & 
           (df['Internship Duration Weeks'].notna()) & 
           (df['Title of Course'].str.strip().str.lower() != 'na'), 'Grade'] = 8
    
    df.drop(columns=['Internship Duration Weeks', 'Course Duration Weeks'], inplace=True)
    return df

st.title("Internship and Course Grading Tool")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.write("### Preview of the uploaded file:")
    st.write(df.head())
    
    if st.button("Process Data"):
        processed_df = process_data(df)
        st.write("### Preview of the processed data:")
        st.write(processed_df.head())
        
        output_file = "graded_internships.csv"
        processed_df.to_csv(output_file, index=False)
        
        st.write("### Download the processed CSV file:")
        with open(output_file, "rb") as f:
            st.download_button("Download CSV", f, file_name=output_file)

