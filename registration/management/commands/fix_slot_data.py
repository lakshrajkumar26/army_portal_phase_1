#!/usr/bin/env python
"""
Management command to fix slot data inconsistencies
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from registration.models import CandidateProfile

class Command(BaseCommand):
    help = 'Fix slot data inconsistencies where consumed_at exists but assigned_at is None'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without actually fixing'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No data will be actually fixed")
            )

        # Find candidates with consumed slots but no assignment date
        inconsistent_candidates = CandidateProfile.objects.filter(
            slot_consumed_at__isnull=False,
            slot_assigned_at__isnull=True
        )

        count = inconsistent_candidates.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("✅ No slot data inconsistencies found"))
            return

        self.stdout.write(f"Found {count} candidates with slot data inconsistencies:")
        
        for candidate in inconsistent_candidates:
            self.stdout.write(
                f"  - {candidate.army_no} ({candidate.name}): "
                f"consumed={candidate.slot_consumed_at}, assigned={candidate.slot_assigned_at}"
            )

        if not dry_run:
            with transaction.atomic():
                # Fix the inconsistency by setting assignment date to consumed date
                for candidate in inconsistent_candidates:
                    # Set assignment date to consumed date (or slightly before)
                    candidate.slot_assigned_at = candidate.slot_consumed_at
                    candidate.has_exam_slot = True  # Ensure this is set
                    candidate.save(update_fields=['slot_assigned_at', 'has_exam_slot'])
                    
                    self.stdout.write(
                        f"  ✅ Fixed {candidate.army_no}: set assigned_at = {candidate.slot_assigned_at}"
                    )

            self.stdout.write(
                self.style.SUCCESS(f"✅ Fixed {count} slot data inconsistencies")
            )
        else:
            self.stdout.write(
                self.style.WARNING("DRY RUN completed. Use without --dry-run to actually fix the data.")
            )