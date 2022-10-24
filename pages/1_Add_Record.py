import streamlit as st
import datetime

st.title("Add A Record")

message_area = st.empty()

def add_record(_date, exercise, reps, weight):
    """add a record to the database"""
    try:
        client = st.session_state['mongo_client']
        db = client.exercise.exercise
        _date = datetime.datetime(_date.year, _date.month, _date.day) 
        data = dict(date=_date, exercise=exercise.lower(), reps=reps, weight=weight)
        _id = db.insert_one(data)
    except Exception as e:
        st.error(e)

    if _id:
        with message_area:
            st.success("New record added")


def get_exercise_set():
    """return a set of unique exercise names"""    
    client = st.session_state['mongo_client']
    collection = client.exercise.types
    raw = collection.find({}, {'name': 1, '_id': 0})
    items = [item.get('name') for item in raw]
    items.sort()
    return items


exercise_set = get_exercise_set()

with st.form("data_entry_form"):
    date = st.date_input('Date')
    exercise = st.selectbox("Select Exercise", options = exercise_set)
    reps = st.number_input("Reps", min_value=1)
    weight = st.number_input("Weight", min_value=1)
    submitted = st.form_submit_button("Submit")
    if submitted:
        add_record(date, exercise, reps, weight)
