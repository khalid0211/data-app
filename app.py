import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.firebase_db import (add_book, edit_book, delete_book, get_books,
                               add_bookshelf, edit_bookshelf, delete_bookshelf, get_bookshelves,
                               add_owner, edit_owner, delete_owner, get_owners,
                               generate_tracking_number, db,
                               get_all_users, update_user_access, delete_user,
                               lend_book, return_book, get_active_loans, get_loan_history)
from utils.book_api import search_book_by_title
from utils.auth import check_authentication, show_user_info_sidebar, can_add_edit_delete, can_view
from utils.auth_utils import is_admin, get_user_profile, update_user_profile

# Page configuration
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 600;
    }
    .success-message {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None
    if 'show_success' not in st.session_state:
        st.session_state.show_success = False

def display_book_stats(books):
    """Display book statistics in metrics"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Books", len(books))

    with col2:
        unique_authors = set()
        for book in books:
            if isinstance(book.get('authors'), list):
                unique_authors.update(book['authors'])
            elif book.get('authors'):
                unique_authors.add(book['authors'])
        st.metric("Unique Authors", len(unique_authors))

    with col3:
        unique_publishers = len(set(book.get('publisher', 'Unknown') for book in books))
        st.metric("Publishers", unique_publishers)

    with col4:
        current_year = datetime.now().year
        recent_books = sum(1 for book in books
                          if book.get('publish_date') and
                          book['publish_date'].startswith(str(current_year)))
        st.metric(f"{current_year} Releases", recent_books)

def add_book_page():
    """Add book page with improved UI"""
    st.markdown("<h2>📖 Add New Book</h2>", unsafe_allow_html=True)

    # Initialize session state for form fields
    if 'book_data' not in st.session_state:
        st.session_state.book_data = {
            'title': '',
            'authors': '',
            'publisher': '',
            'edition': '',
            'publish_date': datetime.now(),
            'page_count': '',
            'isbn': '',
            'preview_url': '',
            'bookshelf_id': '',
            'owner_id': ''
        }

    # Title input with search button (outside form)
    col_title, col_search = st.columns([3, 1])

    with col_title:
        title_input = st.text_input("Title*",
                                    value=st.session_state.book_data['title'],
                                    placeholder="Enter book title",
                                    key="title_input")

    with col_search:
        st.write("")  # Spacer for alignment
        st.write("")  # Spacer for alignment
        search_button = st.button("🔍 Search", use_container_width=True, type="secondary")

    # Handle search button click
    if search_button:
        if not title_input or not title_input.strip():
            st.warning("⚠️ Please enter a book title to search.")
        else:
            with st.spinner("Searching for book information..."):
                book_info = search_book_by_title(title_input)

                if book_info:
                    st.success("✅ Book information found! Fields populated below.")
                    st.session_state.book_data['title'] = book_info.get('title', '')
                    st.session_state.book_data['authors'] = book_info.get('authors', '')
                    st.session_state.book_data['publisher'] = book_info.get('publisher', '')
                    st.session_state.book_data['page_count'] = str(book_info.get('page_count', ''))
                    st.session_state.book_data['isbn'] = book_info.get('isbn', '')
                    st.session_state.book_data['preview_url'] = book_info.get('preview_url', '')

                    # Parse publish date
                    if book_info.get('published_date'):
                        try:
                            st.session_state.book_data['publish_date'] = datetime.strptime(
                                book_info['published_date'], '%Y-%m-%d'
                            ).date()
                        except:
                            st.session_state.book_data['publish_date'] = datetime.now().date()

                    # Show additional info in expander
                    with st.expander("📋 Additional Information Found"):
                        if book_info.get('description'):
                            st.write(f"**Description:** {book_info['description'][:300]}...")
                        if book_info.get('isbn'):
                            st.write(f"**ISBN:** {book_info['isbn']}")
                        if book_info.get('page_count'):
                            st.write(f"**Pages:** {book_info['page_count']}")
                        if book_info.get('categories'):
                            st.write(f"**Categories:** {book_info['categories']}")

                    st.rerun()
                else:
                    st.warning("⚠️ No information found for this title. Please enter the details manually.")

    st.markdown("---")

    # Rest of the form
    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Title (confirm)*",
                                 value=st.session_state.book_data['title'],
                                 placeholder="Confirm book title")
            authors = st.text_input("Author(s)*",
                                   value=st.session_state.book_data['authors'],
                                   placeholder="Comma-separated authors")
            publisher = st.text_input("Publisher",
                                     value=st.session_state.book_data['publisher'],
                                     placeholder="Enter publisher name")
            isbn = st.text_input("ISBN",
                                value=st.session_state.book_data['isbn'],
                                placeholder="ISBN number")

        with col2:
            edition = st.text_input("Edition",
                                   value=st.session_state.book_data['edition'],
                                   placeholder="e.g., 1st, 2nd, Revised")
            page_count = st.text_input("Pages",
                                      value=st.session_state.book_data['page_count'],
                                      placeholder="Number of pages")
            publish_date = st.date_input("Publish Date",
                                        value=st.session_state.book_data['publish_date'],
                                        max_value=datetime.now())

        # Get bookshelves for dropdown
        bookshelves = get_bookshelves()
        shelf_options = [''] + [f"{shelf.get('shelf_id')} - {shelf.get('title')}" for shelf in bookshelves]
        bookshelf = st.selectbox("Bookshelf Location", shelf_options,
                                index=0 if not st.session_state.book_data['bookshelf_id'] else
                                shelf_options.index(next((opt for opt in shelf_options
                                                         if opt.startswith(f"{st.session_state.book_data['bookshelf_id']} -")), ''))
                                if any(opt.startswith(f"{st.session_state.book_data['bookshelf_id']} -") for opt in shelf_options) else 0)

        # Get owners for dropdown
        owners = get_owners()
        owner_options = [''] + [f"{owner.get('owner_id')} - {owner.get('name')}" for owner in owners]
        owner = st.selectbox("Owner", owner_options,
                            index=0 if not st.session_state.book_data['owner_id'] else
                            owner_options.index(next((opt for opt in owner_options
                                                     if opt.startswith(f"{st.session_state.book_data['owner_id']} -")), ''))
                            if any(opt.startswith(f"{st.session_state.book_data['owner_id']} -") for opt in owner_options) else 0)

        preview_url = st.text_input("Google Books Preview URL",
                                   value=st.session_state.book_data['preview_url'],
                                   placeholder="Preview URL (auto-populated from search)")

        # Show generated tracking number
        tracking_num = generate_tracking_number()
        st.info(f"📋 **Tracking Number:** {tracking_num} (will be auto-assigned)")

        st.markdown("**Required fields*")

        col_submit1, col_submit2 = st.columns(2)
        with col_submit1:
            submitted = st.form_submit_button("➕ Add Book", use_container_width=True)
        with col_submit2:
            clear_form = st.form_submit_button("🔄 Clear Form", use_container_width=True)

        if clear_form:
            st.session_state.book_data = {
                'title': '',
                'authors': '',
                'publisher': '',
                'edition': '',
                'publish_date': datetime.now(),
                'page_count': '',
                'isbn': '',
                'preview_url': '',
                'bookshelf_id': '',
                'owner_id': ''
            }
            st.rerun()

        if submitted:
            if not title or not title.strip():
                st.error("❌ Title is required!")
                return
            if not authors or not authors.strip():
                st.error("❌ At least one author is required!")
                return

            try:
                publish_date_str = publish_date.strftime("%Y-%m-%d")

                # Extract bookshelf ID from selection
                selected_shelf_id = ''
                if bookshelf and bookshelf.strip():
                    selected_shelf_id = bookshelf.split(' - ')[0]

                # Extract owner ID from selection
                selected_owner_id = ''
                if owner and owner.strip():
                    selected_owner_id = owner.split(' - ')[0]

                success, tracking_number = add_book(
                    title.strip(), authors.strip(),
                    publisher.strip() if publisher else "",
                    edition.strip() if edition else "",
                    publish_date_str,
                    page_count.strip() if page_count else "",
                    isbn.strip() if isbn else "",
                    preview_url.strip() if preview_url else "",
                    selected_shelf_id,
                    '',  # tracking_number (auto-generated)
                    selected_owner_id
                )

                if success:
                    # Clear session state after successful add
                    st.session_state.book_data = {
                        'title': '',
                        'authors': '',
                    'publisher': '',
                    'edition': '',
                    'publish_date': datetime.now(),
                    'page_count': '',
                    'isbn': '',
                    'preview_url': '',
                    'bookshelf_id': '',
                    'owner_id': ''
                }

                    st.success(f"✅ Book added successfully! Tracking #: {tracking_number}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to add book!")
            except Exception as e:
                st.error(f"❌ Failed to add book: {str(e)}")

def view_books_page():
    """View books page with improved table display"""
    st.markdown("<h2>📚 Library Collection</h2>", unsafe_allow_html=True)

    books = get_books()

    if not books:
        st.info("📭 No books in the library yet. Add your first book!")
        return

    # Display statistics
    display_book_stats(books)

    st.markdown("---")

    # Search and filter section
    st.markdown("### 🔍 Search & Filter")

    # Search and view mode in same row
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input("Search books", placeholder="Search by title, author, or publisher", label_visibility="collapsed")
    with search_col2:
        view_mode = st.selectbox("View Mode", ["Table", "Cards"], label_visibility="collapsed")

    # Filter controls in separate row
    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        # Bookshelf filter
        bookshelves = get_bookshelves()
        shelf_filter_options = ['All Bookshelves'] + [f"{shelf.get('shelf_id')} - {shelf.get('title')}" for shelf in bookshelves]
        selected_shelf_filter = st.selectbox("📚 Bookshelf", shelf_filter_options)

    with filter_col2:
        # Owner filter
        owners = get_owners()
        owner_filter_options = ['All Owners'] + [f"{owner.get('owner_id')} - {owner.get('name')}" for owner in owners]
        selected_owner_filter = st.selectbox("👤 Owner", owner_filter_options)

    with filter_col3:
        # Publish year filter - extract unique years from books
        years = set()
        for book in books:
            pub_date = book.get('publish_date', '')
            if pub_date and len(pub_date) >= 4:
                try:
                    years.add(pub_date[:4])
                except:
                    pass
        year_options = ['All Years'] + sorted(list(years), reverse=True)
        selected_year_filter = st.selectbox("📅 Publish Year", year_options)

    # Apply filters
    filtered_books = books

    # Text search filter
    if search_term:
        search_term_lower = search_term.lower()
        filtered_books = [
            book for book in filtered_books
            if search_term_lower in book.get('title', '').lower() or
               search_term_lower in str(book.get('authors', '')).lower() or
               search_term_lower in book.get('publisher', '').lower()
        ]

    # Bookshelf filter
    if selected_shelf_filter != 'All Bookshelves':
        selected_shelf_id = selected_shelf_filter.split(' - ')[0]
        filtered_books = [
            book for book in filtered_books
            if str(book.get('bookshelf_id', '')) == selected_shelf_id
        ]

    # Owner filter
    if selected_owner_filter != 'All Owners':
        selected_owner_id = selected_owner_filter.split(' - ')[0]
        filtered_books = [
            book for book in filtered_books
            if str(book.get('owner_id', '')) == selected_owner_id
        ]

    # Year filter
    if selected_year_filter != 'All Years':
        filtered_books = [
            book for book in filtered_books
            if book.get('publish_date', '').startswith(selected_year_filter)
        ]

    # Show filter results count
    st.info(f"📊 Showing {len(filtered_books)} of {len(books)} books")

    if not filtered_books:
        st.warning("No books match your filter criteria.")
        return

    st.markdown("---")

    if view_mode == "Table":
        # Create DataFrame for table view
        df_data = []
        for book in filtered_books:
            authors_str = book.get('authors', 'N/A')
            if isinstance(authors_str, list):
                authors_str = ", ".join(authors_str)

            # Get bookshelf title
            shelf_id = book.get('bookshelf_id', '')
            shelf_title = ''
            if shelf_id:
                bookshelves = get_bookshelves()
                matching_shelf = next((s for s in bookshelves if str(s.get('shelf_id')) == str(shelf_id)), None)
                if matching_shelf:
                    shelf_title = matching_shelf.get('title', '')

            # Get owner name
            owner_id = book.get('owner_id', '')
            owner_name = ''
            if owner_id:
                owners = get_owners()
                matching_owner = next((o for o in owners if str(o.get('owner_id')) == str(owner_id)), None)
                if matching_owner:
                    owner_name = matching_owner.get('name', '')

            # Get lending status
            is_lent = book.get('is_lent', False)
            if is_lent:
                lent_to = book.get('lent_to', 'Unknown')
                lent_date = book.get('lent_date', 'Unknown')
                status = f"🔴 Lent to {lent_to}"
            else:
                status = "🟢 Available"

            df_data.append({
                "Tracking #": book.get('tracking_number', 'N/A'),
                "Title": book.get('title', 'N/A'),
                "Author(s)": authors_str,
                "Owner": owner_name if owner_name else 'N/A',
                "Bookshelf": shelf_title if shelf_title else 'N/A',
                "Status": status,
                "ISBN": book.get('isbn', 'N/A')
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    else:  # Cards view
        # Display books in expandable cards
        for book in filtered_books:
            authors_str = book.get('authors', 'N/A')
            if isinstance(authors_str, list):
                authors_str = ", ".join(authors_str)

            # Get bookshelf title
            shelf_id = book.get('bookshelf_id', '')
            shelf_title = ''
            if shelf_id:
                bookshelves = get_bookshelves()
                matching_shelf = next((s for s in bookshelves if str(s.get('shelf_id')) == str(shelf_id)), None)
                if matching_shelf:
                    shelf_title = matching_shelf.get('title', '')

            # Get owner name
            owner_id = book.get('owner_id', '')
            owner_name = ''
            if owner_id:
                owners = get_owners()
                matching_owner = next((o for o in owners if str(o.get('owner_id')) == str(owner_id)), None)
                if matching_owner:
                    owner_name = matching_owner.get('name', '')

            # Get lending status for card title
            is_lent = book.get('is_lent', False)
            status_icon = "🔴" if is_lent else "🟢"

            with st.expander(f"{status_icon} {book.get('title', 'No Title')} - {book.get('tracking_number', 'No Tracking')}"):
                # Show lending status prominently if lent
                if is_lent:
                    st.error(f"🔴 **LENT OUT** - Borrowed by: {book.get('lent_to', 'Unknown')} on {book.get('lent_date', 'Unknown')}")
                else:
                    st.success("🟢 **AVAILABLE**")

                st.markdown("---")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Tracking #:** {book.get('tracking_number', 'N/A')}")
                    st.write(f"**Author(s):** {authors_str}")
                    st.write(f"**Publisher:** {book.get('publisher', 'N/A')}")
                    st.write(f"**ISBN:** {book.get('isbn', 'N/A')}")
                    st.write(f"**Pages:** {book.get('page_count', 'N/A')}")
                with col2:
                    st.write(f"**Edition:** {book.get('edition', 'N/A')}")
                    st.write(f"**Publish Date:** {book.get('publish_date', 'N/A')}")
                    st.write(f"**Owner:** {owner_name if owner_name else 'Not assigned'}")
                    st.write(f"**Bookshelf:** {shelf_title if shelf_title else 'Not assigned'}")
                    if book.get('preview_url'):
                        st.markdown(f"[📖 Google Books Preview]({book['preview_url']})")
                st.caption(f"Firestore ID: {book.get('id', 'N/A')}")

def edit_delete_book_page():
    """Edit/Delete book page with improved UI"""
    st.markdown("<h2>✏️ Manage Books</h2>", unsafe_allow_html=True)

    books = get_books()

    if not books:
        st.info("📭 No books available to edit or delete.")
        return

    # Book selection
    book_options = [f"{book.get('title', 'Untitled')} - {book.get('authors', 'Unknown')} ({book.get('id', '')})"
                   for book in books]
    selected_option = st.selectbox("Select a book", book_options, key="book_selector")

    if selected_option:
        # Extract book ID from selection
        book_id = selected_option.split('(')[-1].rstrip(')')
        selected_book = next((book for book in books if book.get('id') == book_id), None)

        if selected_book:
            # Create tabs for Edit and Delete
            tab1, tab2 = st.tabs(["✏️ Edit", "🗑️ Delete"])

            with tab1:
                # Initialize session state for edit form
                if 'edit_book_data' not in st.session_state:
                    st.session_state.edit_book_data = {}

                # Search button to auto-fill missing data
                st.markdown("### 🔍 Auto-Fill Missing Information")
                col_search1, col_search2 = st.columns([3, 1])

                with col_search1:
                    st.write(f"**Current Title:** {selected_book.get('title', 'N/A')}")

                with col_search2:
                    search_btn = st.button("🔍 Search & Fill", use_container_width=True, type="secondary")

                if search_btn:
                    title_to_search = selected_book.get('title', '')
                    if title_to_search:
                        with st.spinner("Searching for book information..."):
                            book_info = search_book_by_title(title_to_search)

                            if book_info:
                                # Only update fields that are empty or missing
                                updated_fields = []

                                if not selected_book.get('isbn') and book_info.get('isbn'):
                                    st.session_state.edit_book_data['isbn'] = book_info['isbn']
                                    updated_fields.append('ISBN')

                                if not selected_book.get('page_count') and book_info.get('page_count'):
                                    st.session_state.edit_book_data['page_count'] = str(book_info['page_count'])
                                    updated_fields.append('Pages')

                                if not selected_book.get('preview_url') and book_info.get('preview_url'):
                                    st.session_state.edit_book_data['preview_url'] = book_info['preview_url']
                                    updated_fields.append('Preview URL')

                                if not selected_book.get('publisher') and book_info.get('publisher'):
                                    st.session_state.edit_book_data['publisher'] = book_info['publisher']
                                    updated_fields.append('Publisher')

                                if not selected_book.get('publish_date') and book_info.get('published_date'):
                                    st.session_state.edit_book_data['publish_date'] = book_info['published_date']
                                    updated_fields.append('Publish Date')

                                if updated_fields:
                                    st.success(f"✅ Updated fields: {', '.join(updated_fields)}")
                                    st.rerun()
                                else:
                                    st.info("ℹ️ All fields already have data. No updates needed.")
                            else:
                                st.warning("⚠️ No information found for this title.")

                st.markdown("---")

                with st.form("edit_book_form"):
                    col1, col2 = st.columns(2)

                    # Check if tracking number exists, if not show warning
                    current_tracking = selected_book.get('tracking_number', '')
                    if not current_tracking:
                        new_tracking = generate_tracking_number()
                        st.warning(f"⚠️ **No tracking number!** Will auto-generate: {new_tracking}")
                    else:
                        st.info(f"📋 **Tracking Number:** {current_tracking}")

                    with col1:
                        new_title = st.text_input("Title", value=selected_book.get('title', ''))

                        authors_val = selected_book.get('authors', '')
                        if isinstance(authors_val, list):
                            authors_val = ", ".join(authors_val)
                        new_authors = st.text_input("Author(s)", value=authors_val)

                        # Use session state data if available from search, otherwise use book data
                        publisher_value = st.session_state.edit_book_data.get('publisher', selected_book.get('publisher', ''))
                        new_publisher = st.text_input("Publisher", value=publisher_value)

                        isbn_value = st.session_state.edit_book_data.get('isbn', selected_book.get('isbn', ''))
                        new_isbn = st.text_input("ISBN", value=isbn_value)

                    with col2:
                        new_edition = st.text_input("Edition", value=selected_book.get('edition', ''))

                        page_count_value = st.session_state.edit_book_data.get('page_count', selected_book.get('page_count', ''))
                        new_page_count = st.text_input("Pages", value=page_count_value)

                        # Parse date - use session state if available
                        date_str = st.session_state.edit_book_data.get('publish_date', selected_book.get('publish_date', ''))
                        try:
                            current_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
                        except:
                            current_date = datetime.now().date()

                        new_publish_date = st.date_input("Publish Date", value=current_date)

                    # Bookshelf selector
                    bookshelves = get_bookshelves()
                    shelf_options = [''] + [f"{shelf.get('shelf_id')} - {shelf.get('title')}" for shelf in bookshelves]

                    # Find current bookshelf index
                    current_shelf_id = str(selected_book.get('bookshelf_id', ''))
                    current_index = 0
                    if current_shelf_id:
                        for i, opt in enumerate(shelf_options):
                            if opt.startswith(f"{current_shelf_id} -"):
                                current_index = i
                                break

                    new_bookshelf = st.selectbox("Bookshelf Location", shelf_options, index=current_index)

                    # Owner selector
                    owners = get_owners()
                    owner_options = [''] + [f"{owner.get('owner_id')} - {owner.get('name')}" for owner in owners]

                    # Find current owner index
                    current_owner_id = str(selected_book.get('owner_id', ''))
                    current_owner_index = 0
                    if current_owner_id:
                        for i, opt in enumerate(owner_options):
                            if opt.startswith(f"{current_owner_id} -"):
                                current_owner_index = i
                                break

                    new_owner = st.selectbox("Owner", owner_options, index=current_owner_index)

                    preview_url_value = st.session_state.edit_book_data.get('preview_url', selected_book.get('preview_url', ''))
                    new_preview_url = st.text_input("Google Books Preview URL", value=preview_url_value)

                    update_button = st.form_submit_button("💾 Update Book", use_container_width=True)

                    if update_button:
                        if not new_title or not new_title.strip():
                            st.error("❌ Title cannot be empty!")
                            return
                        if not new_authors or not new_authors.strip():
                            st.error("❌ At least one author is required!")
                            return

                        try:
                            new_publish_date_str = new_publish_date.strftime("%Y-%m-%d")

                            # Extract bookshelf ID
                            selected_shelf_id = ''
                            if new_bookshelf and new_bookshelf.strip():
                                selected_shelf_id = new_bookshelf.split(' - ')[0]

                            # Extract owner ID
                            selected_owner_id = ''
                            if new_owner and new_owner.strip():
                                selected_owner_id = new_owner.split(' - ')[0]

                            # Generate tracking number if missing
                            tracking_to_save = ''
                            if not current_tracking:
                                tracking_to_save = generate_tracking_number()

                            edit_book(book_id, new_title.strip(), new_authors.strip(),
                                    new_publisher.strip(), new_edition.strip(),
                                    new_publish_date_str,
                                    new_page_count.strip() if new_page_count else "",
                                    new_isbn.strip() if new_isbn else "",
                                    new_preview_url.strip() if new_preview_url else "",
                                    selected_shelf_id,
                                    tracking_to_save,
                                    selected_owner_id)

                            # Clear edit session state
                            st.session_state.edit_book_data = {}

                            success_msg = "✅ Book updated successfully!"
                            if tracking_to_save:
                                success_msg += f" Tracking #: {tracking_to_save}"

                            st.success(success_msg)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to update book: {str(e)}")

            with tab2:
                st.warning("⚠️ This action cannot be undone!")
                st.write(f"**Title:** {selected_book.get('title', 'N/A')}")

                authors_display = selected_book.get('authors', 'N/A')
                if isinstance(authors_display, list):
                    authors_display = ", ".join(authors_display)
                st.write(f"**Author(s):** {authors_display}")

                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("🗑️ Confirm Delete", type="primary", use_container_width=True):
                        try:
                            delete_book(book_id)
                            st.success("✅ Book deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to delete book: {str(e)}")

def manage_bookshelves_page():
    """Manage bookshelves page"""
    st.markdown("<h2>📚 Manage Bookshelves</h2>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Add Bookshelf", "📋 View/Edit Bookshelves"])

    with tab1:
        st.markdown("### Add New Bookshelf")
        with st.form("add_shelf_form"):
            shelf_title = st.text_input("Shelf Title*", placeholder="e.g., Living Room Shelf A")
            shelf_description = st.text_area("Description", placeholder="Optional description")

            submitted = st.form_submit_button("➕ Add Bookshelf", use_container_width=True)

            if submitted:
                if not shelf_title or not shelf_title.strip():
                    st.error("❌ Shelf title is required!")
                else:
                    success, shelf_id = add_bookshelf(shelf_title.strip(), shelf_description.strip())
                    if success:
                        st.success(f"✅ Bookshelf added successfully! ID: {shelf_id}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add bookshelf!")

    with tab2:
        st.markdown("### Existing Bookshelves")
        shelves = get_bookshelves()

        if not shelves:
            st.info("📭 No bookshelves created yet.")
        else:
            for shelf in sorted(shelves, key=lambda x: x.get('shelf_id', 0)):
                with st.expander(f"📚 Shelf #{shelf.get('shelf_id')} - {shelf.get('title', 'Untitled')}"):
                    with st.form(f"edit_shelf_{shelf.get('id')}"):
                        new_title = st.text_input("Title", value=shelf.get('title', ''))
                        new_desc = st.text_area("Description", value=shelf.get('description', ''))

                        col1, col2 = st.columns(2)
                        with col1:
                            update = st.form_submit_button("💾 Update", use_container_width=True)
                        with col2:
                            delete = st.form_submit_button("🗑️ Delete", type="primary", use_container_width=True)

                        if update:
                            if edit_bookshelf(shelf.get('id'), new_title, new_desc):
                                st.success("✅ Updated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Update failed!")

                        if delete:
                            if delete_bookshelf(shelf.get('id')):
                                st.success("✅ Deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Delete failed!")

def manage_owners_page():
    """Manage book owners page"""
    st.markdown("<h2>👤 Manage Owners</h2>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Add Owner", "📋 View/Edit Owners"])

    with tab1:
        st.markdown("### Add New Owner")
        with st.form("add_owner_form"):
            owner_id = st.text_input("Owner ID* (3 digits)", placeholder="e.g., 001", max_chars=3)
            owner_name = st.text_input("Name*", placeholder="Owner's full name")
            email = st.text_input("Email", placeholder="owner@email.com")
            cell_phone = st.text_input("Cell Phone", placeholder="+1234567890")

            submitted = st.form_submit_button("➕ Add Owner", use_container_width=True)

            if submitted:
                if not owner_id or not owner_id.strip():
                    st.error("❌ Owner ID is required!")
                elif not owner_name or not owner_name.strip():
                    st.error("❌ Owner name is required!")
                else:
                    success, message = add_owner(owner_id.strip(), owner_name.strip(),
                                                email.strip(), cell_phone.strip())
                    if success:
                        st.success(f"✅ Owner added successfully! ID: {owner_id}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

    with tab2:
        st.markdown("### Existing Owners")
        owners = get_owners()

        if not owners:
            st.info("📭 No owners created yet.")
        else:
            for owner in sorted(owners, key=lambda x: x.get('owner_id', '')):
                with st.expander(f"👤 {owner.get('owner_id')} - {owner.get('name', 'Unnamed')}"):
                    with st.form(f"edit_owner_{owner.get('id')}"):
                        st.info(f"**Owner ID:** {owner.get('owner_id')} (cannot be changed)")
                        new_name = st.text_input("Name", value=owner.get('name', ''))
                        new_email = st.text_input("Email", value=owner.get('email', ''))
                        new_phone = st.text_input("Cell Phone", value=owner.get('cell_phone', ''))

                        col1, col2 = st.columns(2)
                        with col1:
                            update = st.form_submit_button("💾 Update", use_container_width=True)
                        with col2:
                            delete = st.form_submit_button("🗑️ Delete", type="primary", use_container_width=True)

                        if update:
                            if not new_name or not new_name.strip():
                                st.error("❌ Name cannot be empty!")
                            else:
                                if edit_owner(owner.get('id'), new_name, new_email, new_phone):
                                    st.success("✅ Updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Update failed!")

                        if delete:
                            if delete_owner(owner.get('id')):
                                st.success("✅ Deleted successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Delete failed!")

def user_profile_page():
    """User profile page for creating/updating profile"""
    st.markdown("<h2>👤 User Profile</h2>", unsafe_allow_html=True)

    user_email = st.session_state.user_email
    user_profile = get_user_profile(db, user_email)

    if not user_profile:
        st.error("❌ Could not load user profile!")
        return

    # Show profile creation prompt if not created
    if not user_profile.get('profile_created', False):
        st.warning("⚠️ **Please complete your profile before using the system.**")

    st.markdown("---")

    with st.form("profile_form"):
        st.markdown("### Personal Information")

        col1, col2 = st.columns(2)

        with col1:
            email_display = st.text_input("Email", value=user_email, disabled=True)
            full_name = st.text_input("Full Name*",
                                     value=user_profile.get('full_name', ''),
                                     placeholder="Enter your full name")

        with col2:
            display_name = st.text_input("Display Name",
                                        value=user_profile.get('display_name', ''),
                                        disabled=True)
            cell_phone = st.text_input("Cell Phone*",
                                      value=user_profile.get('cell_phone', ''),
                                      placeholder="+1234567890")

        st.markdown("---")
        st.info("**Note:** Complete profile is required before borrowing books.")

        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

        if submitted:
            if not full_name or not full_name.strip():
                st.error("❌ Full name is required!")
            elif not cell_phone or not cell_phone.strip():
                st.error("❌ Cell phone is required!")
            else:
                success = update_user_profile(db, user_profile['id'],
                                             full_name.strip(), cell_phone.strip())
                if success:
                    st.success("✅ Profile updated successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to update profile!")

def manage_users_page():
    """Admin-only user management page"""
    st.markdown("<h2>👥 User Management</h2>", unsafe_allow_html=True)

    # Check if admin (by email OR by access level)
    if not (is_admin(st.session_state.user_email) or st.session_state.access_level == 'admin'):
        st.error("🚫 Access Denied - Admin only!")
        return

    st.markdown("### User Access Control")
    st.info("💡 Manage user access levels and approve new users")

    users = get_all_users()

    if not users:
        st.info("📭 No users found.")
        return

    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        admin_count = len([u for u in users if u.get('access_level') == 'admin'])
        st.metric("Admin", admin_count)
    with col2:
        # Count both 'manage' and old 'full' as manage
        manage_count = len([u for u in users if u.get('access_level') in ['manage', 'full']])
        st.metric("Manage", manage_count)
    with col3:
        view_only = len([u for u in users if u.get('access_level') == 'view'])
        st.metric("View Only", view_only)
    with col4:
        no_access = len([u for u in users if u.get('access_level') == 'none'])
        st.metric("Pending", no_access)

    st.markdown("---")

    # Filter by access level
    filter_options = ['All Users', 'Admin', 'Manage', 'View Only', 'No Access']
    selected_filter = st.selectbox("Filter by Access Level", filter_options)

    # Apply filter
    filtered_users = users
    if selected_filter == 'Admin':
        filtered_users = [u for u in users if u.get('access_level') == 'admin']
    elif selected_filter == 'Manage':
        # Include both 'manage' and old 'full' in Manage filter
        filtered_users = [u for u in users if u.get('access_level') in ['manage', 'full']]
    elif selected_filter == 'View Only':
        filtered_users = [u for u in users if u.get('access_level') == 'view']
    elif selected_filter == 'No Access':
        filtered_users = [u for u in users if u.get('access_level') == 'none']

    # Display users
    for user in filtered_users:
        email = user.get('email', 'N/A')
        access_level = user.get('access_level', 'none')

        # Icon based on access level
        if access_level == 'admin':
            icon = '🔒'
        elif access_level == 'manage' or access_level == 'full':  # Map old 'full' to 'manage'
            icon = '✏️'
        elif access_level == 'view':
            icon = '👁️'
        else:
            icon = '🚫'

        with st.expander(f"{icon} {user.get('display_name', 'N/A')} ({email})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Email:** {email}")
                st.write(f"**Display Name:** {user.get('display_name', 'N/A')}")
                st.write(f"**Full Name:** {user.get('full_name', 'Not set')}")
                st.write(f"**Cell Phone:** {user.get('cell_phone', 'Not set')}")

            with col2:
                st.write(f"**Profile Created:** {'✅ Yes' if user.get('profile_created') else '❌ No'}")
                st.write(f"**Created:** {user.get('created_at', 'N/A')[:10]}")
                st.write(f"**Last Login:** {user.get('last_login', 'N/A')[:10]}")

                if user.get('approved_by'):
                    st.write(f"**Approved By:** {user.get('approved_by')}")

            # Access level control
            st.markdown("---")
            st.markdown("**Change Access Level:**")

            # Map old 'full' to new 'manage' for backward compatibility
            display_access_level = 'manage' if access_level == 'full' else access_level

            # Show warning if user has old 'full' access level
            if access_level == 'full':
                st.warning("⚠️ This user has old 'full' access. Please update to 'manage' or 'admin'.")

            new_access = st.selectbox(
                "Access Level",
                ['admin', 'manage', 'view', 'none'],
                index=['admin', 'manage', 'view', 'none'].index(display_access_level),
                key=f"access_{user.get('id')}"
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button(f"💾 Update Access", key=f"update_{user.get('id')}", use_container_width=True):
                    success = update_user_access(user.get('id'), new_access, st.session_state.user_email)
                    if success:
                        st.success(f"✅ Updated {email} to {new_access} access!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update access!")

            with col_btn2:
                if st.button(f"🗑️ Delete User", key=f"delete_{user.get('id')}", type="primary", use_container_width=True):
                    # Prevent deleting yourself
                    if email == st.session_state.user_email:
                        st.error("❌ You cannot delete your own account!")
                    else:
                        success = delete_user(user.get('id'))
                        if success:
                            st.success(f"✅ User {email} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete user!")

def book_lending_page():
    """Admin-only book lending page"""
    st.markdown("<h2>📖 Book Lending</h2>", unsafe_allow_html=True)

    # Check if admin (by email OR by access level)
    if not (is_admin(st.session_state.user_email) or st.session_state.access_level == 'admin'):
        st.error("🚫 Access Denied - Admin only!")
        return

    tab1, tab2, tab3 = st.tabs(["📤 Lend Book", "📥 Return Book", "📊 Loan History"])

    with tab1:
        st.markdown("### Lend a Book")

        with st.form("lend_book_form"):
            # Get available books (not lent)
            all_books = get_books()
            available_books = [b for b in all_books if not b.get('is_lent', False)]

            if not available_books:
                st.warning("⚠️ No books available to lend!")
                st.form_submit_button("Lend Book", disabled=True)
            else:
                book_options = [f"{b.get('title')} - {b.get('tracking_number', 'No tracking')}"
                               for b in available_books]
                selected_book_str = st.selectbox("Select Book*", book_options)

                # Get users with profiles
                all_users = get_all_users()
                users_with_profiles = [u for u in all_users if u.get('profile_created', False)]

                if not users_with_profiles:
                    st.warning("⚠️ No users with completed profiles!")
                    user_options = []
                else:
                    user_options = [f"{u.get('full_name', u.get('display_name'))} ({u.get('email')})"
                                   for u in users_with_profiles]

                selected_user_str = st.selectbox("Borrower*", user_options if user_options else ["No users available"])

                # Due date (default 14 days from now)
                default_due = datetime.now().date() + timedelta(days=14)
                due_date = st.date_input("Due Date*", value=default_due, min_value=datetime.now().date())

                submitted = st.form_submit_button("📤 Lend Book", use_container_width=True)

                if submitted:
                    if not user_options:
                        st.error("❌ No users available!")
                    else:
                        # Extract book ID
                        selected_book = available_books[book_options.index(selected_book_str)]
                        book_id = selected_book.get('id')

                        # Extract user info
                        selected_user = users_with_profiles[user_options.index(selected_user_str)]
                        borrower_email = selected_user.get('email')
                        borrower_name = selected_user.get('full_name', selected_user.get('display_name'))

                        # Lend book
                        success, message = lend_book(
                            book_id,
                            borrower_email,
                            borrower_name,
                            st.session_state.user_email,
                            due_date.strftime("%Y-%m-%d")
                        )

                        if success:
                            st.success(f"✅ {message}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

    with tab2:
        st.markdown("### Return a Book")

        active_loans = get_active_loans()

        if not active_loans:
            st.info("📭 No active loans.")
        else:
            for loan in active_loans:
                with st.expander(f"📕 {loan.get('book_title')} - {loan.get('tracking_number')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Book:** {loan.get('book_title')}")
                        st.write(f"**Tracking #:** {loan.get('tracking_number')}")
                        st.write(f"**Borrowed By:** {loan.get('borrowed_by_name')}")

                    with col2:
                        st.write(f"**Borrowed Date:** {loan.get('borrowed_date')}")
                        st.write(f"**Due Date:** {loan.get('due_date')}")

                        # Check if overdue
                        try:
                            due = datetime.strptime(loan.get('due_date'), "%Y-%m-%d").date()
                            if due < datetime.now().date():
                                days_overdue = (datetime.now().date() - due).days
                                st.error(f"⚠️ **OVERDUE by {days_overdue} days!**")
                            else:
                                days_remaining = (due - datetime.now().date()).days
                                if days_remaining <= 3:
                                    st.warning(f"⚠️ Due in {days_remaining} days")
                                else:
                                    st.success(f"✅ {days_remaining} days remaining")
                        except:
                            pass

                    if st.button(f"📥 Mark as Returned", key=f"return_{loan.get('id')}", use_container_width=True):
                        success, message = return_book(loan.get('book_id'))
                        if success:
                            st.success(f"✅ {message}")
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

    with tab3:
        st.markdown("### Loan History")

        # Filter options
        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            all_users = get_all_users()
            user_filter_options = ['All Users'] + [u.get('email') for u in all_users]
            selected_user_filter = st.selectbox("Filter by User", user_filter_options)

        with col_filter2:
            status_filter = st.selectbox("Status", ['All', 'Active', 'Returned'])

        # Get loan history
        if selected_user_filter == 'All Users':
            loan_history = get_loan_history()
        else:
            loan_history = get_loan_history(selected_user_filter)

        # Apply status filter
        if status_filter == 'Active':
            loan_history = [l for l in loan_history if not l.get('returned', False)]
        elif status_filter == 'Returned':
            loan_history = [l for l in loan_history if l.get('returned', False)]

        st.info(f"📊 Showing {len(loan_history)} loan(s)")

        if not loan_history:
            st.info("📭 No loan history found.")
        else:
            # Create DataFrame
            df_data = []
            for loan in loan_history:
                df_data.append({
                    "Tracking #": loan.get('tracking_number', 'N/A'),
                    "Book": loan.get('book_title', 'N/A'),
                    "Borrower": loan.get('borrowed_by_name', 'N/A'),
                    "Borrowed": loan.get('borrowed_date', 'N/A'),
                    "Due": loan.get('due_date', 'N/A'),
                    "Returned": loan.get('returned_date', 'Not returned') if loan.get('returned') else 'Active',
                    "Status": '✅ Returned' if loan.get('returned') else '📖 Active'
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

def main():
    # Check authentication first
    if not check_authentication():
        return  # Stop here if not authenticated

    initialize_session_state()

    # Header
    st.markdown('<p class="main-header">📚 Library Management System</p>', unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("---")

    # Build menu based on access level
    user_access_level = st.session_state.access_level
    # Check if user is admin by email OR by access level in database
    user_is_admin = is_admin(st.session_state.user_email) or user_access_level == 'admin'
    has_manage_access = can_add_edit_delete()
    has_view_access = can_view()

    menu_options = {}

    # All authenticated users with view/manage/admin can view books
    if has_view_access:
        menu_options["📚 View Books"] = "view"

    # Manage and Admin users get book management features
    if has_manage_access:
        menu_options["➕ Add Book"] = "add"
        menu_options["✏️ Manage Books"] = "manage"
        menu_options["📚 Bookshelves"] = "shelves"
        menu_options["👤 Owners"] = "owners"

    # Admin-only features (by email OR by access level)
    if user_is_admin:
        menu_options["📖 Book Lending"] = "lending"
        menu_options["👥 User Management"] = "users"

    # All users can access their profile
    menu_options["👤 My Profile"] = "profile"

    choice = st.sidebar.radio("Go to", list(menu_options.keys()))

    # Show user info in sidebar
    show_user_info_sidebar()

    st.sidebar.markdown("---")
    if user_access_level == 'admin':
        st.sidebar.info("🔒 **Admin:** Full system access")
    elif user_access_level == 'manage':
        st.sidebar.info("✏️ **Manage:** Can add/edit books")
    elif user_access_level == 'view':
        st.sidebar.info("👁️ **View:** Read-only access")

    # Route to appropriate page
    selected_page = menu_options[choice]

    if selected_page == "add":
        if has_manage_access:
            add_book_page()
        else:
            st.error("🚫 Access Denied - Manage access required!")
    elif selected_page == "view":
        view_books_page()
    elif selected_page == "manage":
        if has_manage_access:
            edit_delete_book_page()
        else:
            st.error("🚫 Access Denied - Manage access required!")
    elif selected_page == "shelves":
        if has_manage_access:
            manage_bookshelves_page()
        else:
            st.error("🚫 Access Denied - Manage access required!")
    elif selected_page == "owners":
        if has_manage_access:
            manage_owners_page()
        else:
            st.error("🚫 Access Denied - Manage access required!")
    elif selected_page == "lending":
        if user_is_admin:
            book_lending_page()
        else:
            st.error("🚫 Access Denied - Admin only!")
    elif selected_page == "users":
        if user_is_admin:
            manage_users_page()
        else:
            st.error("🚫 Access Denied - Admin only!")
    elif selected_page == "profile":
        user_profile_page()

if __name__ == "__main__":
    main()