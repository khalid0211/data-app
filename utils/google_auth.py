"""
Google OAuth Authentication Module
Uses streamlit-google-auth for Google Sign-In
"""

import streamlit as st
from streamlit_google_auth import Authenticate
import json
import os

def initialize_google_auth():
    """Initialize Google OAuth authenticator"""
    try:
        # Get credentials from Streamlit secrets
        client_id = st.secrets["google_oauth"]["client_id"]
        client_secret = st.secrets["google_oauth"]["client_secret"]
        redirect_uri = st.secrets["google_oauth"]["redirect_uri"]

        # Create temporary credentials JSON file
        # streamlit-google-auth requires a file path, not direct credentials
        credentials_dict = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
        }

        # Create .streamlit directory if it doesn't exist
        streamlit_dir = ".streamlit"
        if not os.path.exists(streamlit_dir):
            os.makedirs(streamlit_dir)

        # Write credentials to temporary file
        credentials_path = os.path.join(streamlit_dir, "google_credentials.json")
        with open(credentials_path, 'w') as f:
            json.dump(credentials_dict, f)

        # Create authenticator with the credentials file
        authenticator = Authenticate(
            secret_credentials_path=credentials_path,
            cookie_name='library_auth_cookie',
            cookie_key='library_auth_key_randomly_generated_12345',
            redirect_uri=redirect_uri,
        )

        return authenticator
    except KeyError as e:
        st.error(f"""
        ⚠️ **Google OAuth Configuration Missing!**

        Please configure Google OAuth credentials in `.streamlit/secrets.toml`:

        Missing key: {str(e)}

        See `.streamlit/secrets.toml` for instructions.
        """)
        return None
    except Exception as e:
        st.error(f"❌ Error initializing Google Auth: {str(e)}")
        return None

def check_google_authentication(db, authenticator):
    """
    Check Google authentication and return user info

    Returns:
        tuple: (authenticated, user_email, user_name)
    """
    try:
        # Check if user is authenticated
        authenticator.check_authentification()

        # Get auth status
        if st.session_state['connected']:
            user_info = st.session_state['user_info']

            email = user_info.get('email', '')
            name = user_info.get('name', email)

            return True, email, name
        else:
            return False, None, None

    except Exception as e:
        st.error(f"❌ Authentication error: {str(e)}")
        return False, None, None

def show_google_login_button(authenticator):
    """Display Google Sign-In button"""
    st.markdown("<h1 style='text-align: center;'>📚 Library Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🔐 Sign in with Google</h3>", unsafe_allow_html=True)

    st.markdown("---")

    st.info("""
    **🔒 Secure Google Authentication**

    This system uses Google OAuth for secure authentication.

    **To access the library:**
    1. Click "Login with Google" below
    2. Sign in with your Google account
    3. Admin (khalid0211@gmail.com) gets full access automatically
    4. Other users need approval from admin
    """)

    # Center the login button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        authenticator.login()

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>🔒 Secure authentication powered by Google</p>
    <p>For access approval, contact: <strong>Dr. Khalid Ahmad Khan</strong><br>
    📧 khalid0211@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)

def show_google_logout_button(authenticator):
    """Display logout button"""
    authenticator.logout()
