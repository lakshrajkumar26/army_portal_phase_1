# Exam Session Persistence Fix - Complete Solution

## Problem Summary

The exam portal had a critical issue where candidates would get stuck with old question sets even after:
- Question sets were changed by administrators
- Exam slots were reset or reassigned
- New slots were assigned after consumption

### Root Cause

The issue was caused by **persistent ExamSession records** in the database:

1. When a candidate first took an exam, an `ExamSession` was created with specific `ExamQuestion` records linked to questions from a particular set (e.g., Set C)
2. The system's session retrieval logic would find existing incomplete sessions and resume them:
   ```python
   session = ExamSession.objects.filter(
       user=request.user,
       paper=paper,
       completed_at__isnull=True
   ).order_by("-started_at").first()
   ```
3. Even after slot resets and question set changes, these old sessions persisted, causing candidates to see outdated questions

## Complete Fix Implementation

### 1. Updated CandidateProfile Model (`registration/models.py`)

Enhanced slot management methods to automatically clear incomplete sessions:

```python
def assign_exam_slot(self, assigned_by_user=None):
    """
    Assign a new exam slot to the candidate
    CRITICAL FIX: Clear incomplete exam sessions to prevent old question set persistence
    """
    from questions.models import ExamSession
    
    # Clear any incomplete exam sessions to prevent old question set binding
    incomplete_sessions = ExamSession.objects.filter(
        user=self.user,
        completed_at__isnull=True
    )
    cleared_count = incomplete_sessions.count()
    if cleared_count > 0:
        incomplete_sessions.delete()
        print(f"✅ Cleared {cleared_count} incomplete sessions for {self.army_no} during slot assignment")
    
    # ... rest of slot assignment logic
```

Similar fixes applied to:
- `reset_exam_slot()` - Clears sessions when slots are reset
- Both methods now ensure fresh question set assignment

### 2. Updated ActivateSets Model (`questions/models.py`)

Enhanced the save method to clear incomplete sessions when question sets change:

```python
def save(self, *args, **kwargs):
    """
    Override save to sync with QuestionSetActivation model
    CRITICAL FIX: Clear incomplete exam sessions when question sets change
    """
    # Check if question sets are changing
    sets_changed = False
    if self.pk:  # Existing record
        try:
            old_instance = ActivateSets.objects.get(pk=self.pk)
            if (old_instance.active_primary_set != self.active_primary_set or 
                old_instance.active_secondary_set != self.active_secondary_set):
                sets_changed = True
        except ActivateSets.DoesNotExist:
            pass
    
    with transaction.atomic():
        super().save(*args, **kwargs)
        
        # If question sets changed, clear incomplete sessions for this trade
        if sets_changed:
            from registration.models import CandidateProfile
            candidates = CandidateProfile.objects.filter(trade=self.trade)
            total_cleared = 0
            
            for candidate in candidates:
                incomplete_sessions = ExamSession.objects.filter(
                    user=candidate.user,
                    completed_at__isnull=True
                )
                cleared_count = incomplete_sessions.count()
                if cleared_count > 0:
                    incomplete_sessions.delete()
                    total_cleared += cleared_count
            
            if total_cleared > 0:
                print(f"✅ Cleared {total_cleared} incomplete sessions for {self.trade.name} due to question set change")
        
        # ... rest of sync logic
```

### 3. Enhanced Admin Actions (`registration/admin.py`)

Updated all slot management actions to include session cleanup:

```python
def assign_exam_slots(modeladmin, request, queryset):
    """Assign exam slots to selected candidates with session cleanup"""
    from questions.models import ExamSession
    
    count = 0
    sessions_cleared = 0
    
    for candidate in queryset:
        # Clear incomplete sessions before assigning new slot
        incomplete_sessions = ExamSession.objects.filter(
            user=candidate.user,
            completed_at__isnull=True
        )
        cleared_count = incomplete_sessions.count()
        if cleared_count > 0:
            incomplete_sessions.delete()
            sessions_cleared += cleared_count
        
        if candidate.assign_exam_slot(assigned_by_user=request.user):
            count += 1
    
    # ... success message with session cleanup info
```

Added new admin action for manual session cleanup:
```python
def clear_incomplete_sessions(modeladmin, request, queryset):
    """Clear incomplete exam sessions for selected candidates"""
    # ... implementation
```

### 4. Management Command (`questions/management/commands/clear_incomplete_sessions.py`)

Created a comprehensive management command for session cleanup:

```bash
# Clear all incomplete sessions
python manage.py clear_incomplete_sessions --all

# Clear sessions for specific trade
python manage.py clear_incomplete_sessions --trade "TTC"

# Clear sessions for specific candidate
python manage.py clear_incomplete_sessions --army-no "12345678"

# Dry run to see what would be cleared
python manage.py clear_incomplete_sessions --all --dry-run
```

### 5. Utility Scripts

Created helper scripts:
- `fix_exam_session_persistence.py` - Interactive tool for fixing session persistence
- `test_session_persistence_fix.py` - Automated test to verify the fix works

## Test Results

The fix was thoroughly tested with the following scenario:

1. ✅ **Setup**: Created candidate with TTC trade, Set C questions
2. ✅ **Initial Session**: Generated exam session with Set C questions  
3. ✅ **Question Set Change**: Changed active set from C to E
4. ✅ **Session Cleanup**: Incomplete sessions automatically cleared
5. ✅ **Slot Reset/Reassign**: Reset and reassigned exam slot
6. ✅ **New Session**: Generated new session with Set E questions
7. ✅ **Verification**: Confirmed candidate now sees Set E questions

**Test Output:**
```
✅ SUCCESS: New session correctly uses Set E!
🎉 TEST PASSED: Session persistence fix is working!
```

## Key Benefits

### For Administrators
- **Reliable Question Set Management**: Changes to question sets now immediately affect all candidates
- **Flexible Slot Management**: Can reset/reassign slots without worrying about old sessions
- **Admin Tools**: New actions and commands for managing session cleanup
- **Transparency**: Clear feedback on how many sessions were cleared during operations

### For Candidates  
- **Fresh Question Sets**: Always get the currently active question set
- **No Stale Sessions**: Won't be stuck with old questions from previous attempts
- **Consistent Experience**: Exam behavior is predictable and reliable

### For System Integrity
- **Data Consistency**: Question set assignments are always current
- **Performance**: No accumulation of stale session data
- **Debugging**: Clear logging of session cleanup operations

## Usage Instructions

### For Immediate Fix
If you have candidates currently stuck with old question sets:

1. **Use the management command**:
   ```bash
   python manage.py clear_incomplete_sessions --all
   ```

2. **Or use the admin interface**:
   - Select affected candidates
   - Choose "🧹 Clear Incomplete Exam Sessions" action

### For Ongoing Operations
The fix is now automatic:
- Changing question sets automatically clears affected sessions
- Resetting/assigning slots automatically clears sessions
- Admin actions include session cleanup by default

## Files Modified

1. `registration/models.py` - Enhanced slot management methods
2. `questions/models.py` - Enhanced ActivateSets save method  
3. `registration/admin.py` - Updated admin actions with session cleanup
4. `questions/management/commands/clear_incomplete_sessions.py` - New management command
5. `fix_exam_session_persistence.py` - Utility script
6. `test_session_persistence_fix.py` - Test verification script

## Conclusion

This comprehensive fix resolves the exam session persistence issue by ensuring that incomplete exam sessions are automatically cleared whenever:
- Question sets are changed
- Exam slots are reset or reassigned
- Administrators manually trigger session cleanup

The solution is robust, well-tested, and provides both automatic and manual tools for managing session persistence issues.