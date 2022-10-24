import streamlit as st
import datetime
import time

st.header("Data Entry")
message_area = st.empty()

def add_record(_date, exercise, reps, weight):
    # add a record to the database
    try:
        client = st.session_state['mongo_client']
        db = client.exercise.exercise
        _date = datetime.datetime(_date.year, _date.month, _date.day) 
        data = dict(date=_date, exercise=exercise, reps=reps, weight=weight)
        _id = db.insert_one(data)
    except Exception as e:
        st.error(e)

    if _id:
        with message_area:
            st.success("New record added")
        # time.sleep(3)
        # message_area.empty()

def convert_date_to_string(_date):
    return _date.strftime("%Y-%m-%d")


def get_exercise_set():
    """return a set of unique exercise names"""    
    client = st.session_state['mongo_client']
    exercise = client.exercise.exercise
    raw = exercise.find({}, {'exercise': 1, '_id': 0})
    return { item.get('exercise') for item in raw }

exercise_set = get_exercise_set()

with st.form("data_entry_form"):
    date = st.date_input('Date')
    exercise = st.selectbox("Select Exercise", options = exercise_set)
    reps = st.number_input("Reps", min_value=1)
    weight = st.number_input("Weight", min_value=1)

    submitted = st.form_submit_button("Submit")
    if submitted:
        add_record(date, exercise, reps, weight)
