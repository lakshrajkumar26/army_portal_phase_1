# First Time Setup Commands

## Prerequisites
Make sure you have Python and pip installed on your system.

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Database Setup
```bash
# Run database migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

## Step 3: Initialize System Data
```bash
# Run the comprehensive first-time setup script
python first_time_setup.py
```

This script will:
- Initialize GlobalPaperTypeControl settings
- Create UniversalSetActivation records
- Set up default ActivateSets (Set A, Set B, Set C)
- Create default question paper configurations
- Initialize system defaults

## Step 4: Create PO Users (if needed)
```bash
# Create PO admin users
python manage.py create_po_user
```

## Step 5: Start the Server
```bash
# Start Django development server
python manage.py runserver
```

## Alternative: Quick Setup Script
If you encounter any template or database issues on a new PC, run:
```bash
# Fix template errors and initialize database
python fix_new_pc_setup.py
```

## Troubleshooting Commands

### If you see template errors:
```bash
python fix_template_errors.py
```

### If you need to clear Django cache:
```bash
python clear_django_cache.py
```

### If you need to restart server cleanly:
```bash
python restart_clean_server.py
```

### If you need to manage logging levels:
```bash
python manage_logging.py
```

## Admin Access
After setup, access the admin interface at:
- URL: http://127.0.0.1:8000/admin/
- Login with the superuser credentials you created

## Important Notes
1. Always run `python manage.py migrate` first on a new PC
2. Run `python first_time_setup.py` to initialize system data
3. The system uses MySQL database (not MongoDB)
4. Make sure your `.env` file is properly configured
5. For production, use the `.env.production` file as reference

## Role-Based Access
- **Superuser**: Full access to all features
- **PO_ADMIN**: Can edit marks and export data, no slot management
- **CENTER_ADMIN**: Can manage slots, no marks editing or sensitive exports