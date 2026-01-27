# Data Management System - Quick Reference

## 🚀 Quick Access

### From Admin Dashboard
1. Go to: `http://127.0.0.1:8000/admin/`
2. Click purple card: **"Open Data Management →"**

### From Top Menu
1. Click **"Data Management"** in navigation bar (any admin page)

### Direct URL
```
http://127.0.0.1:8000/admin/deletedata/examdatacleanup/
```

## 🗑️ Operations

### Delete Exam Data
**What it does:** Removes all exam-related data, keeps users
**Confirmation:** 3 steps (type "DELETE EXAM DATA")
**Preserves:** Users, Profiles, Centers

### Delete Everything  
**What it does:** Complete system reset
**Confirmation:** 2 steps (just click OK - NO TYPING!)
**Preserves:** Admin accounts ONLY
**Includes:** Centers table (centers_center)

## 📊 What Gets Deleted

| Item | Delete Exam Data | Delete Everything |
|------|------------------|-------------------|
| Questions & Papers | ✅ | ✅ |
| Exam Sessions | ✅ | ✅ |
| Candidate Answers | ✅ | ✅ |
| Question Uploads | ✅ | ✅ |
| User Registrations | ❌ | ✅ |
| Candidate Profiles | ❌ | ✅ |
| Exam Centers | ❌ | ✅ |
| Admin Accounts | ❌ | ❌ |

## 💻 CLI Commands

```bash
# Dry run (test mode)
python manage.py cleanup_exam_data --level=exam-data --dry-run --debug
python manage.py cleanup_exam_data --level=everything --dry-run --debug

# Execute
python manage.py cleanup_exam_data --level=exam-data --confirm --debug
python manage.py cleanup_exam_data --level=everything --confirm --debug
```

## ⚠️ Important

- ✅ Always backup database first
- ✅ Operations are permanent
- ✅ Admin accounts always preserved
- ✅ Debug logging enabled
- ✅ Transaction safety built-in

## 🎨 UI Features

- Professional Django admin theme
- Card-based layout
- Color-coded operations (Orange/Red)
- Loading spinners
- Clear warnings
- Breadcrumb navigation

## Status: ✅ READY
