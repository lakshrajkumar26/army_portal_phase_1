# Requirements Document

## Introduction

This document specifies the requirements for enhancing the existing Django-based exam system's question management capabilities. The system currently manages questions for various trades (DMV, ARTISAN, CHEFCOM, etc.) with PRIMARY/SECONDARY paper types but lacks proper question set management and has a complex upload format. This enhancement will introduce A-Z question sets, simplified admin controls, and an improved upload format to provide better control over question distribution and easier administration.

## Glossary

- **Question_Set**: A labeled collection of questions (A, B, C, D, E, F, etc.) for a specific trade and paper type
- **Trade**: A specific job category (DMV, ARTISAN, CHEFCOM, etc.) that candidates are tested on
- **Paper_Type**: Either PRIMARY or SECONDARY examination type
- **Admin_User**: System administrator with permissions to manage question sets and activations
- **Upload_System**: The mechanism for importing questions from external files
- **Activation_System**: The mechanism for controlling which question sets are available to candidates
- **Question_Bank**: The complete collection of all questions across all trades and sets
- **Global_Control**: Master control system for activating paper types across all trades simultaneously

## Requirements

### Requirement 1: Question Set Management System

**User Story:** As an admin user, I want to organize questions into labeled sets (A-Z) for each trade, so that I can manage multiple versions of question papers and control which version candidates receive.

#### Acceptance Criteria

1. THE Question_Bank SHALL support question sets labeled A through Z for each trade and paper type combination
2. WHEN an admin creates a question, THE Upload_System SHALL require a question_set field to be specified
3. THE Question_Bank SHALL store questions with their associated question_set identifier
4. WHEN displaying questions in admin interface, THE System SHALL group questions by trade, paper_type, and question_set
5. THE System SHALL prevent duplicate question_set labels within the same trade and paper_type combination

### Requirement 2: Question Set Activation Control

**User Story:** As an admin user, I want to control which question set is active for each trade, so that I can ensure candidates only see questions from the intended version.

#### Acceptance Criteria

1. WHEN an admin activates a question set for a trade, THE Activation_System SHALL deactivate all other sets for that trade and paper type
2. THE System SHALL ensure only one question set is active per trade and paper type at any time
3. WHEN a candidate starts an exam, THE System SHALL only present questions from the currently active set for their trade
4. THE Activation_System SHALL maintain an audit trail of set activation changes with timestamps and admin user information
5. IF no question set is active for a trade, THEN THE System SHALL prevent exam generation for that trade

### Requirement 3: Simplified Global Paper Type Control

**User Story:** As an admin user, I want to activate PRIMARY or SECONDARY papers globally with simple checkboxes, so that I can quickly switch all trades to the same paper type without individual trade management.

#### Acceptance Criteria

1. WHEN admin checks the PRIMARY checkbox, THE System SHALL activate PRIMARY papers for all trades and deactivate all SECONDARY papers
2. WHEN admin checks the SECONDARY checkbox, THE System SHALL activate SECONDARY papers for all trades and deactivate all PRIMARY papers
3. THE System SHALL prevent both PRIMARY and SECONDARY from being active simultaneously
4. THE System SHALL provide visual feedback showing which paper type is currently active globally
5. THE Global_Control SHALL override individual trade-level activations when used

### Requirement 4: Enhanced Upload Format

**User Story:** As an admin user, I want to upload questions using a simplified column-based format instead of JSON arrays, so that I can more easily prepare and validate question data.

#### Acceptance Criteria

1. THE Upload_System SHALL accept CSV files with separate columns for option_a, option_b, option_c, and option_d
2. THE Upload_System SHALL reject files that use the old JSON array format for options
3. WHEN processing uploads, THE System SHALL validate that all required columns are present: question, part, marks, option_a, option_b, option_c, option_d, correct_answer, trade, paper_type, question_set, is_common, is_active
4. THE Upload_System SHALL validate that question_set values are single letters A-Z
5. THE Upload_System SHALL provide detailed error messages for invalid upload formats or missing data

### Requirement 5: Database Schema Enhancement

**User Story:** As a system architect, I want the database to efficiently store and query question sets, so that the system can scale with large question banks while maintaining performance.

#### Acceptance Criteria

1. THE Question model SHALL include a question_set field with single character A-Z validation
2. THE System SHALL create a QuestionSetActivation model to track which sets are active for each trade and paper type
3. THE Database SHALL maintain referential integrity between questions and their associated trades and question sets
4. THE System SHALL create appropriate database indexes for efficient querying by trade, paper_type, and question_set
5. THE Migration_System SHALL preserve existing question data when adding the question_set field

### Requirement 6: Backward Compatibility

**User Story:** As a system administrator, I want existing questions to continue working after the enhancement, so that current exam operations are not disrupted during the transition.

#### Acceptance Criteria

1. WHEN the system is upgraded, THE Migration_System SHALL assign existing questions to a default question set (A)
2. THE System SHALL continue to support existing exam generation logic for questions without explicit set assignments
3. THE Admin_Interface SHALL display both old and new format questions in a unified view
4. THE System SHALL maintain existing API endpoints for exam generation while adding new set-aware functionality
5. THE Upgrade_Process SHALL not require immediate re-upload of existing question data

### Requirement 7: Admin Interface Enhancements

**User Story:** As an admin user, I want an intuitive interface for managing question sets and activations, so that I can efficiently control the exam system without technical expertise.

#### Acceptance Criteria

1. THE Admin_Interface SHALL provide a dashboard showing active question sets for all trades at a glance
2. WHEN viewing questions, THE Interface SHALL allow filtering by trade, paper_type, and question_set
3. THE Interface SHALL provide bulk operations for activating/deactivating question sets
4. THE Admin_Interface SHALL display validation errors clearly during question upload with specific line numbers and error descriptions
5. THE Interface SHALL provide a preview function to review questions before activation

### Requirement 8: Question Set Validation and Integrity

**User Story:** As an admin user, I want the system to validate question set completeness, so that I can ensure candidates receive properly structured exams.

#### Acceptance Criteria

1. WHEN activating a question set, THE System SHALL validate that sufficient questions exist for each part (A, B, C, D, E, F) according to trade requirements
2. THE Validation_System SHALL check that all required question parts have the correct number of questions as defined in HARD_CODED_TRADE_CONFIG
3. IF a question set is incomplete, THEN THE System SHALL prevent activation and display specific missing requirements
4. THE System SHALL validate that correct_answer values correspond to valid options (option_a, option_b, option_c, or option_d)
5. THE Validation_System SHALL ensure question text and options are not empty or contain only whitespace

### Requirement 9: Audit and Reporting

**User Story:** As a system administrator, I want to track question set usage and changes, so that I can maintain accountability and analyze exam patterns.

#### Acceptance Criteria

1. THE System SHALL log all question set activation and deactivation events with timestamps and admin user information
2. THE Reporting_System SHALL provide statistics on question set usage across different exam sessions
3. THE System SHALL track which question sets were used for each completed exam session
4. THE Audit_System SHALL maintain a history of question uploads with file names, upload dates, and processing results
5. THE System SHALL generate reports showing question distribution across sets and trades for analysis

### Requirement 10: Error Handling and Recovery

**User Story:** As an admin user, I want clear error messages and recovery options when question management operations fail, so that I can quickly resolve issues and maintain system availability.

#### Acceptance Criteria

1. WHEN question upload fails, THE System SHALL provide specific error messages indicating the problem location and suggested fixes
2. IF question set activation fails due to insufficient questions, THEN THE System SHALL suggest which questions need to be added
3. THE System SHALL provide rollback capability for failed question set activations
4. WHEN database constraints are violated, THE Error_Handler SHALL provide user-friendly explanations rather than technical database errors
5. THE System SHALL gracefully handle concurrent admin operations and prevent data corruption during simultaneous question set modifications