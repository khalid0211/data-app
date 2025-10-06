# 📚 Library Management System

A comprehensive library management system built with Streamlit and Firebase, featuring authentication, access control, and book lending capabilities.

## ✨ Features

### 🔐 Authentication & Access Control
- **Temporary Authentication** (for testing) - Email/Name login
- **Four Access Levels:**
  - 🔒 **Admin** - Full system access including user management and book lending
  - ✏️ **Manage** - Add, edit, delete books and manage system
  - 👁️ **View** - Read-only access to library
  - 🚫 **None** - Must request approval from admin
- **Admin Controls** - User management and book lending (khalid0211@gmail.com)

### 📖 Book Management
- Add books with Google Books API auto-fill
- Edit and delete books
- Track books by:
  - Unique tracking numbers (BK-YYYYMMDD-XXXX)
  - ISBN
  - Bookshelves (physical locations)
  - Owners (3-digit owner IDs)
- Search and filter books
- Table and card view modes

### 📤 Book Lending System (Admin Only)
- Lend books to authenticated users
- Track active loans with due dates
- Return books
- Overdue indicators (🔴 red for overdue, ⚠️ yellow for due soon)
- Complete loan history with filtering
- Borrower must have completed profile

### 👤 User Management
- User registration on first login
- Admin approval required for access
- User profiles with contact information
- Profile required before borrowing books

### 📚 Additional Features
- Bookshelf management (organize by location)
- Owner management (track book ownership)
- Book statistics dashboard
- Lending status visible in all views (🟢 Available / 🔴 Lent Out)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to project directory
cd F:\Coding\data-app

# Install dependencies
python -m pip install streamlit firebase-admin pandas requests pyrebase4 setuptools
```

### 2. Firebase Setup

**You need:**
- Firebase Admin SDK key at: `D:\Dropbox\MySoftware\Portfolio\mylibrary-firebase.json`
- Firebase project with Firestore database

**Collections needed:**
- `books` - Book records
- `bookshelves` - Shelf locations
- `owners` - Book owners
- `users` - User accounts and access levels
- `book_loans` - Lending transactions

### 3. Run Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📖 Usage

### Admin Account
- **Email:** khalid0211@gmail.com
- **Automatically gets:** Full access + Admin privileges

### New User Flow
1. Visit app → Enter email and name
2. User created with "no access"
3. Contact admin for approval
4. Admin grants access via User Management page
5. User can now access system

### Adding Books
1. Go to **➕ Add Book**
2. Enter book title
3. Click **🔍 Search** to auto-fill from Google Books API
4. Or enter details manually
5. Assign to bookshelf and owner (optional)
6. Click **➕ Add Book**

### Lending Books (Admin Only)
1. Go to **📖 Book Lending**
2. **Lend Book** tab:
   - Select available book
   - Select borrower (must have profile)
   - Set due date (default: 14 days)
   - Click **📤 Lend Book**
3. **Return Book** tab:
   - View active loans
   - Click **📥 Mark as Returned**
4. **Loan History** tab:
   - View all loans
   - Filter by user or status

---

## 📁 Project Structure

```
F:\Coding\data-app\
├── app.py                              # Main application
├── utils/
│   ├── firebase_utils.py               # Firestore database operations
│   ├── book_api.py                     # Google Books API integration
│   ├── auth_utils.py                   # Authentication utilities
│   └── simple_auth.py                  # Temporary authentication
├── config/
│   └── firebase_config.json            # Firebase web config (not used yet)
├── AUTHENTICATION_SETUP_GUIDE.md       # Guide for Google OAuth upgrade
├── IMPLEMENTATION_STATUS.md            # Implementation details
├── TESTING_GUIDE.md                    # Step-by-step testing guide
└── README.md                           # This file
```

---

## 🎯 Access Levels Explained

### 🔒 Admin (khalid0211@gmail.com)
**Can do:**
- Everything Manage can do (below)
- Lend books to users
- Return books
- View loan history
- Approve new users
- Change user access levels

### ✏️ Manage
**Can do:**
- View all books
- Add new books
- Edit/delete books
- Manage bookshelves
- Manage owners
- Update own profile

**Cannot do:**
- Lend/return books (admin only)
- Manage other users (admin only)

### 👁️ View
**Can do:**
- View all books (read-only)
- Update own profile

**Cannot do:**
- Add, edit, or delete anything
- Borrow books

### 🚫 None
**Can do:**
- Create/update own profile
- Request access from admin

**Cannot do:**
- Access any library features

---

## 🔧 Configuration

### Admin Email
Hardcoded in `utils/auth_utils.py`:
```python
ADMIN_EMAIL = "khalid0211@gmail.com"
```

### Firebase Key Path
Located in `utils/firebase_utils.py`:
```python
key_path = "D:\\Dropbox\\MySoftware\\Portfolio\\mylibrary-firebase.json"
```

### Default Loan Period
In `book_lending_page()`:
```python
default_due = datetime.now().date() + timedelta(days=14)  # 14 days
```

---

## 📊 Database Schema

### users Collection
```python
{
    'email': 'user@gmail.com',
    'gmail_id': 'user@gmail.com',
    'display_name': 'User Name',
    'access_level': 'manage',  # 'admin', 'manage', 'view', 'none'
    'profile_created': True,
    'full_name': 'Full Name',
    'cell_phone': '+1234567890',
    'created_at': '2024-01-01T00:00:00Z',
    'last_login': '2024-01-01T00:00:00Z',
    'approved_by': 'khalid0211@gmail.com',
    'approved_at': '2024-01-01T00:00:00Z'
}
```

### books Collection
```python
{
    'title': 'Book Title',
    'authors': ['Author 1', 'Author 2'],
    'publisher': 'Publisher Name',
    'edition': '1st Edition',
    'publish_date': '2024-01-01',
    'page_count': '300',
    'isbn': '978-1234567890',
    'preview_url': 'https://books.google.com/...',
    'tracking_number': 'BK-20240101-0001',
    'bookshelf_id': '1',
    'owner_id': '001',
    'is_lent': False,
    'lent_to': '',
    'lent_date': '',
    'lent_by': ''
}
```

### book_loans Collection
```python
{
    'book_id': 'firestore_doc_id',
    'tracking_number': 'BK-20240101-0001',
    'book_title': 'Book Title',
    'borrowed_by_email': 'user@gmail.com',
    'borrowed_by_name': 'User Name',
    'borrowed_date': '2024-01-01',
    'due_date': '2024-01-15',
    'returned': False,
    'returned_date': None,
    'approved_by': 'khalid0211@gmail.com'
}
```

---

## 🔄 Upgrading to Google OAuth

Currently using **temporary authentication** (email/name input only).

**To upgrade to production Google OAuth:**
1. Follow `AUTHENTICATION_SETUP_GUIDE.md` steps 1-3
2. Install `streamlit-google-auth` or implement Firebase JS SDK
3. Replace `simple_auth.py` with OAuth implementation
4. All other code remains unchanged

**Note:** User management, book lending, and access control are independent of authentication method.

---

## 🧪 Testing

See `TESTING_GUIDE.md` for comprehensive testing scenarios including:
- Admin login and setup
- New user registration and approval
- Book lending workflow
- Access control verification
- Profile requirements
- Overdue notifications

---

## 📞 Support

### Common Issues

**Import errors:**
```bash
python -m pip install setuptools firebase-admin streamlit pandas requests pyrebase4
```

**Firebase connection failed:**
- Verify key path in `utils/firebase_utils.py`
- Check Firebase project is active

**User can't borrow books:**
- User must complete profile first (👤 My Profile)
- Admin must approve user with "full" or "view" access

**Book can't be lent:**
- Book must not already be lent
- Borrower must have completed profile

---

## 🎉 Features Implemented

✅ Authentication with email/name (temporary)
✅ Four-tier access control (Admin, Manage, View, None)
✅ User management and approval system
✅ User profiles with contact information
✅ Book CRUD operations
✅ Google Books API auto-fill
✅ Book tracking numbers
✅ Bookshelf management
✅ Owner management
✅ Book lending system
✅ Loan tracking and history
✅ Overdue detection and indicators
✅ Lending status in all views
✅ Search and filter capabilities
✅ Table and card view modes
✅ Complete access control on all pages

---

## 🚀 Future Enhancements

- [ ] Upgrade to Google OAuth authentication
- [ ] Email notifications for due dates
- [ ] Automated overdue reminders
- [ ] User borrowing history
- [ ] Book reservation system
- [ ] QR code generation for tracking numbers
- [ ] Export loan reports to PDF/Excel
- [ ] Book statistics and analytics
- [ ] Mobile-responsive design improvements

---

## 👨‍💻 Developer

**Dr. Khalid Ahmad Khan**
- Email: khalid0211@gmail.com
- Admin Access: Automatically granted

---

## 📄 License

For internal use only.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Database: [Firebase Firestore](https://firebase.google.com/docs/firestore)
- Book data: [Google Books API](https://developers.google.com/books)

---

**Ready to use! 🎉**

Run `streamlit run app.py` to get started.
