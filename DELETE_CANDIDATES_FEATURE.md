# Delete All Candidates Feature

## Overview
Added a new "Delete All Candidates" button to the Delete Data admin module as requested. This provides a targeted cleanup option that removes all candidate registrations while preserving questions and exam data.

## New Feature Details

### 🆕 Delete All Candidates Button
- **Location:** Delete Data → Clean Exam Data section (4th button)
- **Icon:** 👥 (People icon)
- **Color:** Red (danger level)
- **Function:** Deletes all candidate registrations and profiles while preserving questions

## What Gets Deleted

### ❌ Deleted Items:
- All candidate profiles and registrations
- All non-admin user accounts
- All candidate answers and exam sessions
- All candidate photos and uploaded media
- All exam slots and candidate-related data

### ✅ Preserved Items:
- All questions and question papers
- All admin/superuser accounts
- All exam configuration and settings
- All trade and center data
- Application structure and settings

## Implementation Details

### 1. Admin Interface
- **Template Updated:** `deletedata/templates/admin/deletedata/examdatacleanup/change_list.html`
- **New Button:** Added 4th cleanup card with red styling
- **JavaScript Function:** `deleteAllCandidates()` with multiple confirmations
- **Typed Confirmation:** Requires typing "DELETE CANDIDATES" to proceed

### 2. Backend Implementation
- **New URL:** `delete-candidates/` in ExamDataCleanupAdmin
- **New View:** `delete_candidates_view()` method
- **Management Command:** New `--level=candidates` option in cleanup_exam_data.py
- **Proper Dependencies:** Handles foreign key constraints correctly

### 3. Management Command Enhancement
- **New Level:** `python manage.py cleanup_exam_data --level=candidates`
- **Dry Run Support:** `--dry-run` flag shows what would be deleted
- **Proper Order:** Deletes in correct sequence to avoid foreign key errors
- **File Cleanup:** Removes candidate photos from media folder

### 4. Batch File Integration
- **New Option:** Added to exam_admin.bat slot management menu
- **Interactive:** Shows dry run first, then asks for confirmation
- **Safety:** Requires typing "yes" to proceed

## Deletion Order (Critical for Foreign Keys)

```
1. CandidateAnswer (references candidates and questions)
2. ExamQuestion (for candidate sessions only)
3. ExamSession (for candidate users only)
4. CandidateProfile (references users)
5. User (non-admin users only)
6. Candidate Photos (media files)
```

## Safety Features

### Multiple Confirmations:
1. **First Alert:** Warning about permanent deletion
2. **Second Alert:** Final confirmation with details
3. **Typed Confirmation:** Must type "DELETE CANDIDATES" exactly
4. **Dry Run Available:** Command line shows what would be deleted first

### Visual Warnings:
- Red color coding for danger level
- Clear description of what gets deleted/preserved
- Warning section mentions candidate cleanup
- Alternative options provided

## Usage Examples

### Admin Interface:
1. Go to Admin → Delete Data → Clean Exam Data
2. Click "Delete All Candidates" (red button)
3. Confirm through multiple dialogs
4. Type "DELETE CANDIDATES" when prompted
5. Check success/error messages

### Command Line:
```bash
# See what would be deleted (recommended first)
python manage.py cleanup_exam_data --level=candidates --dry-run

# Actually delete candidates
python manage.py cleanup_exam_data --level=candidates --confirm
```

### Batch File:
```bash
# Run interactive menu
exam_admin.bat
# Choose: 5. Manage exam slots
# Choose: 6. Delete all candidates
# Follow prompts
```

## Testing Results

### ✅ Dry Run Output:
```
Candidate answers to delete: 0
Candidate exam questions to delete: 0  
Candidate exam sessions to delete: 5
Candidate profiles to delete: 5
Non-admin users to delete: 5
Questions to preserve: 40
Question papers to preserve: 2
Admin users to preserve: 3
```

### ✅ Admin Interface:
- Server starts without errors
- New button appears correctly
- Confirmations work properly
- Error handling provides feedback

## Files Modified/Created

### Modified Files:
- `deletedata/templates/admin/deletedata/examdatacleanup/change_list.html` - Added 4th button
- `deletedata/admin.py` - Added delete_candidates_view and URL
- `questions/management/commands/cleanup_exam_data.py` - Added candidates level
- `exam_admin.bat` - Added delete candidates option

### New Functions:
- `deleteAllCandidates()` - JavaScript confirmation function
- `delete_candidates_view()` - Admin view for candidate deletion
- `cleanup_candidates_only()` - Management command function
- `cleanup_candidate_photos()` - Photo cleanup helper

## Current Admin Layout

```
Delete Data/
├── Clean Exam Data/
│   ├── 🗃️ Clean Questions & Papers
│   ├── 🧹 Clean All Exam Data
│   ├── 🎫 Reset Exam Slots
│   └── 👥 Delete All Candidates (NEW)
└── Clean Everything/
    └── 🚨 DELETE EVERYTHING
```

## Summary

The "Delete All Candidates" feature is now fully implemented and provides:
- **Targeted Cleanup:** Remove candidates while keeping questions
- **Safety Features:** Multiple confirmations and dry-run options
- **Proper Dependencies:** Handles foreign key constraints correctly
- **Visual Interface:** Clear, color-coded admin interface
- **Command Line Support:** Full management command integration
- **Batch File Integration:** Interactive menu option

This gives administrators precise control over data cleanup, allowing them to remove all candidate data while preserving the question bank and exam configuration for future use.