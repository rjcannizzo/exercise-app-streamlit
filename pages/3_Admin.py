import streamlit as st

st.title('Admin Page')
message_area = st.empty()

def add_exercise_name_to_db(exercise_name):
    try:
        client = st.session_state['mongo_client']
        collection = client.exercise.types
        collection.insert_one(dict(name=exercise_name.strip()))
        message_area.success(f"Added {exercise_name} to database...")
    except Exception as e:
        message_area.error(e)
    
with st.form("add_type_form"):
    exercise_name = st.text_input('Enter a new exercise name:')
    submitted = st.form_submit_button('Add')
    if submitted:
        add_exercise_name_to_db(exercise_name)