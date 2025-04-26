import streamlit as st
import requests
from typing import Optional

def login(username: str, password: str) -> Optional[str]:
    try:
        response = requests.post(
            f"{st.session_state.api_base_url}/token",
            json={"username": username, "password": password},
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("Invalid username or password. Please try again.")
        elif e.response.status_code == 422:
            error_detail = e.response.json().get("detail", [])
            if isinstance(error_detail, list):
                error_messages = [err.get("msg", "") for err in error_detail]
                st.error(f"Login failed: {'; '.join(error_messages)}")
            else:
                st.error(f"Login failed: {error_detail}")
        else:
            st.error(f"Login failed: {str(e)}")
        return None
    except Exception as e:
        st.error("Unable to connect to the server. Please try again later.")
        return None

def register(email: str, username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{st.session_state.api_base_url}/register",
            json={
                "email": email,
                "username": username,
                "password": password
            }
        )
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            error_detail = e.response.json().get("detail", [])
            if isinstance(error_detail, list):
                error_messages = [err.get("msg", "") for err in error_detail]
                st.error(f"Registration failed: {'; '.join(error_messages)}")
            else:
                st.error(f"Registration failed: {error_detail}")
        else:
            st.error(f"Registration failed: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
        return False

def show_login_form():
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            token = login(username, password)
            if token:
                st.session_state.token = token
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()

def show_register_form():
    with st.form("register_form"):
        st.subheader("Register")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if password != confirm_password:
                st.error("Passwords do not match!")
                return
            
            if register(email, username, password):
                st.success("Registration successful! Please login.")
                st.session_state.show_login = True
                st.rerun()

def show_auth_page():
    if "show_login" not in st.session_state:
        st.session_state.show_login = True
    
    if st.session_state.show_login:
        show_login_form()
        if st.button("Don't have an account? Register"):
            st.session_state.show_login = False
            st.rerun()
    else:
        show_register_form()
        if st.button("Already have an account? Login"):
            st.session_state.show_login = True
            st.rerun() 