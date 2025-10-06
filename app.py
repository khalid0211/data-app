import streamlit as st
from utils.firebase_utils import add_book, edit_book, delete_book, get_books

def main():
    st.title("Simple Library System")

    menu = ["Add Book", "Edit Book", "Delete Book", "View Books"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Add Book":
        st.subheader("Add a New Book")
        title = st.text_input("Title")
        authors = st.text_input("Author(s)")
        publisher = st.text_input("Publisher")
        edition = st.text_input("Edition")
        publish_date = st.date_input("Publish Date")

        if st.button("Add Book"):
            add_book(title, authors, publisher, edition, publish_date)
            st.success("Book added successfully!")

    elif choice == "Edit Book":
        st.subheader("Edit an Existing Book")
        books = get_books()
        book_titles = [book['title'] for book in books]
        selected_book = st.selectbox("Select a book to edit", book_titles)

        if selected_book:
            book = next(book for book in books if book['title'] == selected_book)
            new_title = st.text_input("Title", book['title'])
            new_authors = st.text_input("Author(s)", book['authors'])
            new_publisher = st.text_input("Publisher", book['publisher'])
            new_edition = st.text_input("Edition", book['edition'])
            new_publish_date = st.date_input("Publish Date", book['publish_date'])

            if st.button("Update Book"):
                edit_book(book['id'], new_title, new_authors, new_publisher, new_edition, new_publish_date)
                st.success("Book updated successfully!")

    elif choice == "Delete Book":
        st.subheader("Delete a Book")
        books = get_books()
        book_titles = [book['title'] for book in books]
        selected_book = st.selectbox("Select a book to delete", book_titles)

        if st.button("Delete Book"):
            book = next(book for book in books if book['title'] == selected_book)
            delete_book(book['id'])
            st.success("Book deleted successfully!")

    elif choice == "View Books":
        st.subheader("List of Books")
        books = get_books()
        for book in books:
            st.write(f"**Title:** {book['title']}, **Author(s):** {book['authors']}, **Publisher:** {book['publisher']}, **Edition:** {book['edition']}, **Publish Date:** {book['publish_date']}")

if __name__ == "__main__":
    main()