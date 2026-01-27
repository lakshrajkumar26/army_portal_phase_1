# PO User - Quick Start

## ✅ WORKING - Create PO User

### Super Quick Method
```bash
python manage.py create_po_user --username=PO --password=PO
```

### With Details
```bash
python manage.py create_po_user --username=john_po --password=SecurePass123 --email=john@army.mil --first-name=John --last-name=Doe
```

### Using Batch File
```bash
# Double-click: create_po.bat
# Enter details when prompted
```

## Login
```
URL: http://127.0.0.1:8000/admin/
Username: PO
Password: PO
```

## PO User Features
- ✅ Role: PO_ADMIN
- ✅ Can access admin panel
- ✅ Staff status enabled
- ❌ Not superuser (safe)

## Test User Created
A test PO user has been created:
- **Username:** PO
- **Password:** PO
- **Role:** PO_ADMIN

Ready to login! ✅