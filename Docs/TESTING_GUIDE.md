# 🧪 Testing Guide - Library Management System

## Quick Start Testing

### 1. Launch the Application

```bash
cd F:\Coding\data-app
streamlit run app.py
```

The app should open in your default browser at `http://localhost:8501`

---

## 2. Test Scenario 1: Admin Login & Setup

### Login as Admin
1. **Email:** khalid0211@gmail.com
2. **Display Name:** Dr. Khalid Ahmad Khan
3. Click **🔐 Sign In**

**Expected Result:**
- ✅ Login successful
- ✅ Redirected to main app
- ✅ Sidebar shows: "Access: 🔒 Admin"
- ✅ Menu shows all options:
  - 📚 View Books
  - ➕ Add Book
  - ✏️ Manage Books
  - 📚 Bookshelves
  - 👤 Owners
  - 📖 Book Lending (Admin only)
  - 👥 User Management (Admin only)
  - 👤 My Profile
- ✅ Sidebar tip: "🔒 Admin: Full system access"

### Complete Admin Profile
1. Click **👤 My Profile** in sidebar
2. Fill in:
   - **Full Name:** Dr. Khalid Ahmad Khan
   - **Cell Phone:** +1234567890 (or your actual number)
3. Click **💾 Save Profile**

**Expected Result:**
- ✅ Success message
- ✅ Balloons animation
- ✅ Profile saved to Firestore

---

## 3. Test Scenario 2: New User Registration & Approval

### Create a Test User (Open New Incognito Window)
1. Open new incognito/private browser window
2. Go to `http://localhost:8501`
3. **Email:** testuser@gmail.com
4. **Display Name:** Test User
5. Click **🔐 Sign In**

**Expected Result:**
- ✅ User created in database
- ✅ Shows "Access Denied" page
- ✅ Message: "Your account has been created, but you don't have access..."
- ✅ Contact information displayed
- ✅ "Refresh Access" button visible

### Approve User with Manage Access (Back to Admin Window)
1. Switch to admin window
2. Click **👥 User Management**
3. See statistics showing: Admin: 1, Manage: 0, View Only: 0, Pending: 1
4. Find "Test User (testuser@gmail.com)"
5. Click to expand
6. See: Access Level = "none"
7. Change Access Level dropdown to **"manage"**
8. Click **💾 Update Access**

**Expected Result:**
- ✅ Success message: "Updated testuser@gmail.com to manage access!"
- ✅ User list refreshes
- ✅ Statistics update: Manage: 1, Pending: 0

### Test User Gets Access (Back to Test User Window)
1. Switch to test user window
2. Click **🔄 Refresh Access** button

**Expected Result:**
- ✅ Access granted!
- ✅ Redirected to main app
- ✅ Sidebar shows: "Access: ✏️ Manage"
- ✅ Menu shows manage options:
  - 📚 View Books
  - ➕ Add Book
  - ✏️ Manage Books
  - 📚 Bookshelves
  - 👤 Owners
  - 👤 My Profile
- ✅ No admin-only pages (Book Lending, User Management)
- ✅ Sidebar tip: "✏️ Manage: Can add/edit books"

---

## 4. Test Scenario 3: Book Lending Workflow

### Add a Test Book (As Admin)
1. Click **➕ Add Book**
2. Enter:
   - **Title:** The Great Gatsby
   - Click **🔍 Search** (should auto-fill details)
   - Or enter manually:
     - **Author(s):** F. Scott Fitzgerald
     - **Publisher:** Scribner
     - **Publish Date:** 1925-04-10
3. Click **➕ Add Book**

**Expected Result:**
- ✅ Success message with tracking number
- ✅ Balloons animation
- ✅ Form cleared
- ✅ Book visible in View Books

### Lend the Book
1. Click **📖 Book Lending**
2. Go to **📤 Lend Book** tab
3. Select:
   - **Book:** The Great Gatsby - BK-YYYYMMDD-0001
   - **Borrower:** Test User (testuser@gmail.com)
   - **Due Date:** (default 14 days is fine)
4. Click **📤 Lend Book**

**Expected Result:**
- ✅ Success message: "Book lent successfully"
- ✅ Balloons animation
- ✅ Book disappears from available books list

### Verify Lending Status
1. Click **📚 View Books**
2. Find "The Great Gatsby"

**Expected Result in Table View:**
- ✅ Status column shows: "🔴 Lent to testuser@gmail.com"

**Expected Result in Cards View:**
- ✅ Card title has 🔴 icon
- ✅ Red banner: "🔴 LENT OUT - Borrowed by: testuser@gmail.com on YYYY-MM-DD"

### Check Active Loans
1. Click **📖 Book Lending**
2. Go to **📥 Return Book** tab

**Expected Result:**
- ✅ Shows active loan for "The Great Gatsby"
- ✅ Shows borrower: Test User
- ✅ Shows dates
- ✅ Shows days remaining (should be ~14 days)

### Return the Book
1. In **📥 Return Book** tab
2. Click **📥 Mark as Returned**

**Expected Result:**
- ✅ Success message: "Book returned successfully"
- ✅ Active loans list refreshes (empty now)

### Verify Book Available Again
1. Click **📚 View Books**
2. Find "The Great Gatsby"

**Expected Result:**
- ✅ Status: "🟢 Available"
- ✅ Green banner in cards view: "🟢 AVAILABLE"

### Check Loan History
1. Click **📖 Book Lending**
2. Go to **📊 Loan History** tab

**Expected Result:**
- ✅ Shows 1 loan
- ✅ Status: "✅ Returned"
- ✅ Returned date populated

---

## 5. Test Scenario 4: View-Only Access

### Create View-Only User
1. Admin window → **👥 User Management**
2. Create new user (incognito window):
   - **Email:** viewer@gmail.com
   - **Name:** View Only User
3. Admin approves with access level = **"view"**
4. Viewer logs in

**Expected Result:**
- ✅ Sidebar shows: "Access: 👁️ View Only"
- ✅ Menu shows ONLY:
  - 📚 View Books
  - 👤 My Profile
- ✅ Sidebar tip: "👁️ View: Read-only access"
- ✅ Can view books but no add/edit/delete buttons

---

## 6. Test Scenario 5: Access Control Verification

### Try Accessing Restricted Pages (as View-Only user)
Manually try to access pages by clicking available menu items:

**Expected Results:**
- ✅ View Books: Works ✓
- ✅ My Profile: Works ✓
- ❌ Add Book: Not in menu
- ❌ Manage Books: Not in menu
- ❌ Book Lending: Not in menu
- ❌ User Management: Not in menu

---

## 7. Test Scenario 6: Profile Requirement for Borrowing

### Create User Without Profile
1. Create new user: borrower@gmail.com
2. Admin approves with "full" access
3. Borrower logs in but doesn't complete profile

### Try to Lend Book to User Without Profile (as Admin)
1. Admin → **📖 Book Lending** → **📤 Lend Book**
2. Check **Borrower** dropdown

**Expected Result:**
- ✅ User without profile is NOT in the borrower list
- ✅ Only users with completed profiles appear

### Complete Profile and Retry
1. User completes profile
2. Admin tries lending again

**Expected Result:**
- ✅ User NOW appears in borrower dropdown
- ✅ Can lend book successfully

---

## 8. Test Scenario 7: Overdue Notifications

### Create Overdue Loan (Manual Database Edit)
Since we can't wait 14 days, you can manually edit a loan in Firestore:

1. Firebase Console → Firestore Database
2. Find `book_loans` collection
3. Find an active loan
4. Edit `due_date` field to yesterday's date (e.g., "2025-10-05")
5. Save

### Check Overdue Status
1. App → **📖 Book Lending** → **📥 Return Book**

**Expected Result:**
- ✅ Shows: "⚠️ **OVERDUE by 1 days!**" (in red)

---

## ✅ Testing Checklist

- [ ] Admin login works
- [ ] Admin can complete profile
- [ ] New users get "no access" by default
- [ ] Admin can approve users
- [ ] Approved users can access system
- [ ] View-only users restricted properly
- [ ] Books can be added
- [ ] Books can be lent
- [ ] Lending status shows in View Books
- [ ] Active loans display correctly
- [ ] Books can be returned
- [ ] Loan history tracks properly
- [ ] Overdue status calculates correctly
- [ ] Profile required for borrowing
- [ ] Access control works on all pages
- [ ] Logout works
- [ ] User info shows in sidebar

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError"
**Solution:** Install missing packages:
```bash
python -m pip install streamlit firebase-admin pandas requests
```

### Issue: Firebase connection error
**Solution:** Verify firebase key path in `utils/firebase_utils.py`:
```python
key_path = "D:\\Dropbox\\MySoftware\\Portfolio\\mylibrary-firebase.json"
```

### Issue: User not appearing in borrower list
**Solution:** User must complete profile first (👤 My Profile)

### Issue: Can't lend book
**Solution:**
- Book must not already be lent
- Borrower must have completed profile
- Check that book is in "available" state

### Issue: Access control not working
**Solution:**
- Clear browser cache
- Logout and login again
- Check user's access_level in Firestore

---

## 📊 Expected Database State After Testing

### Collections in Firestore:

**users** (3-4 documents):
- khalid0211@gmail.com (access_level: admin, profile_created: true)
- testuser@gmail.com (access_level: manage, profile_created: true)
- viewer@gmail.com (access_level: view, profile_created: true)
- borrower@gmail.com (access_level: manage, profile_created: true)

**books** (1+ documents):
- The Great Gatsby (is_lent: false after return)
- Other books from previous testing

**book_loans** (1+ documents):
- Loan for The Great Gatsby (returned: true)

**bookshelves** (from previous testing)

**owners** (from previous testing)

---

## 🎉 Success!

If all tests pass, your Library Management System is fully functional with:
- ✅ Authentication
- ✅ Access Control (Admin, Manage, View, None)
- ✅ User Management
- ✅ Book Lending System
- ✅ Loan Tracking
- ✅ Overdue Detection
- ✅ Profile Management

**Ready for production use with Google OAuth upgrade when needed!**
