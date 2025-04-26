import streamlit as st
import requests
import json
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from auth_frontend import show_auth_page

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
st.session_state.api_base_url = API_BASE_URL

def get_connection_strings() -> List[Dict[str, Any]]:
    try:
        response = requests.get(
            f"{API_BASE_URL}/connection-strings/",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to get connection strings: {str(e)}")
        return []

def save_connection_string(database_type: str, name: str, connection_string: str) -> bool:
    try:
        response = requests.post(
            f"{API_BASE_URL}/connection-strings/",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            json={"database_type": database_type, "name": name, "connection_string": connection_string}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to save connection string: {str(e)}")
        return False

def connect_to_database(db_type: str, connection_string: str) -> bool:
    try:
        response = requests.post(
            f"{API_BASE_URL}/connect",
            json={"db_type": db_type, "connection_string": connection_string}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to connect: {str(e)}")
        return False

def disconnect_from_database() -> bool:
    try:
        response = requests.post(f"{API_BASE_URL}/disconnect")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to disconnect: {str(e)}")
        return False

def get_schema() -> List[Dict[str, Any]]:
    try:
        response = requests.get(f"{API_BASE_URL}/schema")
        response.raise_for_status()
        return response.json()["schema"]
    except Exception as e:
        st.error(f"Failed to get schema: {str(e)}")
        return []

def execute_query(natural_language: str) -> Dict[str, Any]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"natural_language": natural_language}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to execute query: {str(e)}")
        return {}

def main():
    st.title("DB Chat")
    
    if "token" not in st.session_state:
        st.session_state.token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    
    if not st.session_state.token:
        show_auth_page()
        return
    
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.username = None
        st.rerun()
    
    with st.sidebar:
        st.header("Database Connection")
        
        connection_strings = get_connection_strings()
        if connection_strings:
            st.subheader("Saved Connections")
            for conn in connection_strings:
                if st.button(f"Connect to {conn['name']}"):
                    if connect_to_database(conn['database_type'], conn["connection_string"]):
                        st.success("Connected successfully!")
        
        st.subheader("New Connection")
        db_type = st.selectbox(
            "Database Type",
            ["mysql", "sqlserver", "postgres", "oracle"]
        )
        connection_name = st.text_input("Connection Name")
        connection_string = st.text_input(
            "Connection String",
            type="password",
            help="Format: username:password@host:port/database"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect"):
                if connect_to_database(db_type, connection_string):
                    st.success("Connected successfully!")
        with col2:
            if st.button("Save Connection"):
                if connection_name and connection_string:
                    if save_connection_string(db_type, connection_name, connection_string):
                        st.success("Connection saved successfully!")
                        st.rerun()
        
        if st.button("Disconnect"):
            if disconnect_from_database():
                st.success("Disconnected successfully!")
    
    if st.button("Get Schema"):
        schema = get_schema()
        if schema:
            st.json(schema)
    
    natural_language = st.text_area(
        "Enter your question in natural language",
        placeholder="e.g., Show me all customers from New York who made purchases in the last month"
    )
    
    if st.button("Execute Query"):
        if natural_language:
            result = execute_query(natural_language)
            if result:
                st.subheader("Generated SQL Query")
                st.code(result["sql_query"], language="sql")
                
                st.subheader("Results")
                st.dataframe(result["results"])
        else:
            st.warning("Please enter a question first")

if __name__ == "__main__":
    main() 