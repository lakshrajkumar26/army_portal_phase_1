#!/usr/bin/env python
"""
Management command to clean up exam-related data with proper cascade handling and debug logging
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from questions.models import Question, QuestionPaper, ExamSession, ExamQuestion, TradePaperActivation, QuestionUpload
from results.models import CandidateAnswer
from registration.models import CandidateProfile
import os
import logging
from django.conf import settings

User = get_user_model()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up exam-related data with proper cascade handling and debug logging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--level',
            type=str,
            choices=['exam-data', 'everything'],
            required=True,
            help='Level of cleanup: exam-data (all exam data except users), everything (complete reset)'
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
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )

    def handle(self, *args, **options):
        level = options['level']
        confirm = options['confirm']
        dry_run = options['dry_run']
        debug = options['debug']

        if debug:
            logger.setLevel(logging.DEBUG)
            self.stdout.write("🐛 DEBUG MODE ENABLED")

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

        try:
            if level == 'exam-data':
                self.cleanup_exam_data_only(dry_run, debug)
            elif level == 'everything':
                self.cleanup_everything(dry_run, debug)

            if not dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Cleanup completed successfully!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("DRY RUN completed. Use --confirm to actually delete the data.")
                )
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"❌ Cleanup failed: {str(e)}")
            )
            raise

    def log_debug(self, message, debug=False):
        """Log debug message if debug mode is enabled"""
        if debug:
            logger.debug(message)
            self.stdout.write(f"🐛 DEBUG: {message}")

    def safe_delete_with_cascade(self, model_class, description, dry_run=False, debug=False):
        """Safely delete model instances with proper cascade handling"""
        try:
            count = model_class.objects.count()
            self.log_debug(f"Found {count} {description} to delete", debug)
            
            if count > 0:
                self.stdout.write(f"{description} to delete: {count}")
                
                if not dry_run:
                    # Use raw SQL to disable foreign key checks temporarily
                    with connection.cursor() as cursor:
                        # For MySQL - disable foreign key checks
                        if 'mysql' in connection.vendor:
                            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                            self.log_debug("Disabled MySQL foreign key checks", debug)
                        
                        try:
                            # Delete the records using Django ORM (which handles cascades properly)
                            deleted_count, deleted_details = model_class.objects.all().delete()
                            self.log_debug(f"Deleted {deleted_count} {description} with details: {deleted_details}", debug)
                            
                            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_count} {description}"))
                            
                            # Log detailed deletion info if debug is enabled
                            if debug and deleted_details:
                                for model_name, count in deleted_details.items():
                                    if count > 0:
                                        self.log_debug(f"  - {model_name}: {count} records", debug)
                        
                        except Exception as delete_error:
                            self.log_debug(f"Django ORM deletion failed, trying raw SQL: {delete_error}", debug)
                            
                            # Fallback: Use raw SQL deletion
                            table_name = model_class._meta.db_table
                            cursor.execute(f"DELETE FROM {table_name}")
                            deleted_count = cursor.rowcount
                            self.log_debug(f"Raw SQL deleted {deleted_count} records from {table_name}", debug)
                            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_count} {description} (via raw SQL)"))
                        
                        finally:
                            # Re-enable foreign key checks
                            if 'mysql' in connection.vendor:
                                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                                self.log_debug("Re-enabled MySQL foreign key checks", debug)
                else:
                    self.stdout.write(f"Would delete {count} {description}")
            else:
                self.stdout.write(f"No {description} found")
                
        except Exception as e:
            logger.error(f"Error deleting {description}: {str(e)}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"❌ Error deleting {description}: {str(e)}")
            )
            raise

    def cleanup_exam_data_only(self, dry_run=False, debug=False):
        """Delete all exam-related data but keep user registrations"""
        self.stdout.write(self.style.WARNING("🗑️  EXAM DATA CLEANUP (Preserving Users)"))
        
        self.log_debug("Starting exam data cleanup", debug)
        
        if not dry_run:
            with transaction.atomic():
                self.log_debug("Starting database transaction", debug)
                
                # Delete in proper order to handle foreign key constraints
                # 1. Delete candidate answers first (they reference questions and candidates)
                self.safe_delete_with_cascade(CandidateAnswer, "candidate answers", dry_run, debug)
                
                # 2. Delete exam questions (they reference questions and sessions)
                self.safe_delete_with_cascade(ExamQuestion, "exam questions", dry_run, debug)
                
                # 3. Delete exam sessions (they reference users and papers)
                self.safe_delete_with_cascade(ExamSession, "exam sessions", dry_run, debug)
                
                # 4. Delete questions (they reference papers and trades)
                self.safe_delete_with_cascade(Question, "questions", dry_run, debug)
                
                # 5. Delete question papers
                self.safe_delete_with_cascade(QuestionPaper, "question papers", dry_run, debug)
                
                # 6. Delete uploads and activations
                self.safe_delete_with_cascade(QuestionUpload, "question uploads", dry_run, debug)
                self.safe_delete_with_cascade(TradePaperActivation, "trade paper activations", dry_run, debug)
                
                # 7. Reset exam slots for candidates (but keep candidates)
                try:
                    candidates_with_slots = CandidateProfile.objects.filter(has_exam_slot=True).count()
                    self.stdout.write(f"Candidates with slots to reset: {candidates_with_slots}")
                    
                    if candidates_with_slots > 0:
                        CandidateProfile.objects.update(
                            has_exam_slot=False,
                            slot_assigned_at=None,
                            slot_consumed_at=None,
                            slot_assigned_by=None,
                            exam_slot_from=None,
                            exam_slot_to=None
                        )
                        self.stdout.write(self.style.SUCCESS(f"✅ Reset {candidates_with_slots} exam slots"))
                        self.log_debug(f"Reset exam slots for {candidates_with_slots} candidates", debug)
                except Exception as e:
                    logger.error(f"Error resetting exam slots: {str(e)}", exc_info=True)
                    self.stdout.write(self.style.WARNING(f"⚠️  Could not reset exam slots: {e}"))
                
                # 8. Clean up uploaded files
                self.cleanup_uploaded_files(debug)
                
                self.log_debug("Database transaction completed successfully", debug)
        else:
            # Dry run - just count items
            self.safe_delete_with_cascade(CandidateAnswer, "candidate answers", dry_run, debug)
            self.safe_delete_with_cascade(ExamQuestion, "exam questions", dry_run, debug)
            self.safe_delete_with_cascade(ExamSession, "exam sessions", dry_run, debug)
            self.safe_delete_with_cascade(Question, "questions", dry_run, debug)
            self.safe_delete_with_cascade(QuestionPaper, "question papers", dry_run, debug)
            self.safe_delete_with_cascade(QuestionUpload, "question uploads", dry_run, debug)
            self.safe_delete_with_cascade(TradePaperActivation, "trade paper activations", dry_run, debug)
            
            candidates_with_slots = CandidateProfile.objects.filter(has_exam_slot=True).count()
            self.stdout.write(f"Candidates with slots to reset: {candidates_with_slots}")
        
        # Preserve counts
        users_count = User.objects.count()
        candidates_count = CandidateProfile.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f"Users preserved: {users_count}"))
        self.stdout.write(self.style.SUCCESS(f"Candidate profiles preserved: {candidates_count}"))

    def cleanup_everything(self, dry_run=False, debug=False):
        """Delete everything - complete reset"""
        self.stdout.write(self.style.ERROR("🗑️  COMPLETE CLEANUP (Everything will be deleted!)"))
        
        self.log_debug("Starting complete cleanup", debug)
        
        if not dry_run:
            with transaction.atomic():
                self.log_debug("Starting database transaction for complete cleanup", debug)
                
                # Delete everything in proper order
                # 1. Delete candidate answers first (they reference questions and candidates)
                self.safe_delete_with_cascade(CandidateAnswer, "candidate answers", dry_run, debug)
                
                # 2. Delete exam questions (they reference questions and sessions)
                self.safe_delete_with_cascade(ExamQuestion, "exam questions", dry_run, debug)
                
                # 3. Delete exam sessions (they reference users and papers)
                self.safe_delete_with_cascade(ExamSession, "exam sessions", dry_run, debug)
                
                # 4. Delete candidate profiles (they reference users)
                self.safe_delete_with_cascade(CandidateProfile, "candidate profiles", dry_run, debug)
                
                # 5. Delete questions
                self.safe_delete_with_cascade(Question, "questions", dry_run, debug)
                
                # 6. Delete question papers
                self.safe_delete_with_cascade(QuestionPaper, "question papers", dry_run, debug)
                
                # 7. Delete uploads and activations
                self.safe_delete_with_cascade(QuestionUpload, "question uploads", dry_run, debug)
                self.safe_delete_with_cascade(TradePaperActivation, "trade paper activations", dry_run, debug)
                
                # 8. Delete users (except superusers for safety)
                try:
                    non_admin_users = User.objects.filter(is_superuser=False)
                    user_count = non_admin_users.count()
                    self.stdout.write(f"Non-admin users to delete: {user_count}")
                    
                    if user_count > 0:
                        deleted_users = non_admin_users.delete()[0]
                        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_users} non-admin users"))
                        self.log_debug(f"Deleted {deleted_users} non-admin users", debug)
                    
                    # Preserve superusers
                    superuser_count = User.objects.filter(is_superuser=True).count()
                    self.stdout.write(self.style.SUCCESS(f"Superusers preserved: {superuser_count}"))
                    
                except Exception as e:
                    logger.error(f"Error deleting users: {str(e)}", exc_info=True)
                    self.stdout.write(self.style.ERROR(f"❌ Error deleting users: {str(e)}"))
                    raise
                
                # 9. Clean up uploaded files
                self.cleanup_uploaded_files(debug)
                self.cleanup_media_files(debug)
                
                self.log_debug("Complete cleanup transaction completed successfully", debug)
        else:
            # Dry run - just count items
            self.safe_delete_with_cascade(CandidateAnswer, "candidate answers", dry_run, debug)
            self.safe_delete_with_cascade(ExamQuestion, "exam questions", dry_run, debug)
            self.safe_delete_with_cascade(ExamSession, "exam sessions", dry_run, debug)
            self.safe_delete_with_cascade(CandidateProfile, "candidate profiles", dry_run, debug)
            self.safe_delete_with_cascade(Question, "questions", dry_run, debug)
            self.safe_delete_with_cascade(QuestionPaper, "question papers", dry_run, debug)
            self.safe_delete_with_cascade(QuestionUpload, "question uploads", dry_run, debug)
            self.safe_delete_with_cascade(TradePaperActivation, "trade paper activations", dry_run, debug)
            
            non_admin_users = User.objects.filter(is_superuser=False).count()
            superuser_count = User.objects.filter(is_superuser=True).count()
            self.stdout.write(f"Non-admin users to delete: {non_admin_users}")
            self.stdout.write(f"Superusers to preserve: {superuser_count}")

    def cleanup_uploaded_files(self, debug=False):
        """Clean up uploaded question files"""
        try:
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'questions')
            self.log_debug(f"Checking upload path: {upload_path}", debug)
            
            if os.path.exists(upload_path):
                import shutil
                shutil.rmtree(upload_path)
                os.makedirs(upload_path, exist_ok=True)
                self.stdout.write("📁 Cleaned up uploaded question files")
                self.log_debug("Successfully cleaned up uploaded question files", debug)
            else:
                self.log_debug("Upload path does not exist", debug)
        except Exception as e:
            logger.error(f"Could not clean up uploaded files: {str(e)}", exc_info=True)
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not clean up uploaded files: {e}")
            )

    def cleanup_media_files(self, debug=False):
        """Clean up media files (photos, etc.)"""
        try:
            photos_path = os.path.join(settings.MEDIA_ROOT, 'photos')
            self.log_debug(f"Checking photos path: {photos_path}", debug)
            
            if os.path.exists(photos_path):
                import shutil
                shutil.rmtree(photos_path)
                os.makedirs(photos_path, exist_ok=True)
                self.stdout.write("📁 Cleaned up media files")
                self.log_debug("Successfully cleaned up media files", debug)
            else:
                self.log_debug("Photos path does not exist", debug)
        except Exception as e:
            logger.error(f"Could not clean up media files: {str(e)}", exc_info=True)
            self.stdout.write(
                self.style.WARNING(f"⚠️  Could not clean up media files: {e}")
            )