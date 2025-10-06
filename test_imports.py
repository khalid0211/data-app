"""Test script to verify all imports work"""

print("Testing imports from app.py...")

try:
    from utils.firebase_db import (add_book, edit_book, delete_book, get_books,
                                   add_bookshelf, edit_bookshelf, delete_bookshelf, get_bookshelves,
                                   add_owner, edit_owner, delete_owner, get_owners,
                                   generate_tracking_number, db,
                                   get_all_users, update_user_access,
                                   lend_book, return_book, get_active_loans, get_loan_history)
    print("✓ firebase_db imports: SUCCESS")
except Exception as e:
    print(f"✗ firebase_db imports: FAILED - {e}")
    exit(1)

try:
    from utils.book_api import search_book_by_title
    print("✓ book_api imports: SUCCESS")
except Exception as e:
    print(f"✗ book_api imports: FAILED - {e}")
    exit(1)

try:
    from utils.auth import check_authentication, show_user_info_sidebar, can_add_edit_delete, can_view
    print("✓ auth imports: SUCCESS")
except Exception as e:
    print(f"✗ auth imports: FAILED - {e}")
    exit(1)

try:
    from utils.auth_utils import is_admin, get_user_profile, update_user_profile
    print("✓ auth_utils imports: SUCCESS")
except Exception as e:
    print(f"✗ auth_utils imports: FAILED - {e}")
    exit(1)

print("\n✓✓✓ All imports successful! ✓✓✓")
