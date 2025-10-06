# 🔐 Google OAuth Setup Guide

Complete step-by-step guide to enable Google Sign-In for your Library Management System.

---

## 📋 Prerequisites

- ✅ Firebase project created (mylibrary)
- ✅ Google account (khalid0211@gmail.com)
- ✅ Application already using Firebase Firestore

---

## Step 1: Enable Google Sign-In in Firebase

### 1.1 Open Firebase Console
1. Go to https://console.firebase.google.com/
2. Select your project: **mylibrary**

### 1.2 Enable Google Authentication
1. In the left sidebar, click **"Authentication"**
2. Click **"Get Started"** (if first time)
3. Go to **"Sign-in method"** tab
4. Find **"Google"** in the providers list
5. Click on **"Google"**
6. Toggle **"Enable"** switch to ON
7. Select **"Project support email"**: khalid0211@gmail.com
8. Click **"Save"**

✅ **Checkpoint:** Google should now show as "Enabled" in the sign-in methods

---

## Step 2: Create OAuth Client ID in Google Cloud Console

### 2.1 Access Google Cloud Console
1. Go to https://console.cloud.google.com/
2. Make sure you're in the same project as Firebase (mylibrary)
3. If not, click project dropdown at top and select **mylibrary**

### 2.2 Enable Google+ API (if not already enabled)
1. Go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"**
3. Click on it and click **"Enable"**
4. Wait for it to enable (~1 minute)

### 2.3 Configure OAuth Consent Screen
1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"Internal"** if this is for your organization only
   - OR **"External"** if anyone with a Google account can sign in
3. Click **"Create"**

4. **Fill in App Information:**
   - App name: `Library Management System`
   - User support email: `khalid0211@gmail.com`
   - App logo: (optional, skip for now)

5. **App domain** (optional for testing):
   - Skip for now, add later for production

6. **Developer contact information:**
   - Email: `khalid0211@gmail.com`

7. Click **"Save and Continue"**

8. **Scopes:** Click **"Add or Remove Scopes"**
   - Check: `../auth/userinfo.email`
   - Check: `../auth/userinfo.profile`
   - Check: `openid`
   - Click **"Update"**
   - Click **"Save and Continue"**

9. **Test users** (if using External):
   - Click **"Add Users"**
   - Add: `khalid0211@gmail.com`
   - Add any other test users
   - Click **"Save and Continue"**

10. Click **"Back to Dashboard"**

### 2.4 Create OAuth 2.0 Client ID
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth 2.0 Client ID"**

3. **Application type:** Select **"Web application"**

4. **Name:** `Library Management Web Client`

5. **Authorized JavaScript origins:**
   - Click **"+ Add URI"**
   - Add: `http://localhost`
   - Click **"+ Add URI"** again
   - Add: `http://localhost:8501`

6. **Authorized redirect URIs:**
   - Click **"+ Add URI"**
   - Add: `http://localhost:8501`

7. Click **"Create"**

8. **IMPORTANT:** A popup will show your credentials:
   - **Client ID**: Something like `123456789-abc...xyz.apps.googleusercontent.com`
   - **Client Secret**: Something like `GOCSPX-abc...xyz`
   - **Copy both** - you'll need them in the next step!

✅ **Checkpoint:** You should have Client ID and Client Secret saved

---

## Step 3: Configure Streamlit Secrets

### 3.1 Open the Secrets File
Navigate to: `F:\Coding\data-app\.streamlit\secrets.toml`

### 3.2 Update with Your Credentials
Replace the placeholder values:

```toml
[google_oauth]
client_id = "YOUR_CLIENT_ID_HERE"
client_secret = "YOUR_CLIENT_SECRET_HERE"
redirect_uri = "http://localhost:8501"
```

**Example (with fake credentials):**
```toml
[google_oauth]
client_id = "123456789-abcdefghijklmnop.apps.googleusercontent.com"
client_secret = "GOCSPX-abcdefghijklmnop"
redirect_uri = "http://localhost:8501"
```

### 3.3 Save and Secure
1. Save the file
2. **NEVER commit this file to Git!**
3. Check that `.streamlit/secrets.toml` is in your `.gitignore`

✅ **Checkpoint:** Secrets file contains your real Client ID and Secret

---

## Step 4: Update Application Code

### 4.1 Switch to Google OAuth Mode
Open: `F:\Coding\data-app\utils\auth.py`

Find this line (around line 12):
```python
AUTH_MODE = 'google'  # Change to 'temporary' to use simple email/name login
```

**It should already be set to `'google'`**

If it says `'temporary'`, change it to `'google'`.

### 4.2 Update app.py to Use New Auth Module
Open: `F:\Coding\data-app\app.py`

**Find this line (at the top):**
```python
from utils.simple_auth import check_authentication, show_user_info_sidebar, can_add_edit_delete, can_view
```

**Replace with:**
```python
from utils.auth import check_authentication, show_user_info_sidebar, can_add_edit_delete, can_view
```

**Find this line (in main function):**
```python
if not check_authentication(db):
    return
```

**Replace with:**
```python
if not check_authentication():
    return
```

### 4.3 Save Changes
Save `app.py`

✅ **Checkpoint:** Application configured to use Google OAuth

---

## Step 5: Test Google Sign-In

### 5.1 Run the Application
```bash
cd F:\Coding\data-app
streamlit run app.py
```

### 5.2 Expected Behavior
1. **Login Page Appears:**
   - Should show "Library Management System" header
   - Should show "Sign in with Google" heading
   - Should show blue "Login with Google" button

2. **Click "Login with Google":**
   - Opens Google Sign-In popup
   - Lists available Google accounts
   - Select your account (e.g., khalid0211@gmail.com)

3. **Grant Permissions:**
   - Google asks to access email and profile
   - Click **"Allow"** or **"Continue"**

4. **Successful Login:**
   - Redirects back to application
   - Creates user in Firestore database
   - khalid0211@gmail.com gets admin access automatically
   - Other users get "no access" and must be approved

### 5.3 Verify in Firebase
1. Go to Firebase Console → Firestore Database
2. Open `users` collection
3. Should see your user document with:
   - `email`: your@gmail.com
   - `display_name`: Your Name
   - `access_level`: 'admin' (if khalid0211@gmail.com) or 'none' (others)

✅ **Checkpoint:** Successfully logged in with Google account

---

## Step 6: Test Complete Flow

### 6.1 Test as Admin
1. Login as khalid0211@gmail.com
2. ✅ Should see "Access: 🔒 Admin" in sidebar
3. ✅ Should see all 8 menu items
4. ✅ Can access User Management
5. ✅ Can access Book Lending

### 6.2 Test as New User
1. Open **Incognito/Private Window**
2. Go to http://localhost:8501
3. Click "Login with Google"
4. Sign in with different Google account
5. ✅ Should see "Access Denied" page
6. ✅ Message says to contact khalid0211@gmail.com

### 6.3 Test User Approval
1. Back to admin window
2. Go to **👥 User Management**
3. Find the new user
4. Change access to **'manage'** or **'view'**
5. Click **💾 Update Access**
6. ✅ Statistics update
7. New user refreshes page
8. ✅ Now has access!

✅ **Checkpoint:** Complete authentication flow working

---

## Troubleshooting

### Issue: "OAuth Configuration Missing" Error
**Cause:** Secrets file not found or has wrong format

**Solution:**
1. Check file exists: `F:\Coding\data-app\.streamlit\secrets.toml`
2. Check syntax is correct (see Step 3.2)
3. Restart Streamlit app

### Issue: "Invalid Client ID" from Google
**Cause:** Wrong Client ID in secrets or wrong project

**Solution:**
1. Double-check Client ID from Google Cloud Console
2. Make sure you copied the full ID (ends with `.apps.googleusercontent.com`)
3. No extra spaces or quotes in secrets file

### Issue: "Redirect URI Mismatch"
**Cause:** Authorized Redirect URI not configured correctly

**Solution:**
1. Go to Google Cloud Console → Credentials
2. Click on your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", verify you have:
   - `http://localhost:8501`
4. Save changes
5. Wait 5 minutes for changes to propagate
6. Try again

### Issue: "Access Blocked" from Google
**Cause:** OAuth consent screen not configured

**Solution:**
1. Complete Step 2.3 (Configure OAuth Consent Screen)
2. Add test users if using "External" type
3. Or switch to "Internal" if within organization

### Issue: Login Works but User Has No Access
**Cause:** This is correct behavior for non-admin users

**Solution:**
1. Login as khalid0211@gmail.com (admin)
2. Go to User Management
3. Approve the user
4. Set appropriate access level

### Issue: Can't See Menu Items After Login
**Cause:** Access level not loaded correctly

**Solution:**
1. Check Firestore - is user's `access_level` set correctly?
2. Logout and login again
3. Check session state in Streamlit (use st.write(st.session_state))

---

## Production Deployment

### Update for Production Domain

When deploying to production (e.g., Streamlit Cloud, your own server):

1. **Google Cloud Console:**
   - Add production domain to Authorized JavaScript origins
   - Add production domain to Authorized redirect URIs
   - Example: `https://yourapp.streamlit.app`

2. **Streamlit Secrets (Production):**
   - If using Streamlit Cloud: Add secrets in app settings
   - If using own server: Update `.streamlit/secrets.toml` with production URIs

3. **OAuth Consent Screen:**
   - Add production domain under "App domain"
   - Submit for verification if using "External" type

4. **Test Thoroughly:**
   - Test login from production URL
   - Test all user access levels
   - Test logout and re-login

---

## Security Best Practices

1. **Never Commit Secrets:**
   - Add `.streamlit/secrets.toml` to `.gitignore`
   - Never put credentials in code

2. **Rotate Credentials Regularly:**
   - Create new OAuth Client ID periodically
   - Update secrets and retire old credentials

3. **Monitor User Access:**
   - Regularly review User Management page
   - Remove access for inactive users
   - Audit admin user list

4. **Use HTTPS in Production:**
   - Always use HTTPS for production
   - Update redirect URIs accordingly

5. **Limit OAuth Scopes:**
   - Only request email and profile scopes
   - Don't request unnecessary permissions

---

## Switching Back to Temporary Auth (Testing)

If you need to switch back to temporary authentication:

**In `utils/auth.py`, change:**
```python
AUTH_MODE = 'temporary'
```

**In `app.py`, change imports back to:**
```python
from utils.simple_auth import check_authentication, show_user_info_sidebar, can_add_edit_delete, can_view
```

Restart the app.

---

## ✅ Success Checklist

- [ ] Firebase Authentication enabled for Google
- [ ] Google Cloud OAuth consent screen configured
- [ ] OAuth 2.0 Client ID created
- [ ] Client ID and Secret saved in `.streamlit/secrets.toml`
- [ ] `AUTH_MODE = 'google'` in `utils/auth.py`
- [ ] App imports from `utils.auth` instead of `utils.simple_auth`
- [ ] Successfully logged in with khalid0211@gmail.com
- [ ] Admin sees all menu items and features
- [ ] Created test user and tested approval flow
- [ ] New user gets access after admin approval
- [ ] Logout works correctly

---

## 🎉 Congratulations!

Your Library Management System now uses **production-ready Google OAuth** authentication!

**Benefits:**
- ✅ Secure authentication via Google
- ✅ No passwords to manage
- ✅ Familiar Google login flow
- ✅ Real user verification
- ✅ Professional authentication system

**Next Steps:**
- Add more users via User Management
- Set appropriate access levels for each user
- Test all features with different access levels
- Prepare for production deployment (if applicable)

For questions or issues, contact: khalid0211@gmail.com
