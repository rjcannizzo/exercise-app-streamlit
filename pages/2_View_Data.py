import os
import streamlit as st
import pandas as pd
import pymongo
import dotenv

@st.cache
def get_data(search={}, projection={'_id':0}):
    """Defaults: get all records but don't return _id column"""    
    client = st.session_state['mongo_client']
    db = client.exercise
    exercise = db.exercise
    return list(exercise.find(search, projection)) 

def convert_date(df, col_name):
    """Convert dataframe[col_name] to a date string"""
    df[col_name] = df[col_name].dt.strftime('%Y-%m-%d')
    

st.header('Data Entry')

df = pd.DataFrame(get_data())
convert_date(df, 'date')
df