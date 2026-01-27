# Implementation Plan: Question Set Management Enhancement

## Overview

This implementation plan converts the question set management design into discrete coding tasks that build incrementally. The approach focuses on enhancing the existing Django exam system with A-Z question sets, global paper type controls, and improved CSV upload format while maintaining backward compatibility.

## Tasks

- [x] 1. Enhance Question model and create new models
  - Add question_set field to existing Question model with A-Z validation
  - Add separate option fields (option_a, option_b, option_c, option_d) to Question model
  - Create QuestionSetActivation model with trade, paper_type, question_set tracking
  - Create GlobalPaperTypeControl model for master paper type control
  - Create database migration to add new fields and preserve existing data
  - _Requirements: 1.1, 1.2, 1.3, 5.1, 5.2, 5.5, 6.1_

- [ ]* 1.1 Write property test for Question model enhancements
  - **Property 10: Content Validation Integrity**
  - **Validates: Requirements 1.2, 5.1, 5.3, 8.5**

- [x] 2. Implement Question Set Activation Logic
  - [x] 2.1 Implement QuestionSetActivation save method with mutual exclusion
    - Override save method to deactivate other sets when one is activated
    - Ensure only one question set is active per trade and paper type
    - _Requirements: 2.1, 2.2_
  
  - [ ]* 2.2 Write property test for question set mutual exclusion
    - **Property 2: Question Set Mutual Exclusion**
    - **Validates: Requirements 2.1, 2.2**
  
  - [x] 2.3 Implement GlobalPaperTypeControl save method
    - Override save method to cascade changes to all trades
    - Deactivate opposite paper type when one is activated
    - Create default activations for all trades
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  
  - [ ]* 2.4 Write property test for global paper type control
    - **Property 4: Global Paper Type Control**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.5**

- [x] 3. Create CSV Upload Processor
  - [x] 3.1 Implement QuestionCSVProcessor class
    - Create validation methods for headers and row data
    - Implement comprehensive field validation (question_set A-Z, correct_answer options, etc.)
    - Add support for new column format (option_a, option_b, option_c, option_d)
    - Reject old JSON array format for options
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 3.2 Write property test for CSV upload validation
    - **Property 5: CSV Upload Format Validation**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
  
  - [x] 3.3 Implement bulk question creation with error handling
    - Use Django's bulk_create for performance
    - Provide detailed error messages with line numbers
    - Handle validation errors gracefully
    - _Requirements: 4.5, 10.1_
  
  - [ ]* 3.4 Write property test for comprehensive error handling
    - **Property 9: Comprehensive Error Handling**
    - **Validates: Requirements 4.5, 10.1, 10.2, 10.3, 10.4**

- [ ] 4. Checkpoint - Ensure core models and upload processing work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Question Set Validation System
  - [ ] 5.1 Create ActivationErrorHandler class
    - Implement validation against HARD_CODED_TRADE_CONFIG
    - Check sufficient questions exist for each part (A, B, C, D, E, F)
    - Validate correct_answer corresponds to valid options
    - Prevent activation of incomplete question sets
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ]* 5.2 Write property test for question set completeness validation
    - **Property 6: Question Set Completeness Validation**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
  
  - [ ] 5.3 Implement rollback capability for failed activations
    - Create rollback methods for failed question set activations
    - Handle concurrent operations safely with database transactions
    - _Requirements: 10.3, 10.5_

- [ ] 6. Enhance Exam Generation Logic
  - [ ] 6.1 Update QuestionPaper.generate_for_candidate method
    - Modify exam generation to use active question sets
    - Query questions from currently active set for candidate's trade
    - Maintain backward compatibility with existing logic
    - _Requirements: 2.3, 2.5, 6.2, 6.4_
  
  - [ ]* 6.2 Write property test for exam generation from active sets
    - **Property 3: Exam Generation from Active Sets**
    - **Validates: Requirements 2.3, 2.5**
  
  - [ ] 6.3 Add question set tracking to ExamSession model
    - Add field to track which question set was used for each exam session
    - Update exam generation to record question set usage
    - _Requirements: 9.3_

- [x] 7. Create Enhanced Admin Interface
  - [x] 7.1 Create QuestionSetActivationAdmin class
    - Add list display with trade, paper_type, question_set, is_active
    - Implement filtering by trade, paper_type, question_set
    - Add bulk activation/deactivation actions
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 7.2 Create GlobalPaperTypeControlAdmin class
    - Add admin actions for global PRIMARY/SECONDARY activation
    - Display current active paper type status
    - _Requirements: 3.4, 7.1_
  
  - [x] 7.3 Enhance existing QuestionAdmin class
    - Add question_set field to list display and filters
    - Add separate option fields to admin form
    - Implement question preview functionality
    - _Requirements: 1.4, 7.5_
  
  - [ ]* 7.4 Write unit tests for admin interface enhancements
    - Test bulk operations functionality
    - Test filtering and display features
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 8. Implement Audit and Reporting System
  - [ ] 8.1 Create AuditLog model and logging functionality
    - Track all question set activation/deactivation events
    - Log question upload operations with file names and results
    - Record timestamps and admin user information
    - _Requirements: 2.4, 9.1, 9.4_
  
  - [ ]* 8.2 Write property test for audit trail completeness
    - **Property 8: Audit Trail Completeness**
    - **Validates: Requirements 2.4, 9.1, 9.4**
  
  - [ ] 8.3 Create reporting views for question set usage
    - Implement statistics on question set usage across exam sessions
    - Create reports showing question distribution across sets and trades
    - _Requirements: 9.2, 9.5_

- [ ] 9. Create Data Migration and Backward Compatibility
  - [ ] 9.1 Create migration script for existing questions
    - Assign all existing questions to default question set 'A'
    - Convert existing JSON options to separate option fields where possible
    - Preserve all existing question data
    - _Requirements: 5.5, 6.1_
  
  - [ ]* 9.2 Write property test for data migration preservation
    - **Property 7: Data Migration Preservation**
    - **Validates: Requirements 5.5, 6.1, 6.2**
  
  - [ ] 9.3 Ensure backward compatibility in admin interface
    - Display both old and new format questions in unified view
    - Maintain existing API endpoints functionality
    - _Requirements: 6.3, 6.4, 6.5_

- [ ] 10. Final Integration and Testing
  - [ ] 10.1 Create comprehensive integration tests
    - Test complete workflow from CSV upload to exam generation
    - Test global paper type control affecting all trades
    - Test concurrent admin operations
    - _Requirements: 10.5_
  
  - [ ]* 10.2 Write property test for question set storage and organization
    - **Property 1: Question Set Storage and Organization**
    - **Validates: Requirements 1.1, 1.3, 1.4**
  
  - [ ] 10.3 Create sample data and documentation
    - Generate sample CSV files in new format
    - Create admin user guide for question set management
    - Document migration process and new features

- [ ] 11. Final checkpoint - Ensure all functionality works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and integration points
- Migration preserves existing data while adding new functionality
- Backward compatibility maintained throughout implementation