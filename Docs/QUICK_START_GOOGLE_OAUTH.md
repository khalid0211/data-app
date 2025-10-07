# ⚡ Quick Start: Google OAuth (5 Steps)

Fast setup guide to enable Google Sign-In. For detailed instructions, see `GOOGLE_OAUTH_SETUP.md`.

---

## ✅ You've Already Done:
- ✅ Installed `streamlit-google-auth` package
- ✅ Created `.streamlit/secrets.toml` template
- ✅ Created `utils/google_auth.py` module
- ✅ Created `utils/auth.py` unified auth module

---

## 🚀 What You Need to Do:

### Step 1: Get OAuth Credentials (10 minutes)

**Go to:** https://console.cloud.google.com/apis/credentials

1. **Select project:** mylibrary
2. **Create OAuth 2.0 Client ID:**
   - Click "+ Create Credentials" → "OAuth 2.0 Client ID"
   - Type: Web application
   - Name: Library Management Web Client
   - Authorized JavaScript origins:
     - `http://localhost`
     - `http://localhost:8501`
   - Authorized redirect URIs:
     - `http://localhost:8501`
   - Click Create

3. **Copy credentials:**
   - Client ID: `123...xyz.apps.googleusercontent.com`
   - Client Secret: `GOCSPX-xyz...`

---

### Step 2: Update Secrets File (1 minute)

**Edit:** `F:\Coding\data-app\.streamlit\secrets.toml`

```toml
[google_oauth]
client_id = "PASTE_YOUR_CLIENT_ID_HERE"
client_secret = "PASTE_YOUR_CLIENT_SECRET_HERE"
redirect_uri = "http://localhost:8501"
```

**Save the file.**

---

### Step 3: Update app.py (2 minutes)

**Open:** `F:\Coding\data-app\app.py`

**Find line 11 (near the top):**
```python
from utils.simple_auth import check_authentication, show_user_info_sidebar, can_add_edit_delete, can_view
```

**Replace with:**
```python
from utils.auth import check_authentication, show_user_info_sidebar, can_add_edit_delete, can_view
```

**Find line ~1180 (in main function):**
```python
if not check_authentication(db):
    return
```

**Replace with:**
```python
if not check_authentication():
    return
```

**Save the file.**

---

### Step 4: Run the App (1 minute)

```bash
streamlit run app.py
```

---

### Step 5: Test Login (2 minutes)

1. **Click "Login with Google" button**
2. **Select your Google account**
3. **Grant permissions** (email & profile)
4. **Success!** You're logged in

---

## ⚠️ Common Issues

### Issue: "OAuth Configuration Missing"
**Fix:** Check `.streamlit/secrets.toml` has your real credentials (no quotes, no extra spaces)

### Issue: "Redirect URI Mismatch"
**Fix:** In Google Cloud Console, make sure you added `http://localhost:8501` to **both**:
- Authorized JavaScript origins
- Authorized redirect URIs

### Issue: Can't find OAuth settings
**Fix:**
1. Go to https://console.cloud.google.com/
2. Make sure you're in the **mylibrary** project (dropdown at top)
3. Go to "APIs & Services" → "Credentials"

---

## 📊 What Happens After Login

### Admin (khalid0211@gmail.com):
- ✅ Automatic admin access
- ✅ All 8 menu items visible
- ✅ Can manage users and lend books

### Other Users:
- ⚠️ "Access Denied" message
- 📧 Need approval from admin
- ✅ Can create profile while waiting

---

## 🔄 Switch Back to Temporary Auth

If you need to go back to email/name login:

**Edit:** `utils/auth.py` (line 12)
```python
AUTH_MODE = 'temporary'
```

Restart app.

---

## 📚 Full Documentation

- **Complete Setup Guide:** `GOOGLE_OAUTH_SETUP.md`
- **Troubleshooting:** `GOOGLE_OAUTH_SETUP.md` (Troubleshooting section)
- **Production Deployment:** `GOOGLE_OAUTH_SETUP.md` (Production section)

---

## ✅ Success Criteria

After completing these 5 steps:

- [ ] Secrets file has real Client ID and Secret
- [ ] app.py imports from `utils.auth`
- [ ] App shows "Login with Google" button
- [ ] Can login with Google account
- [ ] khalid0211@gmail.com has admin access
- [ ] Sidebar shows "Access: 🔒 Admin"
- [ ] All menu items visible for admin

---

**Ready to start? Begin with Step 1! 🚀**
