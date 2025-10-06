import streamlit as st
import json
import pyrebase
from datetime import datetime

# Admin email - hardcoded for security
ADMIN_EMAIL = "khalid0211@gmail.com"

def load_firebase_config():
    """Load Firebase web configuration"""
    try:
        with open('config/firebase_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("⚠️ Firebase configuration file not found. Please create config/firebase_config.json")
        return None
    except json.JSONDecodeError:
        st.error("⚠️ Invalid Firebase configuration file")
        return None

def initialize_firebase_auth():
    """Initialize Firebase for authentication"""
    config = load_firebase_config()
    if not config:
        return None

    try:
        firebase = pyrebase.initialize_app(config)
        return firebase
    except Exception as e:
        st.error(f"⚠️ Error initializing Firebase: {str(e)}")
        return None

def google_sign_in():
    """Handle Google Sign-In"""
    firebase = initialize_firebase_auth()
    if not firebase:
        return None

    auth = firebase.auth()

    # Note: Pyrebase doesn't directly support Google Sign-In popup
    # This is a placeholder - you'll need to implement this using Firebase JS SDK
    # or use streamlit-google-auth library

    st.warning("⚠️ Google Sign-In requires additional setup with Firebase JS SDK")
    st.info("Please follow the authentication guide for complete implementation")

    return None

def is_admin(email):
    """Check if user is admin"""
    return email.lower() == ADMIN_EMAIL.lower()

def get_user_access_level(db, email):
    """Get user's access level from Firestore

    Access levels:
    - admin: Full access + User Management + Book Lending
    - manage: Add, edit, delete books, bookshelves, owners
    - view: Read-only access
    - none: No access
    """
    try:
        # Admin always has admin access
        if is_admin(email):
            return "admin"

        # Query users collection
        users = db.collection('users').where('email', '==', email).stream()
        for user in users:
            user_data = user.to_dict()
            return user_data.get('access_level', 'none')

        # User not found - return none
        return 'none'
    except Exception as e:
        print(f"Error getting user access level: {e}")
        return 'none'

def create_or_update_user(db, email, display_name=None):
    """Create or update user in Firestore"""
    try:
        # Check if user exists
        users = db.collection('users').where('email', '==', email).stream()
        existing_user = None
        user_id = None

        for user in users:
            existing_user = user.to_dict()
            user_id = user.id
            break

        current_time = datetime.now().isoformat()

        if existing_user:
            # Update last login
            db.collection('users').document(user_id).update({
                'last_login': current_time
            })
            return existing_user
        else:
            # Create new user
            new_user_data = {
                'email': email,
                'gmail_id': email,
                'display_name': display_name or email,
                'access_level': 'admin' if is_admin(email) else 'none',
                'profile_created': False,
                'full_name': '',
                'cell_phone': '',
                'created_at': current_time,
                'last_login': current_time,
                'approved_by': None,
                'approved_at': None
            }

            db.collection('users').add(new_user_data)
            return new_user_data
    except Exception as e:
        print(f"Error creating/updating user: {e}")
        return None

def check_access(access_level, required_level):
    """
    Check if user has required access level

    Access hierarchy:
    - admin: Full access + User Management + Book Lending
    - manage: Can add, edit, delete books, bookshelves, owners
    - view: Can only view
    - none: No access
    """
    # Admin has access to everything
    if access_level == 'admin':
        return True

    # Manage has access to manage and view operations
    if access_level == 'manage' and required_level in ['manage', 'view']:
        return True

    # View only has access to view operations
    if access_level == 'view' and required_level == 'view':
        return True

    return False

def require_auth(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        if 'user' not in st.session_state or not st.session_state.user:
            st.warning("⚠️ Please sign in to access this feature")
            return None
        return func(*args, **kwargs)
    return wrapper

def require_access(required_level='view'):
    """Decorator to require specific access level"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'user' not in st.session_state or not st.session_state.user:
                st.warning("⚠️ Please sign in to access this feature")
                return None

            user_level = st.session_state.get('access_level', 'none')

            if not check_access(user_level, required_level):
                st.error("🚫 You don't have permission to access this feature")
                if user_level == 'none':
                    st.info("📧 Please contact Dr. Khalid Ahmad Khan (khalid0211@gmail.com) to request access")
                return None

            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_profile(db, email):
    """Get user's profile information"""
    try:
        users = db.collection('users').where('email', '==', email).stream()
        for user in users:
            return {**user.to_dict(), 'id': user.id}
        return None
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None

def update_user_profile(db, user_id, full_name, cell_phone):
    """Update user's profile"""
    try:
        db.collection('users').document(user_id).update({
            'full_name': full_name,
            'cell_phone': cell_phone,
            'profile_created': True
        })
        return True
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False
