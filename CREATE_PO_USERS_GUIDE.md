# Create PO Users - Quick Guide

## ✅ FIXED - Now Working!

## Method 1: Using Batch File (Easiest)

1. Double-click `create_po.bat`
2. Enter username (e.g., `po_user1`)
3. Enter password (e.g., `SecurePass123`)
4. Enter email (optional, press Enter to skip)
5. Enter first name (optional, press Enter to skip)
6. Enter last name (optional, press Enter to skip)
7. Done! ✅

## Method 2: Using Command Line

```bash
# Basic PO user
python manage.py create_po_user --username=po_user1 --password=SecurePass123

# With email and name
python manage.py create_po_user --username=po_user1 --password=SecurePass123 --email=po@example.com --first-name=John --last-name=Doe
```

## Method 3: Using Django Admin

1. Go to: `http://127.0.0.1:8000/admin/`
2. Login as superuser
3. Click "Users" under "Accounts"
4. Click "Add User" button
5. Fill in:
   - Username: `po_user1`
   - Password: `SecurePass123`
   - Confirm password: `SecurePass123`
6. Click "Save and continue editing"
7. Set permissions:
   - ✅ Check "Staff status" (allows admin access)
   - ❌ Leave "Superuser status" unchecked
   - Role: Select "PO Admin"
8. Click "Save"

## Quick Test

```bash
# Create a test PO user
python manage.py create_po_user --username=PO --password=PO

# Login at: http://127.0.0.1:8000/admin/
# Username: PO
# Password: PO
```

## Login

**URL:** `http://127.0.0.1:8000/admin/`

**Test Credentials:**
- Username: `PO`
- Password: `PO`

## PO User Details

- ✅ Role: PO_ADMIN
- ✅ Can access admin panel
- ✅ Can manage candidates
- ✅ Can view exam data
- ✅ Can assign exam slots
- ❌ Cannot delete everything
- ❌ Not a superuser

## Quick Examples

```bash
# Create simple PO user
python manage.py create_po_user --username=john_po --password=John@2024

# Create PO user with full details
python manage.py create_po_user --username=mary_po --password=Mary@2024 --email=mary@army.mil --first-name=Mary --last-name=Smith

# Create multiple PO users quickly
python manage.py create_po_user --username=po1 --password=Pass123
python manage.py create_po_user --username=po2 --password=Pass456
python manage.py create_po_user --username=po3 --password=Pass789
```

## Available Options

```bash
--username USERNAME     Username for the PO user (required)
--password PASSWORD     Password for the PO user (required)
--email EMAIL          Email for the PO user (optional)
--first-name FIRST_NAME First name of the PO (optional)
--last-name LAST_NAME   Last name of the PO (optional)
```

## Troubleshooting

**Error: User already exists**
- Choose a different username

**Error: Command not found**
- Make sure you're in the project directory
- Check that `accounts/management/commands/create_po_user.py` exists

**Can't login**
- Verify username and password
- Make sure "Staff status" is checked
- Clear browser cache and try again

## Status: ✅ WORKING PERFECTLY
