import os
import streamlit as st
import pandas as pd
import pymongo
import dotenv

dotenv.load_dotenv('.env')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
URI = f"mongodb+srv://rc:{MONGO_PASSWORD}@apps.sdrf5qb.mongodb.net/exercise"

st.header('Home')

@st.experimental_singleton
def get_mongo_client():
    client = pymongo.MongoClient(URI)
    return client

if 'mongo_client' not in st.session_state:
    st.session_state['mongo_client'] = get_mongo_client()

