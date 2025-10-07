"""
Streamlit Native Authentication Module
Uses st.login() for Google OAuth (Streamlit 1.42+)
"""

import streamlit as st
from utils.firebase_db import db
from utils.auth_utils import create_or_update_user, get_user_access_level, is_admin

def check_authentication():
    """
    Check authentication using Streamlit's native st.login()

    Returns:
        bool: True if authenticated with access, False otherwise
    """
    # Check if user is logged in using Streamlit's native authentication
    if not st.user.is_logged_in:
        show_login_page()
        return False

    # User is logged in - get their info
    email = st.user.email
    name = st.user.name

    # Create or update user in database
    user_data = create_or_update_user(db, email.lower().strip(), name.strip())

    if user_data:
        st.session_state.authenticated = True
        st.session_state.user_email = email.lower().strip()
        st.session_state.user_name = name.strip()
        st.session_state.access_level = user_data.get('access_level', 'none')
    else:
        st.error("❌ Failed to create user account")
        return False

    # Refresh access level (in case admin changed it)
    access_level = get_user_access_level(db, st.session_state.user_email)
    st.session_state.access_level = access_level

    # Check if user has access
    if access_level == 'none':
        show_no_access_page()
        return False

    return True

def show_login_page():
    """Display login page with Google authentication"""
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

    # Center the login button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.button("Login with Google", on_click=st.login, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>🔒 Secure authentication powered by Google</p>
    <p>For access approval, contact: <strong>Dr. Khalid Ahmad Khan</strong><br>
    📧 khalid0211@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)

def show_no_access_page():
    """Display no access page"""
    st.markdown("<h1 style='text-align: center;'>🚫 Access Denied</h1>", unsafe_allow_html=True)

    st.warning(f"""
    ### Hello, {st.session_state.user_name}!

    Your account has been created, but you don't have access to the library system yet.

    After you login, request for access by sending email to khalid0211@gmail.com

    Once approved, you'll be able to access the system.
    """)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Access", use_container_width=True):
            st.rerun()

    if st.button("🚪 Logout"):
        logout()

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.access_level = 'none'
    st.logout()

def can_add_edit_delete():
    """Check if user can add, edit, or delete (Manage or Admin)"""
    return st.session_state.get('access_level', 'none') in ['admin', 'manage']

def can_view():
    """Check if user can view"""
    return st.session_state.get('access_level', 'none') in ['admin', 'manage', 'view']

def show_user_info_sidebar():
    """Show user info in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 User Info")
    st.sidebar.write(f"**Name:** {st.session_state.user_name}")
    st.sidebar.write(f"**Email:** {st.session_state.user_email}")

    # Show access level with icon
    access_icons = {
        'admin': '🔒 Admin',
        'manage': '✏️ Manage',
        'view': '👁️ View Only',
        'none': '🚫 No Access'
    }
    access_level = st.session_state.get('access_level', 'none')
    st.sidebar.write(f"**Access:** {access_icons.get(access_level, access_level)}")

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
