#!/usr/bin/env python3
"""
Management command to clear incomplete exam sessions

This command helps resolve the question set persistence issue by clearing
incomplete ExamSession records that prevent candidates from getting updated
question sets.

Usage:
    python manage.py clear_incomplete_sessions --all
    python manage.py clear_incomplete_sessions --trade "TTC"
    python manage.py clear_incomplete_sessions --army-no "12345678"
    python manage.py clear_incomplete_sessions --paper-type "PRIMARY"
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from questions.models import ExamSession
from registration.models import CandidateProfile
from reference.models import Trade


class Command(BaseCommand):
    help = 'Clear incomplete exam sessions to resolve question set persistence issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all incomplete sessions (DANGER)',
        )
        parser.add_argument(
            '--trade',
            type=str,
            help='Clear incomplete sessions for specific trade',
        )
        parser.add_argument(
            '--army-no',
            type=str,
            help='Clear incomplete sessions for specific candidate by army number',
        )
        parser.add_argument(
            '--paper-type',
            type=str,
            choices=['PRIMARY', 'SECONDARY'],
            help='Clear incomplete sessions for specific paper type only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Incomplete Session Cleanup Tool')
        )
        self.stdout.write('=' * 50)

        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN MODE - No changes will be made')
            )

        try:
            if options['all']:
                self.clear_all_sessions(dry_run)
            elif options['trade']:
                self.clear_trade_sessions(options['trade'], options.get('paper_type'), dry_run)
            elif options['army_no']:
                self.clear_candidate_sessions(options['army_no'], options.get('paper_type'), dry_run)
            elif options['paper_type']:
                self.clear_paper_type_sessions(options['paper_type'], dry_run)
            else:
                self.show_statistics()
                
        except Exception as e:
            raise CommandError(f'Error during cleanup: {str(e)}')

    def clear_all_sessions(self, dry_run=False):
        """Clear all incomplete sessions"""
        query = ExamSession.objects.filter(completed_at__isnull=True)
        count = query.count()
        
        if count == 0:
            self.stdout.write('ℹ️ No incomplete sessions found')
            return
        
        self.stdout.write(f'Found {count} incomplete sessions')
        
        if not dry_run:
            with transaction.atomic():
                query.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Cleared {count} incomplete sessions')
            )
        else:
            self.stdout.write(f'Would clear {count} incomplete sessions')

    def clear_trade_sessions(self, trade_name, paper_type=None, dry_run=False):
        """Clear incomplete sessions for specific trade"""
        try:
            trade = Trade.objects.get(name__iexact=trade_name)
        except Trade.DoesNotExist:
            raise CommandError(f'Trade "{trade_name}" not found')

        candidates = CandidateProfile.objects.filter(trade=trade)
        total_count = 0
        
        for candidate in candidates:
            query = ExamSession.objects.filter(
                user=candidate.user,
                completed_at__isnull=True
            )
            
            if paper_type:
                query = query.filter(paper__question_paper=paper_type)
            
            count = query.count()
            total_count += count
            
            if count > 0 and not dry_run:
                with transaction.atomic():
                    query.delete()
                self.stdout.write(f'  Cleared {count} sessions for {candidate.army_no}')

        if total_count == 0:
            self.stdout.write(f'ℹ️ No incomplete sessions found for trade {trade.name}')
        else:
            action = 'Cleared' if not dry_run else 'Would clear'
            self.stdout.write(
                self.style.SUCCESS(f'✅ {action} {total_count} incomplete sessions for trade {trade.name}')
            )

    def clear_candidate_sessions(self, army_no, paper_type=None, dry_run=False):
        """Clear incomplete sessions for specific candidate"""
        try:
            candidate = CandidateProfile.objects.get(army_no=army_no)
        except CandidateProfile.DoesNotExist:
            raise CommandError(f'Candidate with army number "{army_no}" not found')

        query = ExamSession.objects.filter(
            user=candidate.user,
            completed_at__isnull=True
        )
        
        if paper_type:
            query = query.filter(paper__question_paper=paper_type)
        
        count = query.count()
        
        if count == 0:
            self.stdout.write(f'ℹ️ No incomplete sessions found for {candidate.name} ({army_no})')
            return
        
        if not dry_run:
            with transaction.atomic():
                query.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Cleared {count} incomplete sessions for {candidate.name} ({army_no})')
            )
        else:
            self.stdout.write(f'Would clear {count} incomplete sessions for {candidate.name} ({army_no})')

    def clear_paper_type_sessions(self, paper_type, dry_run=False):
        """Clear incomplete sessions for specific paper type"""
        query = ExamSession.objects.filter(
            completed_at__isnull=True,
            paper__question_paper=paper_type
        )
        count = query.count()
        
        if count == 0:
            self.stdout.write(f'ℹ️ No incomplete {paper_type} sessions found')
            return
        
        if not dry_run:
            with transaction.atomic():
                query.delete()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Cleared {count} incomplete {paper_type} sessions')
            )
        else:
            self.stdout.write(f'Would clear {count} incomplete {paper_type} sessions')

    def show_statistics(self):
        """Show statistics about incomplete sessions"""
        self.stdout.write('\n📊 Incomplete Session Statistics')
        self.stdout.write('-' * 30)
        
        total_incomplete = ExamSession.objects.filter(completed_at__isnull=True).count()
        self.stdout.write(f'Total incomplete sessions: {total_incomplete}')
        
        if total_incomplete == 0:
            return
        
        # Group by paper type
        from django.db.models import Count
        by_paper = ExamSession.objects.filter(
            completed_at__isnull=True
        ).values('paper__question_paper').annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write('\nBy paper type:')
        for item in by_paper:
            paper_type = item['paper__question_paper'] or 'Unknown'
            self.stdout.write(f'  {paper_type}: {item["count"]} sessions')
        
        # Group by trade
        by_trade = ExamSession.objects.filter(
            completed_at__isnull=True
        ).values('trade__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write('\nBy trade (top 10):')
        for item in by_trade[:10]:
            trade_name = item['trade__name'] or 'No Trade'
            self.stdout.write(f'  {trade_name}: {item["count"]} sessions')
        
        self.stdout.write('\n💡 Usage examples:')
        self.stdout.write('  Clear all: python manage.py clear_incomplete_sessions --all')
        self.stdout.write('  Clear trade: python manage.py clear_incomplete_sessions --trade "TTC"')
        self.stdout.write('  Clear candidate: python manage.py clear_incomplete_sessions --army-no "12345678"')
        self.stdout.write('  Dry run: python manage.py clear_incomplete_sessions --all --dry-run')