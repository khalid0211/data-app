"""
Simplified Authentication Module
This is a temporary solution until full Firebase Auth with Google Sign-In is implemented.
For production, replace this with proper Firebase Authentication.
"""

import streamlit as st
from utils.firebase_utils import get_all_users
from utils.auth_utils import ADMIN_EMAIL, is_admin, get_user_access_level, create_or_update_user

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

def show_login_page(db):
    """Display login page"""
    st.markdown("<h1 style='text-align: center;'>📚 Library Management System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>🔐 Authentication Required</h3>", unsafe_allow_html=True)

    st.markdown("---")

    st.info("""
    **📝 Temporary Sign-In**

    This is a simplified authentication for development/testing.
    For production, this will be replaced with Google Sign-In.

    **Instructions:**
    1. Enter your Gmail address
    2. Click "Sign In"
    3. Admin (khalid0211@gmail.com) gets full access automatically
    4. Other users need approval from admin
    """)

    with st.form("login_form"):
        email = st.text_input("Gmail Address", placeholder="your.email@gmail.com")
        name = st.text_input("Display Name", placeholder="Your Name")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit = st.form_submit_button("🔐 Sign In", use_container_width=True)

        if submit:
            if not email or '@' not in email:
                st.error("❌ Please enter a valid email address")
            elif not name:
                st.error("❌ Please enter your name")
            else:
                # Create or update user
                user_data = create_or_update_user(db, email.lower().strip(), name.strip())

                if user_data:
                    # Set session state
                    st.session_state.authenticated = True
                    st.session_state.user_email = email.lower().strip()
                    st.session_state.user_name = name.strip()
                    st.session_state.access_level = user_data.get('access_level', 'none')

                    st.success(f"✅ Welcome, {name}!")
                    st.rerun()
                else:
                    st.error("❌ Login failed. Please try again.")

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p>🔒 Secure authentication powered by Firebase</p>
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
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.access_level = 'none'
    st.rerun()

def check_authentication(db):
    """Check if user is authenticated and has access"""
    init_session_state()

    if not st.session_state.authenticated:
        show_login_page(db)
        return False

    # Refresh access level
    access_level = get_user_access_level(db, st.session_state.user_email)
    st.session_state.access_level = access_level

    if access_level == 'none':
        show_no_access_page()
        return False

    return True

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

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
