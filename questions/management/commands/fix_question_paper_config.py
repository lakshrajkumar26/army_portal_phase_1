"""
Management command to fix missing QuestionPaper configurations.

This command ensures that QuestionPaper records exist for active paper types
and fixes the "Exam paper configuration missing" error.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from questions.models import GlobalPaperTypeControl, QuestionPaper, TradePaperActivation


class Command(BaseCommand):
    help = 'Fix missing QuestionPaper configurations for active paper types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Check for active GlobalPaperTypeControl records
        active_controls = GlobalPaperTypeControl.objects.filter(is_active=True)
        
        if not active_controls.exists():
            self.stdout.write(self.style.WARNING('No active GlobalPaperTypeControl records found'))
            
            # Check for active TradePaperActivation records as fallback
            active_trades = TradePaperActivation.objects.filter(is_active=True)
            if active_trades.exists():
                paper_types = active_trades.values_list('paper_type', flat=True).distinct()
                self.stdout.write(f'Found active TradePaperActivation records for: {list(paper_types)}')
                
                for paper_type in paper_types:
                    self._ensure_question_paper(paper_type, dry_run)
            else:
                self.stdout.write(self.style.ERROR('No active paper configurations found'))
                return
        else:
            for control in active_controls:
                self.stdout.write(f'Found active control: {control.paper_type}')
                self._ensure_question_paper(control.paper_type, dry_run)
        
        # Check for orphaned QuestionPaper records
        self._check_orphaned_question_papers(dry_run)
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS('QuestionPaper configuration fix completed'))
        else:
            self.stdout.write(self.style.SUCCESS('DRY RUN completed - use without --dry-run to apply changes'))

    def _ensure_question_paper(self, paper_type, dry_run):
        """Ensure QuestionPaper record exists and is active for the given paper type"""
        try:
            question_paper = QuestionPaper.objects.get(question_paper=paper_type)
            if not question_paper.is_active:
                self.stdout.write(f'  QuestionPaper for {paper_type} exists but is inactive')
                if not dry_run:
                    question_paper.is_active = True
                    question_paper.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Activated QuestionPaper for {paper_type}'))
                else:
                    self.stdout.write(f'  Would activate QuestionPaper for {paper_type}')
            else:
                self.stdout.write(self.style.SUCCESS(f'  ✓ QuestionPaper for {paper_type} is already active'))
        except QuestionPaper.DoesNotExist:
            self.stdout.write(f'  QuestionPaper for {paper_type} does not exist')
            if not dry_run:
                QuestionPaper.objects.create(
                    question_paper=paper_type,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created active QuestionPaper for {paper_type}'))
            else:
                self.stdout.write(f'  Would create QuestionPaper for {paper_type}')

    def _check_orphaned_question_papers(self, dry_run):
        """Check for QuestionPaper records that are active but shouldn't be"""
        active_paper_types = set()
        
        # Get paper types from GlobalPaperTypeControl
        for control in GlobalPaperTypeControl.objects.filter(is_active=True):
            active_paper_types.add(control.paper_type)
        
        # Get paper types from TradePaperActivation as fallback
        if not active_paper_types:
            for paper_type in TradePaperActivation.objects.filter(is_active=True).values_list('paper_type', flat=True).distinct():
                active_paper_types.add(paper_type)
        
        # Check for orphaned active QuestionPaper records
        orphaned = QuestionPaper.objects.filter(is_active=True).exclude(question_paper__in=active_paper_types)
        
        if orphaned.exists():
            self.stdout.write('Found orphaned active QuestionPaper records:')
            for qp in orphaned:
                self.stdout.write(f'  {qp.question_paper} (should be inactive)')
                if not dry_run:
                    qp.is_active = False
                    qp.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Deactivated orphaned QuestionPaper for {qp.question_paper}'))
                else:
                    self.stdout.write(f'  Would deactivate QuestionPaper for {qp.question_paper}')
        else:
            self.stdout.write(self.style.SUCCESS('  No orphaned QuestionPaper records found'))