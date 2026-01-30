# Implementation Plan: Customizable Question Set Naming

## Overview

This implementation plan converts the question set naming system from single-character restrictions to fully customizable string identifiers. The approach follows Django best practices for model field changes, implements robust validation, and ensures backward compatibility with existing data.

## Tasks

- [ ] 1. Create custom validation and update model definition
  - Create custom validator function for question set names
  - Update QuestionSet model with new CharField specifications
  - Add appropriate help text and validation rules
  - _Requirements: 1.1, 1.2, 1.3, 4.1, 4.2_

- [ ]* 1.1 Write property test for string input acceptance
  - **Property 1: String Input Acceptance**
  - **Validates: Requirements 1.1, 1.2, 1.3**

- [ ]* 1.2 Write property test for empty input rejection
  - **Property 6: Empty Input Rejection**
  - **Validates: Requirements 4.1**

- [ ]* 1.3 Write property test for whitespace normalization
  - **Property 7: Whitespace Normalization**
  - **Validates: Requirements 4.2**

- [ ] 2. Create and run database migration
  - Generate Django migration for CharField max_length change
  - Test migration on development database with existing data
  - Verify all existing question set assignments are preserved
  - _Requirements: 5.1, 5.3_

- [ ]* 2.1 Write property test for migration data preservation
  - **Property 9: Migration Data Preservation**
  - **Validates: Requirements 5.3**

- [ ] 3. Update Excel import validation logic
  - Modify Excel import service to use new validation rules
  - Replace single-character validation with flexible string validation
  - Implement proper error handling and reporting for invalid names
  - Ensure exact preservation of names from Excel files
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 3.1 Write property test for Excel import round trip
  - **Property 2: Excel Import Round Trip**
  - **Validates: Requirements 2.1, 2.2**

- [ ]* 3.2 Write property test for import validation consistency
  - **Property 3: Import Validation Consistency**
  - **Validates: Requirements 2.3, 4.4**

- [ ]* 3.3 Write property test for invalid character rejection
  - **Property 4: Invalid Character Rejection**
  - **Validates: Requirements 2.4**

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Update admin interface for variable-length names
  - Modify QuestionSetAdmin class for better display of long names
  - Update list_display and search functionality
  - Ensure proper handling of both legacy and new name formats
  - _Requirements: 1.4, 6.1, 6.4_

- [ ]* 5.1 Write property test for display completeness
  - **Property 10: Display Completeness**
  - **Validates: Requirements 1.4, 6.1**

- [ ]* 5.2 Write property test for partial search matching
  - **Property 11: Partial Search Matching**
  - **Validates: Requirements 6.4**

- [ ] 6. Implement uniqueness validation
  - Add database-level uniqueness constraint validation
  - Implement proper error handling for duplicate names
  - Test uniqueness enforcement across different entry methods
  - _Requirements: 4.3_

- [ ]* 6.1 Write property test for uniqueness enforcement
  - **Property 8: Uniqueness Enforcement**
  - **Validates: Requirements 4.3**

- [ ] 7. Test backward compatibility with legacy data
  - Verify all existing single-letter question sets continue to work
  - Test mixed environments with both legacy and new naming formats
  - Ensure consistent behavior across all system operations
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 7.1 Write property test for legacy compatibility
  - **Property 5: Legacy Compatibility**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [ ] 8. Integration testing and final validation
  - Test complete workflow from Excel import to admin display
  - Verify error handling works correctly across all entry points
  - Test edge cases with maximum length names and special characters
  - Validate that all requirements are met end-to-end
  - _Requirements: All requirements_

- [ ] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties using Hypothesis
- Unit tests focus on specific examples and edge cases
- Migration testing should be done on a copy of production data
- All validation rules must be consistent between manual entry and Excel import