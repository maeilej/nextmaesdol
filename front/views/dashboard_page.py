import streamlit as st
import boto3

def display_dashboard_page():
    st.header("Dashboard")
    st.write("This is a dashboard page.")
    st.write("You can add more content here.")
    st.write("For example, you can add charts or tables.")
    st.write("You can also add buttons or other interactive elements.")
    st.write("Feel free to customize this page to suit your needs.")
    st.write("Good luck with your project!")

    dynamodb = boto3.client('dynamodb', region_name='us-west-2')
    response = dynamodb.list_tables()
    