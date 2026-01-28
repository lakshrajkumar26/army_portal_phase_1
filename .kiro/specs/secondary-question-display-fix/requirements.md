# Requirements Document

## Introduction

This specification addresses a critical bug in the question set management system where secondary questions exist in the database but are not displayed in the admin UI when toggling from primary to secondary paper type. The root cause is incorrect filtering logic in the `ActivateSets.get_available_sets()` method that applies trade-based filtering to secondary questions, which have `trade=NULL` and `is_common=True`.

## Glossary

- **System**: The question set management system
- **ActivateSets**: Django model that manages active question sets for each trade
- **Question**: Django model representing individual exam questions
- **Paper_Type**: Enum field indicating PRIMARY or SECONDARY question classification
- **Trade**: Specific vocational trade (e.g., Electrician, Plumber)
- **Question_Set**: Alphabetical identifier (A-Z) grouping questions within a paper type
- **Admin_UI**: Django admin interface for managing question sets
- **Secondary_Questions**: Questions with paper_type='SECONDARY', trade=NULL, and is_common=True
- **Primary_Questions**: Questions with paper_type='PRIMARY' and specific trade assignment

## Requirements

### Requirement 1: Fix Secondary Question Filtering

**User Story:** As an admin user, I want to see available secondary question sets when I toggle to SECONDARY paper type, so that I can activate and manage secondary question sets properly.

#### Acceptance Criteria

1. WHEN an admin selects SECONDARY paper type in the admin UI, THE System SHALL display all available secondary question sets (A, B, C, D, E)
2. WHEN filtering secondary questions, THE System SHALL use paper_type='SECONDARY' and is_common=True criteria only
3. WHEN filtering secondary questions, THE System SHALL NOT apply trade-based filtering
4. WHEN filtering primary questions, THE System SHALL continue using trade-based filtering with paper_type='PRIMARY'
5. WHEN secondary question sets are displayed, THE System SHALL show accurate question counts for each set

### Requirement 2: Preserve Primary Question Functionality

**User Story:** As an admin user, I want primary question filtering to continue working correctly, so that existing functionality remains unaffected by the secondary question fix.

#### Acceptance Criteria

1. WHEN an admin selects PRIMARY paper type, THE System SHALL filter questions by trade and paper_type='PRIMARY'
2. WHEN displaying primary question sets, THE System SHALL show only question sets belonging to the selected trade
3. WHEN counting primary questions, THE System SHALL include only active questions for the specific trade and paper type

### Requirement 3: Maintain Data Integrity

**User Story:** As a system administrator, I want the fix to preserve existing data relationships, so that no data is corrupted or lost during the implementation.

#### Acceptance Criteria

1. WHEN the filtering logic is updated, THE System SHALL preserve all existing Question records unchanged
2. WHEN the filtering logic is updated, THE System SHALL preserve all existing ActivateSets records unchanged
3. WHEN the fix is applied, THE System SHALL maintain backward compatibility with existing admin workflows

### Requirement 4: Validate Question Count Accuracy

**User Story:** As an admin user, I want accurate question counts displayed for both primary and secondary question sets, so that I can make informed decisions about question set activation.

#### Acceptance Criteria

1. WHEN displaying secondary question sets, THE System SHALL show correct question counts using secondary-specific filtering
2. WHEN displaying primary question sets, THE System SHALL show correct question counts using trade-specific filtering
3. WHEN question counts are calculated, THE System SHALL include only active questions (is_active=True)
4. WHEN question counts are zero, THE System SHALL display "0" rather than hiding the question set

### Requirement 5: Ensure Consistent Filtering Logic

**User Story:** As a developer, I want consistent filtering logic across all methods that handle question retrieval, so that the system behaves predictably and maintainably.

#### Acceptance Criteria

1. WHEN get_available_sets() is called with paper_type='SECONDARY', THE System SHALL apply secondary-specific filtering logic
2. WHEN get_available_sets() is called with paper_type='PRIMARY', THE System SHALL apply trade-specific filtering logic
3. WHEN get_question_count() is called, THE System SHALL use the same filtering logic as get_available_sets() for consistency
4. WHEN any question filtering occurs, THE System SHALL respect the is_active=True constraint
5. WHEN filtering logic is implemented, THE System SHALL use database indexes efficiently for performance