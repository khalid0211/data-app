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

def add_book(title, authors, publisher, edition, publish_date_str):
    """Adds a new book to Firestore. Expects publish_date_str as a string."""
    try:
        db.collection('books').add({
            'title': title,
            'authors': authors,
            'publisher': publisher,
            'edition': edition,
            'publish_date': publish_date_str
        })
        return True
    except Exception as e:
        print(f"Error adding book: {e}")
        return False

def get_books():
    """Retrieves all books from Firestore."""
    try:
        books_stream = db.collection('books').stream()
        return [{**book.to_dict(), 'id': book.id} for book in books_stream]
    except Exception as e:
        print(f"Error getting books: {e}")
        return []

def edit_book(book_id, title, authors, publisher, edition, publish_date_str):
    """Updates an existing book. Expects publish_date_str as a string."""
    try:
        db.collection('books').document(book_id).update({
            'title': title,
            'authors': authors,
            'publisher': publisher,
            'edition': edition,
            'publish_date': publish_date_str
        })
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