"""
Unified Authentication Module
Supports both Google OAuth and Temporary Authentication
"""

import streamlit as st
from utils.firebase_utils import db
from utils.auth_utils import create_or_update_user, get_user_access_level, is_admin

# Authentication mode configuration
# Set to 'google' for production or 'temporary' for testing
AUTH_MODE = 'google'  # Change to 'temporary' to use simple email/name login

def init_session_state():
    """Initialize authentication session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'access_level' not in st.session_state:
        st.session_state.access_level = 'none'
    if 'authenticator' not in st.session_state:
        st.session_state.authenticator = None

def check_authentication():
    """
    Main authentication check - uses configured AUTH_MODE

    Returns:
        bool: True if authenticated with access, False otherwise
    """
    init_session_state()

    if AUTH_MODE == 'google':
        return check_google_auth()
    elif AUTH_MODE == 'temporary':
        return check_temporary_auth()
    else:
        st.error(f"❌ Invalid AUTH_MODE: {AUTH_MODE}")
        return False

def check_google_auth():
    """Check Google OAuth authentication"""
    from utils.google_auth import initialize_google_auth, check_google_authentication, show_google_login_button

    # Initialize authenticator if not already done
    if st.session_state.authenticator is None:
        st.session_state.authenticator = initialize_google_auth()

        if st.session_state.authenticator is None:
            st.error("❌ Could not initialize Google OAuth")
            st.stop()

    authenticator = st.session_state.authenticator

    # Check if authenticated
    is_authenticated, email, name = check_google_authentication(db, authenticator)

    if not is_authenticated:
        # Show login page
        show_google_login_button(authenticator)
        return False

    # User is authenticated - create/update user in database
    if not st.session_state.authenticated or st.session_state.user_email != email:
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

def check_temporary_auth():
    """Check temporary authentication (email/name input)"""
    from utils.simple_auth import check_authentication as temp_auth
    return temp_auth(db)

def show_no_access_page():
    """Display no access page"""
    st.markdown("<h1 style='text-align: center;'>🚫 Access Denied</h1>", unsafe_allow_html=True)

    st.warning(f"""
    ### Hello, {st.session_state.user_name}!

    Your account has been created, but you don't have access to the library system yet.

    **📧 To request access:**
    Please contact **Dr. Khalid Ahmad Khan** at:
    - Email: khalid0211@gmail.com

    Once approved, you'll be able to access the system.
    """)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Access", use_container_width=True):
            st.rerun()

    if st.button("🚪 Logout"):
        logout()

def logout():
    """Logout user (works for both auth modes)"""
    if AUTH_MODE == 'google' and st.session_state.authenticator:
        from utils.google_auth import show_google_logout_button
        show_google_logout_button(st.session_state.authenticator)

    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.access_level = 'none'
    st.session_state.authenticator = None
    st.rerun()

def can_add_edit_delete():
    """Check if user can add, edit, or delete (Manage or Admin)"""
    return st.session_state.access_level in ['admin', 'manage']

def can_view():
    """Check if user can view"""
    return st.session_state.access_level in ['admin', 'manage', 'view']

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
    access_level = st.session_state.access_level
    st.sidebar.write(f"**Access:** {access_icons.get(access_level, access_level)}")

    # Show auth mode indicator
    if AUTH_MODE == 'temporary':
        st.sidebar.caption("⚠️ Using temporary auth")

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
