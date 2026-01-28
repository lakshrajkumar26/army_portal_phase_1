# Implementation Plan: Secondary Question Display Fix

## Overview

This implementation plan addresses the critical bug where secondary questions are not displayed in the admin UI due to incorrect filtering logic in the `ActivateSets.get_available_sets()` method. The fix involves implementing paper-type-specific filtering logic while preserving existing primary question functionality.

## Tasks

- [ ] 1. Implement paper-type-specific filtering in get_available_sets method
  - Modify `ActivateSets.get_available_sets()` in `questions/models.py` to use conditional filtering based on paper_type
  - For SECONDARY: filter by paper_type='SECONDARY', is_common=True, is_active=True (no trade filter)
  - For PRIMARY: maintain existing trade-based filtering with paper_type='PRIMARY', is_active=True
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2_

- [ ]* 1.1 Write property test for secondary question filtering
  - **Property 1: Secondary Question Filtering**
  - **Validates: Requirements 1.1, 1.2, 1.3, 5.1**

- [ ]* 1.2 Write property test for primary question filtering
  - **Property 2: Primary Question Filtering**
  - **Validates: Requirements 1.4, 2.1, 2.2, 5.2**

- [ ] 2. Implement paper-type-specific filtering in get_question_count method
  - Modify `ActivateSets.get_question_count()` in `questions/models.py` to use the same conditional filtering logic
  - Ensure consistency with get_available_sets() filtering approach
  - For SECONDARY: count questions with paper_type='SECONDARY', is_common=True, question_set match, is_active=True
  - For PRIMARY: count questions with trade match, paper_type='PRIMARY', question_set match, is_active=True
  - _Requirements: 4.1, 4.2, 5.3_

- [ ]* 2.1 Write property test for question count accuracy
  - **Property 3: Question Count Accuracy**
  - **Validates: Requirements 1.5, 4.1, 4.2**

- [ ]* 2.2 Write property test for method consistency
  - **Property 5: Method Consistency**
  - **Validates: Requirements 5.3**

- [ ] 3. Add comprehensive active question filtering validation
  - Ensure both methods consistently apply is_active=True filtering
  - Add explicit checks to prevent inactive questions from being included in results
  - _Requirements: 2.3, 4.3, 5.4_

- [ ]* 3.1 Write property test for active question filtering
  - **Property 4: Active Question Filtering**
  - **Validates: Requirements 2.3, 4.3, 5.4**

- [ ] 4. Checkpoint - Verify core filtering logic
  - Run all property tests to ensure filtering logic works correctly
  - Test with sample data to verify secondary questions are now displayed
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Add error handling and edge case management
  - Add input validation for invalid paper_type values (default to PRIMARY)
  - Handle cases where ActivateSets has no associated trade for PRIMARY questions
  - Add null safety for question_set parameter in get_question_count()
  - _Requirements: Error handling requirements_

- [ ]* 5.1 Write unit tests for error handling
  - Test invalid paper_type inputs
  - Test null/missing trade scenarios
  - Test null question_set parameter handling

- [ ] 6. Create comprehensive integration test
  - Test the complete admin UI workflow with both PRIMARY and SECONDARY paper types
  - Verify that secondary question sets (A, B, C, D, E) are displayed when SECONDARY is selected
  - Verify that primary question functionality remains unchanged
  - Test question count accuracy in the admin interface
  - _Requirements: 1.1, 1.5, 2.1, 2.2_

- [ ]* 6.1 Write integration tests for admin UI
  - Test admin interface displays secondary question sets correctly
  - Test primary question workflows remain functional
  - Test question count display accuracy

- [ ] 7. Performance validation and optimization
  - Verify that existing database indexes support the new filtering patterns
  - Test query performance with large datasets
  - Ensure no performance regression for primary question filtering
  - _Requirements: 5.5_

- [ ]* 7.1 Write performance tests
  - Benchmark filtering performance with large question datasets
  - Compare performance before and after the fix

- [ ] 8. Final checkpoint - Complete system validation
  - Run full test suite to ensure no regressions
  - Test with production-like data volumes
  - Verify admin UI displays secondary questions correctly
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The fix maintains backward compatibility with existing primary question workflows
- Property tests validate universal correctness properties across all question configurations
- Integration tests ensure the admin UI works correctly after the fix
- Performance tests ensure the fix doesn't introduce performance regressions