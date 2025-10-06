import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st
from datetime import datetime

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK, checking to prevent re-initialization.
    """
    if not firebase_admin._apps:
        # The path to your service account key file
        key_path = "D:\\Dropbox\\MySoftware\\Portfolio\\mylibrary-firebase.json"

        if not os.path.exists(key_path):
            # This will show a clear error in Streamlit if the key is not found
            raise FileNotFoundError(f"Firebase service account key not found at {key_path}.")

        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    
    return firestore.client()

# Initialize Firestore client
db = initialize_firebase()

def add_book(title, authors, publisher, edition, publish_date_str, page_count='',
             isbn='', preview_url='', bookshelf_id='', tracking_number='', owner_id=''):
    """Adds a new book to Firestore. Expects publish_date_str as a string."""
    try:
        # Generate tracking number if not provided
        if not tracking_number:
            tracking_number = generate_tracking_number()

        db.collection('books').add({
            'title': title,
            'authors': authors,
            'publisher': publisher,
            'edition': edition,
            'publish_date': publish_date_str,
            'page_count': page_count,
            'isbn': isbn,
            'preview_url': preview_url,
            'bookshelf_id': bookshelf_id,
            'tracking_number': tracking_number,
            'owner_id': owner_id,
            'is_lent': False,
            'lent_to': '',
            'lent_date': '',
            'lent_by': ''
        })
        return True, tracking_number
    except Exception as e:
        print(f"Error adding book: {e}")
        return False, None

def get_books():
    """Retrieves all books from Firestore."""
    try:
        books_stream = db.collection('books').stream()
        return [{**book.to_dict(), 'id': book.id} for book in books_stream]
    except Exception as e:
        print(f"Error getting books: {e}")
        return []

def edit_book(book_id, title, authors, publisher, edition, publish_date_str, page_count='',
              isbn='', preview_url='', bookshelf_id='', tracking_number='', owner_id=''):
    """Updates an existing book. Expects publish_date_str as a string."""
    try:
        update_data = {
            'title': title,
            'authors': authors,
            'publisher': publisher,
            'edition': edition,
            'publish_date': publish_date_str,
            'page_count': page_count,
            'isbn': isbn,
            'preview_url': preview_url,
            'bookshelf_id': bookshelf_id,
            'owner_id': owner_id
        }

        # Only update tracking number if provided
        if tracking_number:
            update_data['tracking_number'] = tracking_number

        db.collection('books').document(book_id).update(update_data)
        return True
    except Exception as e:
        print(f"Error updating book: {e}")
        return False

def delete_book(book_id):
    """Deletes a book from Firestore by its ID."""
    try:
        db.collection('books').document(book_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting book: {e}")
        return False

# Bookshelf Management Functions
def add_bookshelf(title, description=''):
    """Adds a new bookshelf to Firestore."""
    try:
        # Get current max ID to generate next ID
        shelves = db.collection('bookshelves').stream()
        max_id = 0
        for shelf in shelves:
            shelf_data = shelf.to_dict()
            if shelf_data.get('shelf_id', 0) > max_id:
                max_id = shelf_data['shelf_id']

        new_id = max_id + 1

        db.collection('bookshelves').add({
            'shelf_id': new_id,
            'title': title,
            'description': description
        })
        return True, new_id
    except Exception as e:
        print(f"Error adding bookshelf: {e}")
        return False, None

def get_bookshelves():
    """Retrieves all bookshelves from Firestore."""
    try:
        shelves_stream = db.collection('bookshelves').stream()
        return [{**shelf.to_dict(), 'id': shelf.id} for shelf in shelves_stream]
    except Exception as e:
        print(f"Error getting bookshelves: {e}")
        return []

def edit_bookshelf(doc_id, title, description=''):
    """Updates an existing bookshelf."""
    try:
        db.collection('bookshelves').document(doc_id).update({
            'title': title,
            'description': description
        })
        return True
    except Exception as e:
        print(f"Error updating bookshelf: {e}")
        return False

def delete_bookshelf(doc_id):
    """Deletes a bookshelf from Firestore by its document ID."""
    try:
        db.collection('bookshelves').document(doc_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting bookshelf: {e}")
        return False

def generate_tracking_number():
    """Generates a unique tracking number for a book (format: BK-YYYYMMDD-NNNN)."""
    from datetime import datetime

    try:
        # Get current date
        date_str = datetime.now().strftime("%Y%m%d")

        # Get all books with tracking numbers from today
        books = db.collection('books').where('tracking_number', '>=', f'BK-{date_str}-0000').stream()

        max_seq = 0
        for book in books:
            book_data = book.to_dict()
            tracking = book_data.get('tracking_number', '')
            if tracking.startswith(f'BK-{date_str}-'):
                try:
                    seq = int(tracking.split('-')[-1])
                    if seq > max_seq:
                        max_seq = seq
                except:
                    pass

        new_seq = max_seq + 1
        return f'BK-{date_str}-{new_seq:04d}'
    except Exception as e:
        print(f"Error generating tracking number: {e}")
        # Fallback to timestamp-based tracking number
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f'BK-{timestamp}'

# Owner Management Functions
def add_owner(owner_id, name, email='', cell_phone=''):
    """Adds a new owner to Firestore. Owner ID must be 3 digits."""
    try:
        # Validate owner_id is 3 digits
        if not owner_id or len(str(owner_id)) != 3 or not str(owner_id).isdigit():
            return False, "Owner ID must be exactly 3 digits"

        # Check if owner_id already exists
        existing = db.collection('owners').where('owner_id', '==', owner_id).stream()
        if any(existing):
            return False, f"Owner ID {owner_id} already exists"

        db.collection('owners').add({
            'owner_id': owner_id,
            'name': name,
            'email': email,
            'cell_phone': cell_phone
        })
        return True, "Success"
    except Exception as e:
        print(f"Error adding owner: {e}")
        return False, str(e)

def get_owners():
    """Retrieves all owners from Firestore."""
    try:
        owners_stream = db.collection('owners').stream()
        return [{**owner.to_dict(), 'id': owner.id} for owner in owners_stream]
    except Exception as e:
        print(f"Error getting owners: {e}")
        return []

def edit_owner(doc_id, name, email='', cell_phone=''):
    """Updates an existing owner. Cannot change owner_id."""
    try:
        db.collection('owners').document(doc_id).update({
            'name': name,
            'email': email,
            'cell_phone': cell_phone
        })
        return True
    except Exception as e:
        print(f"Error updating owner: {e}")
        return False

def delete_owner(doc_id):
    """Deletes an owner from Firestore by its document ID."""
    try:
        db.collection('owners').document(doc_id).delete()
        return True
    except Exception as e:
        print(f"Error deleting owner: {e}")
        return False

# User Management Functions
def get_all_users():
    """Retrieves all users from Firestore"""
    try:
        users_stream = db.collection('users').stream()
        return [{**user.to_dict(), 'id': user.id} for user in users_stream]
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def update_user_access(user_id, access_level, approved_by):
    """Update user's access level"""
    from datetime import datetime
    try:
        db.collection('users').document(user_id).update({
            'access_level': access_level,
            'approved_by': approved_by,
            'approved_at': datetime.now().isoformat()
        })
        return True
    except Exception as e:
        print(f"Error updating user access: {e}")
        return False

# Book Lending Functions
def lend_book(book_id, borrower_email, borrower_name, lender_email, due_date):
    """Lend a book to a user"""
    from datetime import datetime
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Get book details
        book = db.collection('books').document(book_id).get()
        if not book.exists:
            return False, "Book not found"

        book_data = book.to_dict()

        # Check if already lent
        if book_data.get('is_lent', False):
            return False, "Book is already lent out"

        # Update book status
        db.collection('books').document(book_id).update({
            'is_lent': True,
            'lent_to': borrower_email,
            'lent_date': current_date,
            'lent_by': lender_email
        })

        # Create loan record
        db.collection('book_loans').add({
            'book_id': book_id,
            'tracking_number': book_data.get('tracking_number', ''),
            'book_title': book_data.get('title', ''),
            'borrowed_by_email': borrower_email,
            'borrowed_by_name': borrower_name,
            'borrowed_date': current_date,
            'due_date': due_date,
            'returned': False,
            'returned_date': None,
            'approved_by': lender_email
        })

        return True, "Book lent successfully"
    except Exception as e:
        print(f"Error lending book: {e}")
        return False, str(e)

def return_book(book_id):
    """Mark a book as returned"""
    from datetime import datetime
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Update book status
        db.collection('books').document(book_id).update({
            'is_lent': False,
            'lent_to': '',
            'lent_date': '',
            'lent_by': ''
        })

        # Update loan record
        loans = db.collection('book_loans').where('book_id', '==', book_id).where('returned', '==', False).stream()
        for loan in loans:
            db.collection('book_loans').document(loan.id).update({
                'returned': True,
                'returned_date': current_date
            })

        return True, "Book returned successfully"
    except Exception as e:
        print(f"Error returning book: {e}")
        return False, str(e)

def get_active_loans():
    """Get all active book loans"""
    try:
        loans_stream = db.collection('book_loans').where('returned', '==', False).stream()
        return [{**loan.to_dict(), 'id': loan.id} for loan in loans_stream]
    except Exception as e:
        print(f"Error getting active loans: {e}")
        return []

def get_loan_history(email=None):
    """Get loan history, optionally filtered by user email"""
    try:
        if email:
            loans_stream = db.collection('book_loans').where('borrowed_by_email', '==', email).stream()
        else:
            loans_stream = db.collection('book_loans').stream()

        return [{**loan.to_dict(), 'id': loan.id} for loan in loans_stream]
    except Exception as e:
        print(f"Error getting loan history: {e}")
        return []

st.set_page_config(layout="wide")

def main():
    st.title("📚 Simple Library System")

    # --- MENU ---
    menu = ["Add Book", "View All Books", "Edit/Delete Book"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Book":
        st.subheader("Add a New Book")

        with st.form(key="add_book_form", clear_on_submit=True):
            title = st.text_input("Title")
            authors = st.text_input("Author(s) (comma-separated)")
            publisher = st.text_input("Publisher")
            edition = st.text_input("Edition")
            publish_date = st.date_input("Publish Date", value=datetime.now())
            
            submit_button = st.form_submit_button(label="Add Book")

            if submit_button:
                if title and authors:
                    authors_list = [author.strip() for author in authors.split(',')]
                    # Convert date to a string format for Firestore
                    publish_date_str = publish_date.strftime("%Y-%m-%d")
                    
                    try:
                        add_book(title, authors_list, publisher, edition, publish_date_str)
                        st.success("Book added successfully!")
                    except Exception as e:
                        st.error(f"Failed to add book: {e}")
                else:
                    st.warning("Title and Author(s) are required.")

    elif choice == "View All Books":
        st.subheader("All Books in the Library")
        books = get_books()

        if books:
            for book in books:
                authors_str = ", ".join(book.get('authors', ['N/A']))
                with st.expander(f"{book.get('title', 'No Title')} by {authors_str}"):
                    st.write(f"**Publisher:** {book.get('publisher', 'N/A')}")
                    st.write(f"**Edition:** {book.get('edition', 'N/A')}")
                    st.write(f"**Publish Date:** {book.get('publish_date', 'N/A')}")
                    st.write(f"**Document ID:** {book.get('id', 'N/A')}")
        else:
            st.info("No books found in the library.")

    elif choice == "Edit/Delete Book":
        st.subheader("Edit or Delete a Book")
        books = get_books()
        
        if books:
            book_titles = [f"{book.get('title')} ({book.get('id')})" for book in books]
            selected_book_title = st.selectbox("Select a book to edit or delete", book_titles)

            selected_book = None
            if selected_book_title:
                selected_id = selected_book_title.split('(')[-1][:-1]
                for book in books:
                    if book['id'] == selected_id:
                        selected_book = book
                        break
            
            if selected_book:
                st.write("---")
                
                with st.form(key="edit_form"):
                    new_title = st.text_input("Title", value=selected_book.get('title', ''))
                    new_authors = st.text_input("Author(s) (comma-separated)", value=", ".join(selected_book.get('authors', [])))
                    new_publisher = st.text_input("Publisher", value=selected_book.get('publisher', ''))
                    new_edition = st.text_input("Edition", value=selected_book.get('edition', ''))
                    
                    # Convert date string from Firestore back to a date object for the widget
                    current_date_str = selected_book.get('publish_date')
                    if current_date_str:
                        current_date = datetime.strptime(current_date_str, "%Y-%m-%d").date()
                    else:
                        current_date = datetime.now().date()
                    new_publish_date = st.date_input("Publish Date", value=current_date)

                    col1, col2 = st.columns([1, 5])
                    with col1:
                        update_button = st.form_submit_button("Update")
                    with col2:
                        delete_button = st.form_submit_button("Delete")

                if update_button:
                    authors_list = [author.strip() for author in new_authors.split(',')]
                    # Convert date back to string for Firestore
                    new_publish_date_str = new_publish_date.strftime("%Y-%m-%d")
                    try:
                        edit_book(selected_book['id'], new_title, authors_list, new_publisher, new_edition, new_publish_date_str)
                        st.success("Book updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update book: {e}")

                if delete_button:
                    try:
                        delete_book(selected_book['id'])
                        st.success("Book deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete book: {e}")
        else:
            st.info("No books available to edit or delete.")

if __name__ == "__main__":
    main()