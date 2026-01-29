# New PC Setup Guide - Django Exam Portal

## 🔍 **Problem Analysis**

When running the Django Exam Portal on a new PC, you encountered:

1. **Template Variable Errors**:
   - `VariableDoesNotExist: Failed lookup for key [filter_input_length]`
   - `VariableDoesNotExist: Failed lookup for key [dark_mode_theme]`

2. **Empty Admin Pages**:
   - Activate Sets page showing nothing
   - Secondary questions not appearing

3. **Database Issues**:
   - Missing initial data after migration
   - Uninitialized system records

## 🔧 **Root Causes**

### 1. Missing Admin Attributes
- `QuestionAdmin` and `ActivateSetsAdmin` classes missing `filter_input_length` attribute
- Jazzmin theme expecting variables that don't exist in context

### 2. Database Initialization
- Fresh database missing required system records
- No `GlobalPaperTypeControl` records
- No `UniversalSetActivation` records  
- No `ActivateSets` records for trades

### 3. Template Context Issues
- Jazzmin theme templates expecting specific context variables
- Missing theme configuration in settings

## ✅ **Solutions Implemented**

### 1. Fixed Admin Classes
```python
# Added to QuestionAdmin and ActivateSetsAdmin
filter_input_length = 10  # Fix template variable error
```

### 2. Enhanced Jazzmin Configuration
```python
JAZZMIN_SETTINGS = {
    # ... comprehensive theme settings
    "dark_mode_theme": None,  # Fix template error
}

JAZZMIN_UI_TWEAKS = {
    # ... UI settings with proper defaults
    "dark_mode_theme": None,  # Fix template error
}
```

### 3. Database Initialization Scripts
- `fix_new_pc_setup.py` - Complete database initialization
- `fix_template_errors.py` - Quick template error fixes
- `first_time_setup.py` - Complete first-time setup

## 🚀 **Quick Fix Commands**

### **Option 1: Complete First-Time Setup (Recommended)**
```bash
# Run complete setup (includes everything)
python first_time_setup.py
```

### **Option 2: Quick Template Fix Only**
```bash
# Fix just the template errors
python fix_template_errors.py

# Restart server
python restart_clean_server.py
```

### **Option 3: Manual Step-by-Step**
```bash
# 1. Fix template errors
python fix_template_errors.py

# 2. Run migrations
python manage.py migrate

# 3. Initialize system data
python fix_new_pc_setup.py

# 4. Set clean logging
python manage_logging.py set INFO

# 5. Start server
python restart_clean_server.py
```

## 📋 **What Each Script Does**

### `first_time_setup.py`
- ✅ Checks and installs requirements
- ✅ Sets up environment variables
- ✅ Runs database migrations
- ✅ Initializes all system data
- ✅ Fixes template errors
- ✅ Creates superuser
- ✅ Starts clean server

### `fix_template_errors.py`
- ✅ Adds missing Jazzmin configuration
- ✅ Initializes required database records
- ✅ Fixes `dark_mode_theme` and `filter_input_length` errors

### `fix_new_pc_setup.py`
- ✅ Runs database migrations
- ✅ Initializes `GlobalPaperTypeControl`
- ✅ Initializes `UniversalSetActivation`
- ✅ Initializes `ActivateSets` for all trades
- ✅ Checks question data integrity

## 🔄 **After Setup Steps**

### 1. Upload Questions
1. Go to **Admin > Questions > 1 QP Upload**
2. Upload your Excel/CSV file with questions
3. Verify questions appear in **Questions > 3 QP Delete**

### 2. Configure Question Sets
1. Go to **Admin > Questions > Activate Sets**
2. Select **PRIMARY** or **SECONDARY** paper type
3. Choose question sets for each trade
4. Set exam duration

### 3. Verify Setup
1. Check that **Activate Sets** page shows all trades
2. Verify questions are categorized correctly
3. Test exam interface with a candidate

## 🐛 **Troubleshooting**

### Still Getting Template Errors?
```bash
# Clear Django cache and restart
python clear_django_cache.py
python restart_clean_server.py
```

### Activate Sets Page Empty?
```bash
# Re-initialize system data
python fix_new_pc_setup.py
```

### Questions Not Showing?
```bash
# Check question data
python manage.py shell
>>> from questions.models import Question
>>> print(f"Total questions: {Question.objects.count()}")
>>> print(f"PRIMARY: {Question.objects.filter(paper_type='PRIMARY').count()}")
>>> print(f"SECONDARY: {Question.objects.filter(paper_type='SECONDARY').count()}")
```

### Database Connection Issues?
1. Check `.env` file database settings:
   ```
   DB_NAME=exam_portal
   DB_USER=root
   DB_PASSWORD=root
   DB_HOST=localhost
   DB_PORT=3306
   ```
2. Ensure MySQL server is running
3. Create database if it doesn't exist:
   ```sql
   CREATE DATABASE exam_portal;
   ```

## 📁 **Files Modified/Created**

### Modified Files:
- `questions/admin.py` - Added `filter_input_length` attributes
- `config/settings.py` - Enhanced Jazzmin configuration

### New Files:
- `first_time_setup.py` - Complete setup script
- `fix_new_pc_setup.py` - Database initialization
- `fix_template_errors.py` - Quick template fixes
- `NEW_PC_SETUP_GUIDE.md` - This guide

## ✅ **Verification Checklist**

After running setup, verify:
- [ ] No template variable errors in console
- [ ] Admin interface loads without errors
- [ ] Activate Sets page shows all trades
- [ ] Questions appear in QP Delete section
- [ ] Can upload new questions
- [ ] Can configure question sets
- [ ] Exam interface works for candidates

## 🎯 **Success Indicators**

You'll know setup is successful when:
1. **Clean console output** - No `VariableDoesNotExist` errors
2. **Populated Activate Sets** - All trades visible with configuration options
3. **Working question upload** - Can upload and see questions
4. **Functional admin** - All admin pages load without errors

## 🔄 **For Future Deployments**

To avoid these issues on new PCs:
1. Always run `first_time_setup.py` on fresh installations
2. Ensure `.env` file is properly configured
3. Run database initialization scripts after migrations
4. Test admin interface before going live

The setup scripts ensure consistent deployment across different environments and resolve all template/database initialization issues automatically.