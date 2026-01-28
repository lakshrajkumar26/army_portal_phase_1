# Requirements Document

## Introduction

This specification addresses three critical issues in the question set management system that prevent proper handling of secondary questions and limit administrative efficiency. The system currently has a data import bug where questions containing "SECONDARY" in their text are incorrectly classified as PRIMARY, a UI filtering bug that prevents secondary questions from being displayed, and lacks a universal set activation feature for bulk operations.

## Glossary

- **System**: The Django-based question set management system
- **Question**: Django model representing individual exam questions with fields for text, paper_type, trade, is_common, question_set, and is_active
- **Paper_Type**: Enum field with values PRIMARY (trade-specific) or SECONDARY (common across trades)
- **Trade**: Specific vocational trade (e.g., OCC, DMV, TTC)
- **Question_Set**: Alphabetical identifier (A-Z) grouping questions within a paper type
- **ActivateSets**: Django model managing active question sets for each trade
- **Admin_Interface**: Django admin interface at /admin/questions/activatesets/
- **Secondary_Questions**: Questions with paper_type='SECONDARY', trade=NULL, and is_common=True
- **Primary_Questions**: Questions with paper_type='PRIMARY' and specific trade assignment
- **Data_Import**: Process of uploading and processing .dat files containing question data
- **Universal_Set_Activator**: New feature to activate question sets for all trades simultaneously
- **Excel_Parser**: Component that processes decrypted .dat files and extracts question data

## Requirements

### Requirement 1: Fix Data Import Classification Bug

**User Story:** As a system administrator, I want questions containing "SECONDARY" in their text to be correctly classified with paper_type='SECONDARY', so that secondary questions are properly imported and available for activation.

#### Acceptance Criteria

1. WHEN the Excel parser processes a question with "SECONDARY" in the text field, THE System SHALL set paper_type='SECONDARY' for that question
2. WHEN the Excel parser processes a question with "SECONDARY" in the text field, THE System SHALL set trade=NULL for that question
3. WHEN the Excel parser processes a question with "SECONDARY" in the text field, THE System SHALL set is_common=True for that question
4. WHEN the Excel parser processes a question without "SECONDARY" in the text field, THE System SHALL maintain existing PRIMARY classification logic
5. WHEN secondary questions are imported, THE System SHALL preserve all other question attributes (text, part, marks, options, correct_answer, question_set, is_active)

### Requirement 2: Fix UI Filtering Logic Bug

**User Story:** As an admin user, I want to see available secondary question sets when I toggle to SECONDARY paper type, so that I can activate and manage secondary question sets properly.

#### Acceptance Criteria

1. WHEN an admin selects SECONDARY paper type in the admin UI, THE System SHALL display all available secondary question sets using paper_type='SECONDARY' and is_common=True filtering
2. WHEN filtering secondary questions, THE System SHALL NOT apply trade-based filtering
3. WHEN filtering primary questions, THE System SHALL continue using trade-based filtering with paper_type='PRIMARY'
4. WHEN secondary question sets are displayed, THE System SHALL show accurate question counts for each set
5. WHEN the get_available_sets method is called with paper_type='SECONDARY', THE System SHALL return question sets from questions where paper_type='SECONDARY', is_common=True, and is_active=True

### Requirement 3: Implement Universal Set Activation Feature

**User Story:** As an admin user, I want to activate a question set for all trades at once, so that I can efficiently manage question set assignments without having to configure each trade individually.

#### Acceptance Criteria

1. WHEN an admin accesses the admin interface, THE System SHALL display a universal set activation form with a dropdown for question sets (A, B, C, D, E)
2. WHEN an admin selects a question set and clicks the universal activation button, THE System SHALL activate that question set for all trades simultaneously
3. WHEN universal activation is performed, THE System SHALL deactivate all other question sets for all trades to ensure only one set is active per trade
4. WHEN universal activation is performed, THE System SHALL update the activated_by field with the current admin user
5. WHEN universal activation is performed, THE System SHALL display a success message indicating how many trades were updated
6. WHEN universal activation is performed, THE System SHALL work alongside the existing individual trade activation interface without conflicts

### Requirement 4: Maintain Data Integrity During Import

**User Story:** As a system administrator, I want the import process to maintain data integrity, so that existing questions are not corrupted and duplicate detection works correctly.

#### Acceptance Criteria

1. WHEN questions are imported with the new classification logic, THE System SHALL preserve all existing Question records unchanged
2. WHEN duplicate questions are detected during import, THE System SHALL use the same duplicate detection logic (text+part+trade/is_common+question_set)
3. WHEN secondary questions are imported, THE System SHALL ensure they have consistent field values (trade=NULL, is_common=True, paper_type='SECONDARY')
4. WHEN the import process encounters errors, THE System SHALL log detailed error messages without crashing the server
5. WHEN the import process completes, THE System SHALL report accurate counts of created and skipped questions

### Requirement 5: Ensure Backward Compatibility

**User Story:** As a system administrator, I want the fixes to maintain backward compatibility, so that existing workflows and data remain functional.

#### Acceptance Criteria

1. WHEN the new classification logic is applied, THE System SHALL continue to support existing primary question workflows
2. WHEN the UI filtering fix is applied, THE System SHALL preserve all existing admin interface functionality
3. WHEN the universal set activator is added, THE System SHALL maintain compatibility with existing individual trade activation features
4. WHEN any changes are made, THE System SHALL not require database migrations or data transformations
5. WHEN the system is updated, THE System SHALL continue to support existing .dat file formats and decryption processes

### Requirement 6: Validate Question Count Accuracy

**User Story:** As an admin user, I want accurate question counts displayed for both primary and secondary question sets, so that I can make informed decisions about question set activation.

#### Acceptance Criteria

1. WHEN displaying secondary question sets, THE System SHALL show correct question counts using secondary-specific filtering (paper_type='SECONDARY', is_common=True, is_active=True)
2. WHEN displaying primary question sets, THE System SHALL show correct question counts using trade-specific filtering (trade=specific_trade, paper_type='PRIMARY', is_active=True)
3. WHEN question counts are calculated, THE System SHALL include only active questions (is_active=True)
4. WHEN question counts are zero, THE System SHALL display "0" rather than hiding the question set
5. WHEN the get_question_count method is called, THE System SHALL use the same filtering logic as get_available_sets for consistency

### Requirement 7: Implement Robust Error Handling

**User Story:** As a system administrator, I want comprehensive error handling during import and activation processes, so that system failures are prevented and issues are clearly communicated.

#### Acceptance Criteria

1. WHEN invalid .dat files are uploaded, THE System SHALL provide clear error messages without crashing
2. WHEN decryption fails, THE System SHALL log the error and continue processing other files
3. WHEN Excel parsing encounters malformed data, THE System SHALL skip invalid rows and continue processing valid ones
4. WHEN universal set activation is attempted with invalid parameters, THE System SHALL validate inputs and provide appropriate error messages
5. WHEN database operations fail during import or activation, THE System SHALL roll back transactions and maintain data consistency

### Requirement 8: Optimize Performance for Large Datasets

**User Story:** As a system administrator, I want the system to handle large question datasets efficiently, so that import and activation operations complete in reasonable time.

#### Acceptance Criteria

1. WHEN processing large .dat files, THE System SHALL use bulk database operations to minimize query overhead
2. WHEN filtering questions for display, THE System SHALL utilize existing database indexes for optimal performance
3. WHEN performing universal set activation, THE System SHALL use batch updates to minimize database round trips
4. WHEN calculating question counts, THE System SHALL use efficient database queries with appropriate filtering
5. WHEN the system processes multiple concurrent operations, THE System SHALL maintain acceptable response times