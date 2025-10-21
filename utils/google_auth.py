"""
Google OAuth Authentication Module
Uses streamlit-google-auth for Google Sign-In
"""
from google_auth_oauthlib.flow import Flow

import streamlit as st
from streamlit_google_auth import Authenticate
import json
import os
import tempfile

def initialize_google_auth():
    """Initialize Google OAuth authenticator"""
    # This function will now only be used to check for secrets
    # and return the authenticator for session management.
    # The login button logic is handled separately.
    if "google_oauth" not in st.secrets:
        st.error("Google OAuth secrets not found!")
        return None
    try:
        # Get credentials from Streamlit secrets
        client_id = st.secrets["google_oauth"]["client_id"]
        client_secret = st.secrets["google_oauth"]["client_secret"]
        redirect_uri = st.secrets["google_oauth"]["redirect_uri"]

        # The streamlit-google-auth library requires a file path.
        # We create a temporary JSON file to hold the credentials.
        credentials_dict = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uris": [redirect_uri],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        }

        # Write credentials to a temporary file (cross-platform)
        temp_dir = tempfile.gettempdir()
        credentials_path = os.path.join(temp_dir, "google_credentials.json")
        with open(credentials_path, "w") as f:
            json.dump(credentials_dict, f)

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
    try:
        st.markdown("<h1 style='text-align: center;'>📚 Library Management System</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>🔐 Sign in with Google</h3>", unsafe_allow_html=True)

        st.markdown("---")

        st.info("""
        **🔒 Secure Google Authentication**

        This system uses Google OAuth for secure authentication.

        **To access the library:**
        1. Click "Login with Google" below
        2. Sign in with your Google account
        """)

        # Manually construct the authorization URL to force a full-page redirect
        client_config = {
            "web": {
                "client_id": st.secrets["google_oauth"]["client_id"],
                "client_secret": st.secrets["google_oauth"]["client_secret"],
                "redirect_uris": [st.secrets["google_oauth"]["redirect_uri"]],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid'],
            redirect_uri=st.secrets["google_oauth"]["redirect_uri"]
        )
        authorization_url, _ = flow.authorization_url(prompt='consent')

        # Center the login button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.link_button("Login with Google", authorization_url, use_container_width=True, type="primary")

        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>🔒 Secure authentication powered by Google</p>
        <p>For access approval, contact: <strong>Dr. Khalid Ahmad Khan</strong><br>
        📧 khalid0211@gmail.com</p>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error creating login button: {e}")

def show_google_logout_button(authenticator):
    """Display logout button"""
    authenticator.logout()
