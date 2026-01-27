#!/usr/bin/env python
"""
Management command to clean up exam-related data with different levels of cleanup
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth import get_user_model
from questions.models import Question, QuestionPaper, ExamSession, ExamQuestion, TradePaperActivation, QuestionUpload
from results.models import CandidateAnswer
from registration.models import CandidateProfile
import os
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Clean up exam-related data with different levels of cleanup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--level',
            type=str,
            choices=['questions', 'exam-data', 'candidates', 'everything'],
            required=True,
            help='Level of cleanup: questions (only questions), exam-data (all exam data except users), candidates (only candidates), everything (complete reset)'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the deletion (required for safety)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        level = options['level']
        confirm = options['confirm']
        dry_run = options['dry_run']

        if not confirm and not dry_run:
            raise CommandError(
                "This command will delete data permanently. "
                "Use --confirm to proceed or --dry-run to see what would be deleted."
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No data will be actually deleted")
            )

        self.stdout.write(f"Cleanup level: {level}")
        self.stdout.write("=" * 50)

        if level == 'questions':
            self.cleanup_questions_only(dry_run)
        elif level == 'exam-data':
            self.cleanup_exam_data_only(dry_run)
        elif level == 'candidates':
            self.cleanup_candidates_only(dry_run)
        elif level == 'everything':
            self.cleanup_everything(dry_run)

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Cleanup completed successfully!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("DRY RUN completed. Use --confirm to actually delete the data.")
            )

    def cleanup_questions_only(self, dry_run=False):
        """Delete only questions and question papers"""
        self.stdout.write(self.style.WARNING("🗑️  QUESTIONS CLEANUP"))
        
        # Count items
        questions_count = Question.objects.count()
        papers_count = QuestionPaper.objects.count()
        uploads_count = QuestionUpload.objects.count()
        activations_count = TradePaperActivation.objects.count()
        exam_questions_count = ExamQuestion.objects.count()
        sessions_count = ExamSession.objects.count()
        answers_count = CandidateAnswer.objects.count()
        
        self.stdout.write(f"Candidate answers to delete: {answers_count}")
        self.stdout.write(f"Exam questions to delete: {exam_questions_count}")
        self.stdout.write(f"Exam sessions to delete: {sessions_count}")
        self.stdout.write(f"Questions to delete: {questions_count}")
        self.stdout.write(f"Question papers to delete: {papers_count}")
        self.stdout.write(f"Question uploads to delete: {uploads_count}")
        self.stdout.write(f"Trade activations to delete: {activations_count}")
        
        if not dry_run:
            with transaction.atomic():
                # Delete in proper order to avoid foreign key constraints
                # 1. Delete answers first (they reference questions)
                CandidateAnswer.objects.all().delete()
                
                # 2. Delete exam questions (they reference questions and sessions)
                ExamQuestion.objects.all().delete()
                
                # 3. Delete exam sessions
                ExamSession.objects.all().delete()
                
                # 4. Delete questions
                Question.objects.all().delete()
                
                # 5. Delete question papers
                QuestionPaper.objects.all().delete()
                
                # 6. Delete uploads and activations
                QuestionUpload.objects.all().delete()
                TradePaperActivation.objects.all().delete()
                
                # Clean up uploaded files
                self.cleanup_uploaded_files()
                
            self.stdout.write(self.style.SUCCESS("✅ Questions and papers deleted"))

    def cleanup_exam_data_only(self, dry_run=False):
        """Delete all exam-related data but keep user registrations"""
        self.stdout.write(self.style.WARNING("🗑️  EXAM DATA CLEANUP (Preserving Users)"))
        
        # Count items
        questions_count = Question.objects.count()
        papers_count = QuestionPaper.objects.count()
        uploads_count = QuestionUpload.objects.count()
        activations_count = TradePaperActivation.objects.count()
        sessions_count = ExamSession.objects.count()
        exam_questions_count = ExamQuestion.objects.count()
        answers_count = CandidateAnswer.objects.count()
        
        self.stdout.write(f"Candidate answers to delete: {answers_count}")
        self.stdout.write(f"Exam questions to delete: {exam_questions_count}")
        self.stdout.write(f"Exam sessions to delete: {sessions_count}")
        self.stdout.write(f"Questions to delete: {questions_count}")
        self.stdout.write(f"Question papers to delete: {papers_count}")
        self.stdout.write(f"Question uploads to delete: {uploads_count}")
        self.stdout.write(f"Trade activations to delete: {activations_count}")
        
        # Preserve counts
        users_count = User.objects.count()
        candidates_count = CandidateProfile.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f"Users to preserve: {users_count}"))
        self.stdout.write(self.style.SUCCESS(f"Candidate profiles to preserve: {candidates_count}"))
        
        if not dry_run:
            with transaction.atomic():
                # Delete exam-related data in proper order
                # 1. Delete answers first (they reference questions and candidates)
                CandidateAnswer.objects.all().delete()
                
                # 2. Delete exam questions (they reference questions and sessions)
                ExamQuestion.objects.all().delete()
                
                # 3. Delete exam sessions
                ExamSession.objects.all().delete()
                
                # 4. Delete questions
                Question.objects.all().delete()
                
                # 5. Delete question papers
                QuestionPaper.objects.all().delete()
                
                # 6. Delete uploads and activations
                QuestionUpload.objects.all().delete()
                TradePaperActivation.objects.all().delete()
                
                # 7. Reset exam slots for candidates (but keep candidates)
                CandidateProfile.objects.update(
                    has_exam_slot=False,
                    slot_assigned_at=None,
                    slot_consumed_at=None,
                    slot_assigned_by=None
                )
                
                # Clean up uploaded files
                self.cleanup_uploaded_files()
                
            self.stdout.write(self.style.SUCCESS("✅ Exam data deleted, users preserved"))

    def cleanup_candidates_only(self, dry_run=False):
        """Delete only candidate registrations and profiles"""
        self.stdout.write(self.style.WARNING("🗑️  CANDIDATES CLEANUP (Preserving Questions & Exam Data)"))
        
        # Count items
        candidates_count = CandidateProfile.objects.count()
        users_count = User.objects.filter(is_superuser=False, is_staff=False).count()
        answers_count = CandidateAnswer.objects.count()
        candidate_sessions_count = ExamSession.objects.filter(user__is_superuser=False, user__is_staff=False).count()
        candidate_exam_questions_count = ExamQuestion.objects.filter(session__user__is_superuser=False, session__user__is_staff=False).count()
        
        self.stdout.write(f"Candidate answers to delete: {answers_count}")
        self.stdout.write(f"Candidate exam questions to delete: {candidate_exam_questions_count}")
        self.stdout.write(f"Candidate exam sessions to delete: {candidate_sessions_count}")
        self.stdout.write(f"Candidate profiles to delete: {candidates_count}")
        self.stdout.write(f"Non-admin users to delete: {users_count}")
        
        # Preserve counts
        questions_count = Question.objects.count()
        papers_count = QuestionPaper.objects.count()
        admin_users_count = User.objects.filter(is_superuser=True).count() + User.objects.filter(is_staff=True).count()
        
        self.stdout.write(self.style.SUCCESS(f"Questions to preserve: {questions_count}"))
        self.stdout.write(self.style.SUCCESS(f"Question papers to preserve: {papers_count}"))
        self.stdout.write(self.style.SUCCESS(f"Admin users to preserve: {admin_users_count}"))
        
        if not dry_run:
            with transaction.atomic():
                # Delete candidate-related data in proper order
                # 1. Delete candidate answers first
                CandidateAnswer.objects.all().delete()
                
                # 2. Delete exam questions for candidate sessions
                ExamQuestion.objects.filter(session__user__is_superuser=False, session__user__is_staff=False).delete()
                
                # 3. Delete candidate exam sessions
                ExamSession.objects.filter(user__is_superuser=False, user__is_staff=False).delete()
                
                # 4. Delete candidate profiles
                CandidateProfile.objects.all().delete()
                
                # 5. Delete non-admin users
                User.objects.filter(is_superuser=False, is_staff=False).delete()
                
                # Clean up candidate photos
                self.cleanup_candidate_photos()
                
            self.stdout.write(self.style.SUCCESS("✅ Candidates deleted, questions and exam data preserved"))

    def cleanup_everything(self, dry_run=False):
        """Delete everything - complete reset"""
        self.stdout.write(self.style.ERROR("🗑️  COMPLETE CLEANUP (Everything will be deleted!)"))
        
        # Count all items
        questions_count = Question.objects.count()
        papers_count = QuestionPaper.objects.count()
        uploads_count = QuestionUpload.objects.count()
        activations_count = TradePaperActivation.objects.count()
        sessions_count = ExamSession.objects.count()
        exam_questions_count = ExamQuestion.objects.count()
        answers_count = CandidateAnswer.objects.count()
        users_count = User.objects.count()
        candidates_count = CandidateProfile.objects.count()
        
        self.stdout.write(f"Candidate answers to delete: {answers_count}")
        self.stdout.write(f"Exam questions to delete: {exam_questions_count}")
        self.stdout.write(f"Exam sessions to delete: {sessions_count}")
        self.stdout.write(f"Questions to delete: {questions_count}")
        self.stdout.write(f"Question papers to delete: {papers_count}")
        self.stdout.write(f"Question uploads to delete: {uploads_count}")
        self.stdout.write(f"Trade activations to delete: {activations_count}")
        self.stdout.write(f"Candidate profiles to delete: {candidates_count}")
        self.stdout.write(f"Users to delete: {users_count}")
        
        if not dry_run:
            with transaction.atomic():
                # Delete everything in proper order
                # 1. Delete answers first (they reference questions and candidates)
                CandidateAnswer.objects.all().delete()
                
                # 2. Delete exam questions (they reference questions and sessions)
                ExamQuestion.objects.all().delete()
                
                # 3. Delete exam sessions (they reference users and papers)
                ExamSession.objects.all().delete()
                
                # 4. Delete candidate profiles (they reference users)
                CandidateProfile.objects.all().delete()
                
                # 5. Delete questions
                Question.objects.all().delete()
                
                # 6. Delete question papers
                QuestionPaper.objects.all().delete()
                
                # 7. Delete uploads and activations
                QuestionUpload.objects.all().delete()
                TradePaperActivation.objects.all().delete()
                
                # 8. Delete users (except superusers for safety)
                User.objects.filter(is_superuser=False).delete()
                
                # Clean up uploaded files
                self.cleanup_uploaded_files()
                self.cleanup_media_files()
                
            self.stdout.write(self.style.SUCCESS("✅ Complete cleanup done (superusers preserved)"))

    def cleanup_uploaded_files(self):
        """Clean up uploaded question files"""
        try:
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'questions')
            if os.path.exists(upload_path):
                import shutil
                shutil.rmtree(upload_path)
                os.makedirs(upload_path, exist_ok=True)
                self.stdout.write("📁 Cleaned up uploaded question files")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not clean up uploaded files: {e}")
            )

    def cleanup_candidate_photos(self):
        """Clean up candidate photos"""
        try:
            photos_path = os.path.join(settings.MEDIA_ROOT, 'photos')
            if os.path.exists(photos_path):
                import shutil
                shutil.rmtree(photos_path)
                os.makedirs(photos_path, exist_ok=True)
                self.stdout.write("📁 Cleaned up candidate photos")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not clean up candidate photos: {e}")
            )

    def cleanup_media_files(self):
        """Clean up media files (photos, etc.)"""
        try:
            photos_path = os.path.join(settings.MEDIA_ROOT, 'photos')
            if os.path.exists(photos_path):
                import shutil
                shutil.rmtree(photos_path)
                os.makedirs(photos_path, exist_ok=True)
                self.stdout.write("📁 Cleaned up media files")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not clean up media files: {e}")
            )

    def get_confirmation(self, message):
        """Get user confirmation for dangerous operations"""
        response = input(f"{message} (yes/no): ")
        return response.lower() in ['yes', 'y']