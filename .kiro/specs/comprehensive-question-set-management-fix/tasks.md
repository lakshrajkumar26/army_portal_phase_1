# Implementation Plan: Comprehensive Question Set Management Fix

## Overview

This implementation plan addresses three critical issues in the question set management system: fixing the data import bug that misclassifies SECONDARY questions, correcting the UI filtering logic that prevents secondary questions from being displayed, and implementing a universal set activation feature for bulk operations. The approach maintains backward compatibility while implementing targeted fixes across the Excel parser, ActivateSets model, and admin interface.

## Tasks

- [x] 1. Fix SECONDARY question classification in Excel parser
  - Modify `load_questions_from_excel_data()` in `questions/services.py` to detect "SECONDARY" in question text
  - Add text pattern matching logic: if "SECONDARY" in text.upper(), set paper_type='SECONDARY', trade=NULL, is_common=True
  - Preserve existing classification logic for questions without "SECONDARY" in text
  - Ensure all other question attributes (text, part, marks, options, correct_answer, question_set, is_active) are preserved
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 1.1 Write property test for SECONDARY question classification
  - **Property 1: SECONDARY Question Classification**
  - **Validates: Requirements 1.1, 1.2, 1.3, 1.5**

- [ ]* 1.2 Write property test for PRIMARY question classification preservation
  - **Property 2: PRIMARY Question Classification Preservation**
  - **Validates: Requirements 1.4, 5.1**

- [x] 2. Fix UI filtering logic in ActivateSets model
  - Modify `get_available_sets()` method in `questions/models.py` to use paper-type-specific filtering
  - For SECONDARY: filter by paper_type='SECONDARY', is_common=True, is_active=True (no trade filter)
  - For PRIMARY: maintain existing trade-based filtering with paper_type='PRIMARY', is_active=True
  - Modify `get_question_count()` method to use the same conditional filtering logic for consistency
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 2.1 Write property test for paper-type-specific filtering
  - **Property 3: Paper-Type-Specific Filtering**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.5**

- [ ]* 2.2 Write property test for question count accuracy and consistency
  - **Property 4: Question Count Accuracy and Consistency**
  - **Validates: Requirements 2.4, 6.1, 6.2, 6.3, 6.5**

- [x] 3. Checkpoint - Verify core classification and filtering fixes
  - Test that SECONDARY questions are now correctly classified during import
  - Test that secondary question sets are displayed in admin UI when SECONDARY paper type is selected
  - Test that primary question functionality remains unchanged
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement universal set activation feature in admin interface
  - Add universal activation form section to `questions/templates/admin/questions/activatesets/change_list.html`
  - Create dropdown with question sets A, B, C, D, E and "Activate for All Trades" button
  - Style the form to match existing admin interface design
  - Position the universal activator prominently above the individual trade management section
  - _Requirements: 3.1_

- [ ]* 4.1 Write unit test for universal activation UI presence
  - **Property 11: UI Display Consistency**
  - **Validates: Requirements 3.1, 6.4**

- [x] 5. Implement universal activation handler in admin view
  - Add `_handle_universal_activation()` method to ActivateSets admin class in `questions/admin.py`
  - Modify `changelist_view()` to handle POST requests with action='activate_universal_set'
  - Implement input validation for question set selection (A-E only)
  - Add logic to get active paper type and validate it exists
  - _Requirements: 3.2, 3.4, 7.4_

- [ ]* 5.1 Write property test for universal set activation completeness
  - **Property 5: Universal Set Activation Completeness**
  - **Validates: Requirements 3.2, 3.3, 3.4, 3.5**

- [x] 6. Implement bulk activation logic with transaction safety
  - Add atomic transaction wrapper for universal activation operations
  - Implement logic to deactivate all question sets for all trades and selected paper type
  - Implement logic to activate selected question set for all trades
  - Update activated_by field with current admin user for audit trail
  - Count and report number of trades updated
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ]* 6.1 Write property test for system integration harmony
  - **Property 12: System Integration Harmony**
  - **Validates: Requirements 3.6**

- [x] 7. Add comprehensive error handling and validation
  - Add input validation for universal activation (valid question sets, active paper type exists)
  - Add error handling for database failures with transaction rollback
  - Add user-friendly error messages for invalid operations
  - Add success messages with detailed feedback (number of trades updated)
  - Ensure graceful handling of edge cases (no trades, no active paper type)
  - _Requirements: 7.1, 7.4, 7.5_

- [ ]* 7.1 Write property test for comprehensive error handling
  - **Property 8: Comprehensive Error Handling**
  - **Validates: Requirements 4.4, 7.1, 7.2, 7.3, 7.4, 7.5**

- [x] 8. Checkpoint - Verify universal activation feature
  - Test universal activation form appears in admin interface
  - Test universal activation successfully updates all trades
  - Test error handling for invalid inputs
  - Test success messages display correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement data integrity safeguards
  - Add validation to ensure secondary questions have consistent field values (trade=NULL, is_common=True, paper_type='SECONDARY')
  - Preserve existing duplicate detection logic (text+part+trade/is_common+question_set)
  - Ensure import operations don't modify existing Question records
  - Add logging for data integrity issues during import
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 9.1 Write property test for data integrity during operations
  - **Property 6: Data Integrity During Operations**
  - **Validates: Requirements 4.1, 4.3, 5.4**

- [ ]* 9.2 Write property test for duplicate detection consistency
  - **Property 7: Duplicate Detection Consistency**
  - **Validates: Requirements 4.2**

- [x] 10. Add performance optimizations
  - Ensure filtering operations use existing database indexes efficiently
  - Implement bulk database operations for universal activation to minimize query overhead
  - Add query optimization for question count calculations
  - Test performance with large datasets and optimize as needed
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 10.1 Write property test for performance optimization
  - **Property 10: Performance Optimization**
  - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

- [x] 11. Ensure backward compatibility preservation
  - Test that existing primary question workflows continue to function
  - Test that existing admin interface functionality remains intact
  - Test that existing individual trade activation features work alongside universal activation
  - Test that existing .dat file formats and decryption processes continue to work
  - Verify no database migrations are required
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 11.1 Write property test for backward compatibility preservation
  - **Property 9: Backward Compatibility Preservation**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.5**

- [x] 12. Create comprehensive integration tests
  - Test complete .dat file upload and processing workflow with SECONDARY questions
  - Test admin interface displays secondary question sets correctly after classification fix
  - Test universal activation works end-to-end from UI to database
  - Test that primary and secondary workflows can be used together without conflicts
  - Test error scenarios and recovery mechanisms
  - _Requirements: All requirements integration testing_

- [ ]* 12.1 Write integration tests for complete workflows
  - Test end-to-end .dat file processing with SECONDARY classification
  - Test admin UI workflows for both primary and secondary question management
  - Test universal and individual activation working together

- [x] 13. Add comprehensive logging and monitoring
  - Add detailed logging for SECONDARY question detection during import
  - Add logging for universal activation operations (which trades updated, by whom, when)
  - Add error logging for failed operations with sufficient detail for debugging
  - Add performance monitoring for large-scale operations
  - _Requirements: 4.4, 4.5_

- [x] 14. Final checkpoint - Complete system validation
  - Run full test suite to ensure no regressions
  - Test with production-like data volumes (.dat files with 1000+ questions)
  - Verify all three critical issues are resolved:
    1. SECONDARY questions are correctly classified during import
    2. Secondary question sets are displayed in admin UI
    3. Universal set activation works for bulk operations
  - Test system stability under concurrent operations
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation maintains backward compatibility with existing workflows
- Property tests validate universal correctness properties across all question configurations
- Integration tests ensure all three fixes work together without conflicts
- Performance tests ensure the fixes don't introduce performance regressions
- The solution addresses all three critical issues: data import bug, UI filtering bug, and missing universal activation feature