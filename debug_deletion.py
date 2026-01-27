#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from registration.models import CandidateProfile
from questions.models import Question, QuestionPaper, ExamSession, ExamQuestion
from results.models import CandidateAnswer

print("=== DATABASE DELETION DEBUG ===")
print()

# Check current counts before deletion
print("BEFORE DELETION COUNTS:")
print(f"CandidateProfile: {CandidateProfile.objects.count()}")
print(f"Question: {Question.objects.count()}")
print(f"QuestionPaper: {QuestionPaper.objects.count()}")
print(f"ExamSession: {ExamSession.objects.count()}")
print(f"ExamQuestion: {ExamQuestion.objects.count()}")
print(f"CandidateAnswer: {CandidateAnswer.objects.count()}")
print()

# Test deletion of questions only
print("=== TESTING QUESTION DELETION ===")
question_count_before = Question.objects.count()
print(f"Questions before: {question_count_before}")

if question_count_before > 0:
    # Try to delete questions
    try:
        # Delete exam questions first (dependency)
        exam_question_deleted = ExamQuestion.objects.all().delete()
        print(f"ExamQuestion deleted: {exam_question_deleted}")
        
        # Delete exam sessions
        exam_session_deleted = ExamSession.objects.all().delete()
        print(f"ExamSession deleted: {exam_session_deleted}")
        
        # Delete candidate answers
        answer_deleted = CandidateAnswer.objects.all().delete()
        print(f"CandidateAnswer deleted: {answer_deleted}")
        
        # Now delete questions
        question_deleted = Question.objects.all().delete()
        print(f"Question deleted: {question_deleted}")
        
    except Exception as e:
        print(f"Error during deletion: {e}")
        import traceback
        traceback.print_exc()

print()
print("AFTER DELETION COUNTS:")
print(f"CandidateProfile: {CandidateProfile.objects.count()}")
print(f"Question: {Question.objects.count()}")
print(f"QuestionPaper: {QuestionPaper.objects.count()}")
print(f"ExamSession: {ExamSession.objects.count()}")
print(f"ExamQuestion: {ExamQuestion.objects.count()}")
print(f"CandidateAnswer: {CandidateAnswer.objects.count()}")

# Check database connection
from django.db import connection
print()
print("=== DATABASE INFO ===")
print(f"Database engine: {connection.settings_dict['ENGINE']}")
print(f"Database name: {connection.settings_dict['NAME']}")

# Test with raw SQL to see if data is actually there
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM registration_candidateprofile")
    raw_count = cursor.fetchone()[0]
    print(f"Raw SQL count for candidates: {raw_count}")
    
    cursor.execute("SELECT COUNT(*) FROM questions_question")
    raw_question_count = cursor.fetchone()[0]
    print(f"Raw SQL count for questions: {raw_question_count}")
