# 🔐 Authentication Setup Guide for Library Management System

## Overview
This guide will help you implement Google Authentication using Firebase Authentication, along with user access control and book lending features.

---

## 📋 Table of Contents
1. [Firebase Authentication Setup](#1-firebase-authentication-setup)
2. [Required Python Packages](#2-required-python-packages)
3. [Firebase Configuration](#3-firebase-configuration)
4. [Database Schema Changes](#4-database-schema-changes)
5. [Implementation Components](#5-implementation-components)
6. [Testing the Setup](#6-testing-the-setup)

---

## 1. Firebase Authentication Setup

### Step 1.1: Enable Firebase Authentication
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (mylibrary)
3. In the left sidebar, click **"Authentication"**
4. Click **"Get Started"** if this is your first time
5. Go to the **"Sign-in method"** tab

### Step 1.2: Enable Google Sign-In Provider
1. Click on **"Google"** in the list of providers
2. Click the **"Enable"** toggle switch
3. Select a **"Project support email"** (use khalid0211@gmail.com)
4. Click **"Save"**

### Step 1.3: Get Firebase Web Configuration
1. In Firebase Console, click the **gear icon** ⚙️ (Project Settings)
2. Scroll down to **"Your apps"** section
3. If you don't have a web app, click **"Add app"** and select the **Web icon** (</>)
4. Register the app (name it "Library Management Web")
5. Copy the **firebaseConfig** object - it looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "mylibrary-xxxxx.firebaseapp.com",
  projectId: "mylibrary-xxxxx",
  storageBucket: "mylibrary-xxxxx.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:xxxxx"
};
```

### Step 1.4: Set Authorized Domains
1. In Firebase Console → Authentication → Settings
2. Under **"Authorized domains"**, add:
   - `localhost` (for local development)
   - Your production domain (if deploying)

---

## 2. Required Python Packages

### Install Additional Packages

```bash
pip install streamlit-authenticator
pip install pyrebase4
pip install python-jwt
```

**OR** update your requirements.txt:

```
streamlit
firebase-admin
pandas
requests
pyrebase4
streamlit-authenticator
python-jwt
```

Then run:
```bash
pip install -r requirements.txt
```

---

## 3. Firebase Configuration

### Step 3.1: Create Firebase Config File

Create a new file: `F:\Coding\data-app\config\firebase_config.json`

```json
{
  "apiKey": "YOUR_API_KEY",
  "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
  "databaseURL": "https://YOUR_PROJECT_ID.firebaseio.com",
  "projectId": "YOUR_PROJECT_ID",
  "storageBucket": "YOUR_PROJECT_ID.appspot.com",
  "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
  "appId": "YOUR_APP_ID"
}
```

**Replace the placeholders with values from Step 1.3**

### Step 3.2: Secure Your Config File

Add to `.gitignore`:
```
config/firebase_config.json
*.json
```

**⚠️ IMPORTANT:** Never commit this file to GitHub!

---

## 4. Database Schema Changes

### New Collections to Create in Firestore

#### 4.1 **users** Collection
```javascript
{
  "email": "user@example.com",
  "gmail_id": "user@gmail.com",
  "display_name": "John Doe",
  "access_level": "none", // "full", "view", "none"
  "profile_created": true,
  "full_name": "John Doe",
  "cell_phone": "+1234567890",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T00:00:00Z",
  "approved_by": "khalid0211@gmail.com",
  "approved_at": "2024-01-01T00:00:00Z"
}
```

**Access Levels:**
- `full` - Can Add, Edit, Delete books
- `view` - Can only view books
- `none` - No access (default for new users)

#### 4.2 **book_loans** Collection
```javascript
{
  "book_id": "firestore_book_id",
  "tracking_number": "BK-20240101-0001",
  "borrowed_by_email": "user@gmail.com",
  "borrowed_by_name": "John Doe",
  "borrowed_date": "2024-01-01",
  "due_date": "2024-01-15",
  "returned": false,
  "returned_date": null,
  "approved_by": "khalid0211@gmail.com"
}
```

#### 4.3 Update **books** Collection
Add new fields to existing books:
```javascript
{
  // ... existing fields ...
  "is_lent": false,
  "lent_to": "",
  "lent_date": "",
  "lent_by": ""
}
```

---

## 5. Implementation Components

### 5.1 File Structure
```
F:\Coding\data-app\
├── app.py                          # Main application (updated)
├── config/
│   └── firebase_config.json        # Firebase web config (NEW)
├── utils/
│   ├── firebase_utils.py           # Firestore operations (updated)
│   ├── auth_utils.py               # Authentication helpers (NEW)
│   └── book_api.py                 # Google Books API (existing)
└── AUTHENTICATION_SETUP_GUIDE.md   # This file
```

### 5.2 Key Features to Implement

#### A. Authentication Flow
1. User visits app → sees Google Sign-In button
2. User signs in with Google
3. System checks if user exists in `users` collection
4. If new user:
   - Create user record with `access_level: "none"`
   - Show "Contact Dr. Khalid Ahmad Khan for access"
5. If existing user:
   - Check `access_level`
   - Grant appropriate permissions

#### B. Admin User (khalid0211@gmail.com)
- Hardcoded full access
- Can see "👥 User Management" page
- Can approve/deny user access
- Can change user access levels
- Can manage book loans

#### C. User Profile
- After first login, user creates profile:
  - Full Name
  - Cell Phone
  - Email (auto-populated from Google)
- Profile required before requesting books

#### D. Book Lending
- Admin can lend books to authenticated users
- Track who borrowed what and when
- Mark books as "Lent Out" in views
- Return process (toggle off lent status)

#### E. Access Control Checks
- **Full Access Users:**
  - See: Add Book, Edit Book, Delete Book, Lend Book
  - Can perform all operations

- **View Only Users:**
  - See: View Books only
  - Cannot add, edit, or delete

- **No Access Users:**
  - See: Access denied message
  - Instruction to contact admin

---

## 6. Testing the Setup

### Phase 1: Authentication Only
1. Enable Firebase Authentication (Step 1)
2. Install packages (Step 2)
3. Add Firebase config (Step 3)
4. Test Google Sign-In
5. Verify user creation in Firestore

### Phase 2: Access Control
1. Sign in as khalid0211@gmail.com (should have full access)
2. Sign in as different user (should have no access)
3. Use admin panel to grant access
4. Verify access changes work

### Phase 3: Book Lending
1. Create user profiles
2. Test lending books
3. Test returning books
4. Verify loan history

---

## 🚀 Next Steps

### After completing this guide:

**Option 1: Manual Implementation**
- Use this guide to set up Firebase Authentication yourself
- Let me know when ready, and I'll provide the code

**Option 2: Guided Implementation**
- Complete Steps 1-3 above
- Share your Firebase config (I'll help integrate it)
- I'll implement all features step-by-step

**Option 3: Full Implementation**
- I can create all the code NOW with placeholder configs
- You complete the Firebase setup
- Replace placeholders with your actual config
- Test and verify

---

## 📞 Support

If you encounter issues:
1. Check Firebase Console for error messages
2. Verify all packages are installed
3. Ensure firebase_config.json has correct values
4. Check Firestore security rules allow authenticated access

---

## 🔒 Security Considerations

1. **Never commit credentials to Git**
   - Use `.gitignore` for config files
   - Use environment variables for production

2. **Firestore Security Rules**
   - Only authenticated users can read
   - Only admin can write to users collection
   - Only full access users can write to books

3. **Admin Email Verification**
   - Hardcode admin email in code
   - Don't store admin status in database (can be modified)

---

## ⏭️ What Would You Like to Do Next?

**A)** Complete Steps 1-3, then I'll provide the implementation code
**B)** I'll create the code now with placeholders, you fill in config later
**C)** You need help with a specific step in this guide

Please let me know how you'd like to proceed!
