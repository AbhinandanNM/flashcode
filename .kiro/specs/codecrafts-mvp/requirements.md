# Requirements Document

## Introduction

CodeCrafts is an educational programming platform similar to Duolingo but focused on teaching programming languages (starting with Python and C++). The platform provides a gamified learning experience with brief theory lessons followed by immediate practice questions, spaced repetition for memory retention, and competitive features like XP, streaks, leaderboards, and duels. The MVP will run locally using a full-stack web application architecture.

## Requirements

### Requirement 1: User Authentication and Profile Management

**User Story:** As a learner, I want to create an account and manage my profile, so that I can track my learning progress and compete with others.

#### Acceptance Criteria

1. WHEN a new user visits the platform THEN the system SHALL provide registration functionality with username, email, and password
2. WHEN a user provides valid credentials THEN the system SHALL authenticate using JWT tokens
3. WHEN a user logs in THEN the system SHALL display their profile with XP, streak count, and join date
4. WHEN a user completes daily activities THEN the system SHALL maintain and display their learning streak
5. IF a user misses a day THEN the system SHALL reset their streak to zero

### Requirement 2: Lesson Content Management

**User Story:** As a learner, I want to access structured programming lessons with theory and practice, so that I can learn programming concepts effectively.

#### Acceptance Criteria

1. WHEN a user selects a lesson THEN the system SHALL display brief theory content (under 30 seconds read time)
2. WHEN theory is completed THEN the system SHALL immediately present practice questions
3. WHEN a lesson is created THEN the system SHALL support Python and C++ programming languages
4. WHEN lessons are organized THEN the system SHALL categorize them by programming language and difficulty
5. WHEN a user accesses lessons THEN the system SHALL track their progress status (started/completed)

### Requirement 3: Interactive Question System

**User Story:** As a learner, I want to answer different types of programming questions, so that I can practice and reinforce my learning.

#### Acceptance Criteria

1. WHEN a lesson presents questions THEN the system SHALL support multiple choice questions (MCQ)
2. WHEN a lesson presents questions THEN the system SHALL support fill-in-the-blank questions
3. WHEN a lesson presents questions THEN the system SHALL support flashcard-style questions
4. WHEN a lesson presents questions THEN the system SHALL support code editor challenges
5. WHEN a user submits an answer THEN the system SHALL provide immediate feedback on correctness
6. WHEN questions are created THEN the system SHALL assign difficulty levels

### Requirement 4: Code Execution Environment

**User Story:** As a learner, I want to write and execute code in the browser, so that I can practice programming without setting up a local environment.

#### Acceptance Criteria

1. WHEN a code challenge is presented THEN the system SHALL provide an integrated code editor
2. WHEN a user submits code THEN the system SHALL execute it using Judge0 API or local Docker sandbox
3. WHEN code execution completes THEN the system SHALL compare output with expected results
4. WHEN code execution fails THEN the system SHALL display error messages and debugging hints
5. WHEN code is correct THEN the system SHALL award appropriate XP points

### Requirement 5: Spaced Repetition and Flashcards

**User Story:** As a learner, I want to review previously failed questions at optimal intervals, so that I can improve long-term retention.

#### Acceptance Criteria

1. WHEN a user answers incorrectly THEN the system SHALL schedule the question for future review
2. WHEN scheduling reviews THEN the system SHALL use spaced repetition algorithms
3. WHEN a user accesses flashcards THEN the system SHALL present questions due for review
4. WHEN a question is reviewed THEN the system SHALL update the last_reviewed timestamp
5. WHEN review performance improves THEN the system SHALL increase the review interval

### Requirement 6: Gamification System

**User Story:** As a learner, I want to earn points and compete with others, so that I stay motivated to continue learning.

#### Acceptance Criteria

1. WHEN a user completes a lesson THEN the system SHALL award XP points based on difficulty
2. WHEN a user answers questions correctly THEN the system SHALL award bonus XP
3. WHEN a user maintains daily activity THEN the system SHALL increment their streak counter
4. WHEN users earn XP THEN the system SHALL update weekly leaderboards
5. WHEN leaderboards are displayed THEN the system SHALL rank users by total XP

### Requirement 7: Competitive Duels

**User Story:** As a learner, I want to participate in timed coding challenges against other users, so that I can test my skills competitively.

#### Acceptance Criteria

1. WHEN a user initiates a duel THEN the system SHALL match them with another user or bot
2. WHEN a duel starts THEN the system SHALL present identical coding challenges to both participants
3. WHEN participants submit solutions THEN the system SHALL evaluate correctness and speed
4. WHEN a duel completes THEN the system SHALL declare a winner and award bonus XP
5. WHEN no human opponent is available THEN the system SHALL provide bot opponents

### Requirement 8: Local Development Environment

**User Story:** As a developer, I want to run the entire application locally, so that I can develop and test features without external dependencies.

#### Acceptance Criteria

1. WHEN the application is deployed THEN the system SHALL use Docker Compose for orchestration
2. WHEN services start THEN the frontend SHALL be accessible at http://localhost:3000
3. WHEN services start THEN the backend API SHALL be accessible at http://localhost:8000
4. WHEN the database initializes THEN the system SHALL use PostgreSQL or SQLite for data persistence
5. WHEN the application builds THEN the system SHALL complete setup with a single docker-compose command

### Requirement 9: Sample Content Implementation

**User Story:** As a learner, I want to access a complete Python Loops lesson, so that I can experience the full learning flow.

#### Acceptance Criteria

1. WHEN the MVP launches THEN the system SHALL include a complete "Python Loops" lesson
2. WHEN the Python Loops lesson loads THEN the system SHALL present theory about for and while loops
3. WHEN theory completes THEN the system SHALL present MCQ, fill-blank, flashcard, and code editor questions
4. WHEN code challenges are presented THEN the system SHALL include loop-writing exercises
5. WHEN the lesson completes THEN the system SHALL demonstrate the full learning flow from theory to practice