import streamlit as st

def get_exercise_list():
    """return a list of unique exercise names"""    
    client = st.session_state['mongo_client']
    exercise = client.exercise.exercise
    raw = exercise.find({}, {'exercise': 1, '_id': 0})
    return { item.get('exercise') for item in raw }

ex_list = get_exercise_list()
ex_list