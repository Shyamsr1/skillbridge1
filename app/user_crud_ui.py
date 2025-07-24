import json
import streamlit as st
from app import user_profile_crud

st.title("User Profile CRUD Operations")

action = st.selectbox("Select Action", ["Create", "Read", "Update", "Delete"])

user_id = st.text_input("User ID")
name = st.text_input("Name")
email = st.text_input("Email")

if st.button("Submit"):
    if action == "Create":
        result = user_profile_crud.create_user(user_id, name, email)
    elif action == "Read":
        result = user_profile_crud.read_user(user_id)
    elif action == "Update":
        result = user_profile_crud.update_user(user_id, name, email)
    elif action == "Delete":
        result = user_profile_crud.delete_user(user_id)
    st.write(result)
