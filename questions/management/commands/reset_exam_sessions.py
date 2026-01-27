#!/usr/bin/env python
"""
Management command to reset exam sessions and results while keeping questions and users
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from questions.models import ExamSession
from results.models import CandidateAnswer
from registration.models import CandidateProfile

class Command(BaseCommand):
    help = 'Reset exam sessions and results while keeping questions and user data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the reset (required for safety)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reset without actually resetting'
        )
        parser.add_argument(
            '--trade',
            type=str,
            help='Reset sessions only for specific trade (optional)'
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        dry_run = options['dry_run']
        trade_filter = options.get('trade')

        if not confirm and not dry_run:
            raise CommandError(
                "This command will reset exam sessions and results permanently. "
                "Use --confirm to proceed or --dry-run to see what would be reset."
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No data will be actually reset")
            )

        self.stdout.write("🔄 EXAM SESSIONS RESET")
        self.stdout.write("=" * 50)

        # Build querysets
        sessions_query = ExamSession.objects.all()
        answers_query = CandidateAnswer.objects.all()

        if trade_filter:
            # Filter by trade
            candidate_ids = CandidateProfile.objects.filter(
                trade__name__icontains=trade_filter
            ).values_list('id', flat=True)
            
            sessions_query = sessions_query.filter(user__candidateprofile__id__in=candidate_ids)
            answers_query = answers_query.filter(candidate__id__in=candidate_ids)
            
            self.stdout.write(f"Filtering by trade: {trade_filter}")

        # Count items
        sessions_count = sessions_query.count()
        answers_count = answers_query.count()
        
        self.stdout.write(f"Exam sessions to reset: {sessions_count}")
        self.stdout.write(f"Candidate answers to delete: {answers_count}")

        if sessions_count == 0 and answers_count == 0:
            self.stdout.write(self.style.WARNING("No exam sessions or answers found to reset."))
            return

        # Show some details
        if sessions_count > 0:
            self.stdout.write("\nExam sessions details:")
            for session in sessions_query[:5]:  # Show first 5
                status = "Completed" if session.completed_at else "In Progress"
                self.stdout.write(f"  - Session {session.id}: {session.user.username} ({status})")
            
            if sessions_count > 5:
                self.stdout.write(f"  ... and {sessions_count - 5} more sessions")

        if not dry_run:
            with transaction.atomic():
                # Delete candidate answers first (foreign key dependency)
                deleted_answers = answers_query.delete()
                deleted_sessions = sessions_query.delete()
                
            self.stdout.write(
                self.style.SUCCESS(f"✅ Reset completed!")
            )
            self.stdout.write(f"   - Deleted {deleted_answers[0]} candidate answers")
            self.stdout.write(f"   - Deleted {deleted_sessions[0]} exam sessions")
            self.stdout.write("   - Questions and user data preserved")
        else:
            self.stdout.write(
                self.style.WARNING("DRY RUN completed. Use --confirm to actually reset the data.")
            )