# Question Set Management Guide

## Overview

Your exam system now properly supports multiple question sets (A, B, C, D, E) for each trade. This allows you to have different versions of exams for the same trade, ensuring exam security and variety.

## How It Works

1. **Question Sets**: Each question belongs to a specific set (A, B, C, D, E)
2. **Active Sets**: Only ONE set can be active per trade at any time
3. **Exam Generation**: When candidates take exams, they get questions from the currently active set for their trade

## Data Upload Requirements

For the system to work correctly, your Excel/CSV files should include these columns:
- `question` or `question_set`: The question set identifier (A, B, C, D, E)
- `trade`: Trade name (DMV, OCC, etc.)
- `paper_type`: PRIMARY or SECONDARY
- `is_common`: TRUE/FALSE for common questions

**Note**: If your data doesn't have a `question_set` column, the system will try to extract it from the question text (e.g., "DMV PRIMARY Set B Part A..." will be identified as Set B).

## Admin Interface

### 1. Global Paper Type Control
- **Location**: Admin → Questions → Global Paper Type Controls
- **Purpose**: Master control for PRIMARY/SECONDARY paper activation
- **Usage**: 
  - Activate PRIMARY globally to enable primary exams for all trades
  - Activate SECONDARY globally to enable secondary exams for all trades

### 2. Question Set Activation Management
- **Location**: Admin → Questions → Question Set Activations
- **Purpose**: Manage which question set is active for each trade
- **Features**:
  - View all trades and their active question sets
  - Activate/deactivate specific sets per trade
  - Only one set can be active per trade at a time

## Import Process (Fixed)

The import system has been updated to properly handle question sets:

1. **Upload .dat file**: Upload your encrypted Excel file through Admin → Questions → QP Upload
2. **Automatic Processing**: The system will:
   - Decrypt the file
   - Extract question data including question_set field
   - Create questions with correct question_set values
   - Auto-create QuestionSetActivation entries for each trade/paper/set combination
3. **Manual Activation**: Use the Question Set Activation admin to activate the desired sets

## Current Status

After fixing the import issue, you now have:

### DMV Trade:
- PRIMARY Set A: 108 questions (ACTIVE)
- PRIMARY Set B: 108 questions (INACTIVE)
- PRIMARY Set C: 108 questions (INACTIVE)
- PRIMARY Set D: 108 questions (INACTIVE)
- PRIMARY Set E: 108 questions (INACTIVE)

### OCC Trade:
- PRIMARY Set A: 108 questions (INACTIVE)
- PRIMARY Set B: 108 questions (INACTIVE)
- PRIMARY Set C: 108 questions (INACTIVE)
- PRIMARY Set D: 108 questions (INACTIVE)
- PRIMARY Set E: 108 questions (INACTIVE)

## How to Manage Question Sets

### Using Admin Interface:
1. Go to Admin → Questions → Question Set Activations
2. Find the trade and paper type you want to manage
3. Use the bulk actions to activate the desired set
4. The system automatically deactivates other sets for the same trade

### Using Management Command:
```bash
# Show current status
python manage.py manage_question_sets --show-status

# Activate Set B for DMV PRIMARY
python manage.py manage_question_sets --activate-set B --trade DMV --paper-type PRIMARY

# Activate Set C for OCC PRIMARY
python manage.py manage_question_sets --activate-set C --trade OCC --paper-type PRIMARY
```

## Re-uploading Data

**Yes, if you delete the exam data and upload again, it will now map correctly to the given sets!**

The import system has been fixed to:
1. ✅ Extract `question_set` from Excel columns
2. ✅ Fall back to extracting set from question text if column is missing
3. ✅ Create questions with correct question_set values
4. ✅ Auto-create QuestionSetActivation entries for each unique combination

## Example Workflow

1. **Delete Old Data**: Use Admin → Delete Data → Complete Cleanup to remove old questions
2. **Upload New Data**: Upload your .dat file with questions for different sets
3. **Activate Paper Type**: Use Global Paper Type Control to activate PRIMARY or SECONDARY
4. **Set Active Question Sets**: Use Question Set Activation to choose which set is active for each trade
5. **Candidates Take Exam**: They automatically get questions from the active set for their trade

## Benefits

- **Exam Security**: Different sets prevent cheating between exam sessions
- **Flexibility**: Easy to switch between question sets for different exam dates
- **Centralized Control**: Manage all question sets from one admin interface
- **Automatic Management**: System ensures only one set is active per trade
- **Correct Import**: New upload will properly identify and store question sets

## Important Notes

- Only one question set can be active per trade at any time
- When you activate a new set, the previous set is automatically deactivated
- The exam generation system automatically uses the active set for each trade
- All question sets are preserved - you can switch between them anytime
- **Fixed**: Re-uploading data will now correctly map to question sets A, B, C, D, E