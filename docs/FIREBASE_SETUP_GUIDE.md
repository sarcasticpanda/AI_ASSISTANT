# 🔥 Firebase Setup Guide for Jarvis PDF Storage

This guide will help you set up Firebase for storing PDF files in the cloud.

---

## 📋 What You'll Need

- Google account
- 10-15 minutes
- Terminal access

---

## 🚀 Step 1: Create Firebase Project

1. **Go to Firebase Console**
   - Visit: https://console.firebase.google.com/
   - Click "Add project" (or select existing)

2. **Create New Project**
   - Project name: `jarvis-assistant` (or your choice)
   - Click "Continue"
   - Disable Google Analytics (not needed)
   - Click "Create project"
   - Wait ~30 seconds for setup

3. **Enable Firebase Storage**
   - In left sidebar, click "Build" → "Storage"
   - Click "Get started"
   - Select "Start in production mode"
   - Choose location: `us-central1` (or nearest to you)
   - Click "Done"

---

## 🔑 Step 2: Get Service Account Key

1. **Open Project Settings**
   - Click gear icon ⚙️ (top-left, next to "Project Overview")
   - Select "Project settings"

2. **Go to Service Accounts**
   - Click "Service accounts" tab
   - Click "Generate new private key"
   - Click "Generate key" in popup
   - **IMPORTANT**: Save the JSON file securely!

3. **Rename and Move File**
   ```powershell
   # Rename to something simple
   # Move to your project root
   mv C:\Users\<YourName>\Downloads\jarvis-assistant-*.json C:\Users\Lunar` Panda\3-Main\assistant\firebase-credentials.json
   ```

4. **Add to .gitignore** (CRITICAL - don't commit to Git!)
   ```
   firebase-credentials.json
   ```

---

## 📦 Step 3: Install Python SDK

Open your PowerShell terminal in the project directory:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install Firebase Admin SDK
pip install firebase-admin

# Verify installation
python -c "import firebase_admin; print('✅ Firebase Admin installed!')"
```

---

## ✅ Step 4: Test Firebase Connection

Create a test file `test_firebase_connection.py`:

```python
import firebase_admin
from firebase_admin import credentials, storage
import os

# Path to your service account key
cred_path = "firebase-credentials.json"

if not os.path.exists(cred_path):
    print("❌ Credentials file not found!")
    print(f"   Looking for: {os.path.abspath(cred_path)}")
    exit(1)

try:
    # Initialize Firebase
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'jarvis-assistant.appspot.com'  # Replace with your project ID
    })
    
    # Get bucket
    bucket = storage.bucket()
    
    print("✅ Firebase connected successfully!")
    print(f"   Bucket: {bucket.name}")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```powershell
python test_firebase_connection.py
```

---

## 🔧 Step 5: Set Up Security Rules

1. **Go to Storage Rules**
   - Firebase Console → Storage → Rules tab

2. **Update Rules** (allow authenticated access):
   ```javascript
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /{allPaths=**} {
         // Allow read/write for all (change later for production)
         allow read, write: if true;
       }
     }
   }
   ```

3. **Publish Rules**
   - Click "Publish"

---

## 📂 Step 6: Create Firebase Manager

I'll create `backend/core/firebase_manager.py` with these functions:

```python
def initialize(credentials_path: str) -> bool:
    """Initialize Firebase with credentials"""
    
def upload_pdf(file_path: str, filename: str = None) -> str:
    """Upload PDF to Firebase Storage, return download URL"""
    
def download_pdf(url: str, save_path: str) -> str:
    """Download PDF from Firebase to local path"""
    
def delete_pdf(filename: str) -> bool:
    """Delete PDF from Firebase Storage"""
    
def list_pdfs() -> list:
    """List all PDFs in storage"""
```

---

## 🎯 Step 7: Integration Plan

**MongoDB** (local storage):
- User queries
- PDF metadata (filename, firebase_url, summary)
- Conversation history
- Voice commands
- App/website opens

**Firebase** (cloud storage):
- PDF files (binary data)
- Large media files
- Optional: TTS audio cache

**Workflow**:
1. User uploads PDF → Save to Firebase → Get URL
2. Extract text from PDF
3. Generate summary (DeepSeek R1 via OpenRouter)
4. Store in MongoDB:
   ```json
   {
     "filename": "AI_Research.pdf",
     "firebase_url": "https://firebasestorage.googleapis.com/...",
     "summary": "This PDF discusses...",
     "uploaded_at": "2025-11-05T13:09:00Z",
     "questions_asked": []
   }
   ```

---

## 🧪 Step 8: Test Upload/Download

After I create `firebase_manager.py`, test with:

```python
from backend.core import firebase_manager

# Initialize
firebase_manager.initialize("firebase-credentials.json")

# Upload PDF
url = firebase_manager.upload_pdf("test.pdf")
print(f"Uploaded to: {url}")

# Download PDF
firebase_manager.download_pdf(url, "downloaded_test.pdf")
print("Downloaded successfully!")
```

---

## 📊 Expected Storage Costs

Firebase Storage pricing (as of 2025):
- **FREE tier**: 5 GB storage, 1 GB/day download
- **Paid**: $0.026/GB storage, $0.12/GB download

For 100 PDFs (~500 MB total): **FREE!** 🎉

---

## 🔒 Security Best Practices

1. **Never commit credentials** to Git:
   ```gitignore
   firebase-credentials.json
   *.json  # Be careful with this
   ```

2. **Use environment variables** (optional):
   ```python
   import os
   cred_path = os.getenv("FIREBASE_CRED_PATH", "firebase-credentials.json")
   ```

3. **Update security rules** for production:
   ```javascript
   // Only allow authenticated users
   allow read, write: if request.auth != null;
   ```

---

## 🐛 Troubleshooting

**Error: "Bucket not found"**
- Check project ID in Firebase Console
- Ensure Storage is enabled
- Update bucket name in code

**Error: "Permission denied"**
- Check security rules (allow read, write: if true)
- Verify service account has "Storage Admin" role

**Error: "Credentials file not found"**
- Check file path is correct
- Ensure file is in project root
- Use absolute path if needed

---

## ✅ Checklist

Before proceeding:
- [ ] Firebase project created
- [ ] Storage enabled
- [ ] Service account key downloaded
- [ ] Credentials file saved in project root
- [ ] Added to .gitignore
- [ ] Firebase Admin SDK installed
- [ ] Connection test passed
- [ ] Security rules updated

---

## 🎉 Next Steps

Once Firebase is set up:
1. I'll create `firebase_manager.py`
2. We'll test PDF upload/download
3. Integrate with MongoDB for metadata
4. Build PDF summarization (Phase 2)
5. Connect to Jarvis voice commands

**Ready to proceed?** Let me know when Firebase is set up and I'll create the manager code!
