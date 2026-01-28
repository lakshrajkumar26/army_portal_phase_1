"""
Django management command to debug question set assignments.

Usage:
    python manage.py debug_question_sets
    python manage.py debug_question_sets --trade TTC
    python manage.py debug_question_sets --fix
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from questions.models import (
    Question, QuestionSetActivation, ActivateSets, 
    TradePaperActivation, GlobalPaperTypeControl
)
from reference.models import Trade
from registration.models import CandidateProfile


class Command(BaseCommand):
    help = 'Debug question set assignments and fix issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--trade',
            type=str,
            help='Specific trade to debug (e.g., TTC, OCC)'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix question set assignment issues'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information'
        )

    def handle(self, *args, **options):
        trade_name = options.get('trade')
        fix_issues = options.get('fix')
        verbose = options.get('verbose')
        
        self.stdout.write(
            self.style.SUCCESS('🔍 Debugging Question Set Assignments...')
        )
        
        # Check global paper type control
        self._check_global_controls()
        
        # Check question availability
        self._check_question_availability(trade_name, verbose)
        
        # Check question set activations
        self._check_question_set_activations(trade_name, verbose)
        
        # Check ActivateSets synchronization
        self._check_activate_sets_sync(trade_name, verbose)
        
        # Test question generation
        self._test_question_generation(trade_name, verbose)
        
        if fix_issues:
            self._fix_issues(trade_name)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Question set debugging completed')
        )

    def _check_global_controls(self):
        """Check global paper type controls"""
        self.stdout.write('\n📋 Global Paper Type Controls:')
        
        controls = GlobalPaperTypeControl.objects.all()
        if not controls.exists():
            self.stdout.write(self.style.WARNING('  ⚠️  No global controls found'))
            return
        
        for control in controls:
            status = '✅ ACTIVE' if control.is_active else '⚪ INACTIVE'
            self.stdout.write(f'  {status} {control.paper_type}')
            if control.is_active:
                self.stdout.write(f'    Last activated: {control.last_activated}')
                self.stdout.write(f'    Activated by: {control.activated_by}')

    def _check_question_availability(self, trade_name, verbose):
        """Check question availability by trade and set"""
        self.stdout.write('\n📚 Question Availability:')
        
        trades = Trade.objects.all()
        if trade_name:
            trades = trades.filter(name__icontains=trade_name)
        
        for trade in trades:
            self.stdout.write(f'\n  🏷️  Trade: {trade.name} ({trade.code})')
            
            # Check PRIMARY questions
            primary_questions = Question.objects.filter(
                trade=trade,
                paper_type='PRIMARY',
                is_active=True
            )
            
            primary_sets = primary_questions.values_list('question_set', flat=True).distinct()
            self.stdout.write(f'    PRIMARY: {primary_questions.count()} questions in sets {list(primary_sets)}')
            
            if verbose:
                for question_set in primary_sets:
                    count = primary_questions.filter(question_set=question_set).count()
                    self.stdout.write(f'      Set {question_set}: {count} questions')
            
            # Check SECONDARY questions (by trade code in text)
            secondary_questions = Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                is_active=True,
                text__icontains=trade.code.upper()
            )
            
            secondary_sets = secondary_questions.values_list('question_set', flat=True).distinct()
            self.stdout.write(f'    SECONDARY: {secondary_questions.count()} questions in sets {list(secondary_sets)}')
            
            if verbose:
                for question_set in secondary_sets:
                    count = secondary_questions.filter(question_set=question_set).count()
                    self.stdout.write(f'      Set {question_set}: {count} questions')

    def _check_question_set_activations(self, trade_name, verbose):
        """Check QuestionSetActivation records"""
        self.stdout.write('\n🎯 Question Set Activations:')
        
        trades = Trade.objects.all()
        if trade_name:
            trades = trades.filter(name__icontains=trade_name)
        
        for trade in trades:
            self.stdout.write(f'\n  🏷️  Trade: {trade.name}')
            
            activations = QuestionSetActivation.objects.filter(trade=trade)
            if not activations.exists():
                self.stdout.write(self.style.WARNING('    ⚠️  No activations found'))
                continue
            
            for activation in activations:
                status = '✅ ACTIVE' if activation.is_active else '⚪ INACTIVE'
                self.stdout.write(f'    {status} {activation.paper_type} Set {activation.question_set}')
                if verbose and activation.is_active:
                    self.stdout.write(f'      Activated: {activation.activated_at}')
                    self.stdout.write(f'      By: {activation.activated_by}')

    def _check_activate_sets_sync(self, trade_name, verbose):
        """Check ActivateSets synchronization"""
        self.stdout.write('\n🔄 ActivateSets Synchronization:')
        
        trades = Trade.objects.all()
        if trade_name:
            trades = trades.filter(name__icontains=trade_name)
        
        for trade in trades:
            self.stdout.write(f'\n  🏷️  Trade: {trade.name}')
            
            try:
                activate_sets = ActivateSets.objects.get(trade=trade)
                self.stdout.write(f'    PRIMARY Set: {activate_sets.active_primary_set}')
                self.stdout.write(f'    SECONDARY Set: {activate_sets.active_secondary_set}')
                self.stdout.write(f'    Last updated: {activate_sets.last_updated}')
                
                # Check if it matches QuestionSetActivation
                try:
                    primary_activation = QuestionSetActivation.objects.get(
                        trade=trade, paper_type='PRIMARY', is_active=True
                    )
                    if primary_activation.question_set != activate_sets.active_primary_set:
                        self.stdout.write(self.style.ERROR(
                            f'    ❌ PRIMARY MISMATCH: ActivateSets={activate_sets.active_primary_set}, '
                            f'QuestionSetActivation={primary_activation.question_set}'
                        ))
                    else:
                        self.stdout.write('    ✅ PRIMARY synchronized')
                except QuestionSetActivation.DoesNotExist:
                    self.stdout.write(self.style.WARNING('    ⚠️  No PRIMARY QuestionSetActivation found'))
                
                try:
                    secondary_activation = QuestionSetActivation.objects.get(
                        trade=trade, paper_type='SECONDARY', is_active=True
                    )
                    if secondary_activation.question_set != activate_sets.active_secondary_set:
                        self.stdout.write(self.style.ERROR(
                            f'    ❌ SECONDARY MISMATCH: ActivateSets={activate_sets.active_secondary_set}, '
                            f'QuestionSetActivation={secondary_activation.question_set}'
                        ))
                    else:
                        self.stdout.write('    ✅ SECONDARY synchronized')
                except QuestionSetActivation.DoesNotExist:
                    self.stdout.write(self.style.WARNING('    ⚠️  No SECONDARY QuestionSetActivation found'))
                
            except ActivateSets.DoesNotExist:
                self.stdout.write(self.style.WARNING('    ⚠️  No ActivateSets record found'))

    def _test_question_generation(self, trade_name, verbose):
        """Test question generation for a sample candidate"""
        self.stdout.write('\n🧪 Testing Question Generation:')
        
        # Get a sample candidate
        candidate = CandidateProfile.objects.first()
        if not candidate:
            self.stdout.write(self.style.WARNING('  ⚠️  No candidates found for testing'))
            return
        
        trade = candidate.trade
        if trade_name:
            try:
                trade = Trade.objects.get(name__icontains=trade_name)
                # Update candidate's trade for testing
                candidate.trade = trade
            except Trade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'  ❌ Trade {trade_name} not found'))
                return
        
        if not trade:
            self.stdout.write(self.style.WARNING('  ⚠️  Candidate has no trade assigned'))
            return
        
        self.stdout.write(f'  Testing with candidate: {candidate.name} (Trade: {trade.name})')
        
        # Check what paper type is active
        try:
            activation = TradePaperActivation.objects.get(trade=trade, is_active=True)
            paper_type = activation.paper_type
            self.stdout.write(f'  Active paper type: {paper_type}')
        except TradePaperActivation.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠️  No active paper type for this trade'))
            return
        
        # Check what question set should be used
        try:
            question_set_activation = QuestionSetActivation.objects.get(
                trade=trade,
                paper_type=paper_type,
                is_active=True
            )
            expected_set = question_set_activation.question_set
            self.stdout.write(f'  Expected question set: {expected_set}')
        except QuestionSetActivation.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'  ⚠️  No active question set for {trade.name} {paper_type}'))
            expected_set = 'A'  # Default fallback
            self.stdout.write(f'  Using fallback set: {expected_set}')
        
        # Test question filtering
        if paper_type == 'PRIMARY':
            questions = Question.objects.filter(
                trade=trade,
                paper_type='PRIMARY',
                question_set=expected_set,
                is_active=True
            )
        else:
            questions = Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                question_set=expected_set,
                is_active=True,
                text__icontains=trade.code.upper()
            )
        
        self.stdout.write(f'  Available questions in Set {expected_set}: {questions.count()}')
        
        if verbose and questions.exists():
            # Show sample questions
            sample_questions = questions[:3]
            for q in sample_questions:
                self.stdout.write(f'    - {q.part}: {q.text[:50]}...')

    def _fix_issues(self, trade_name):
        """Attempt to fix common issues"""
        self.stdout.write('\n🔧 Fixing Issues:')
        
        trades = Trade.objects.all()
        if trade_name:
            trades = trades.filter(name__icontains=trade_name)
        
        fixed_count = 0
        
        with transaction.atomic():
            for trade in trades:
                # Ensure ActivateSets record exists
                activate_sets, created = ActivateSets.objects.get_or_create(
                    trade=trade,
                    defaults={
                        'active_primary_set': 'A',
                        'active_secondary_set': 'A',
                    }
                )
                
                if created:
                    self.stdout.write(f'  ✅ Created ActivateSets for {trade.name}')
                    fixed_count += 1
                
                # Ensure QuestionSetActivation records exist and are synchronized
                for paper_type in ['PRIMARY', 'SECONDARY']:
                    expected_set = (activate_sets.active_primary_set 
                                  if paper_type == 'PRIMARY' 
                                  else activate_sets.active_secondary_set)
                    
                    # Check if activation exists
                    activation, created = QuestionSetActivation.objects.get_or_create(
                        trade=trade,
                        paper_type=paper_type,
                        question_set=expected_set,
                        defaults={'is_active': True}
                    )
                    
                    if created:
                        self.stdout.write(f'  ✅ Created {paper_type} activation for {trade.name} Set {expected_set}')
                        fixed_count += 1
                    
                    # Ensure only this set is active for this paper type
                    QuestionSetActivation.objects.filter(
                        trade=trade,
                        paper_type=paper_type
                    ).exclude(pk=activation.pk).update(is_active=False)
                    
                    activation.is_active = True
                    activation.save()
        
        self.stdout.write(f'  🎯 Fixed {fixed_count} issues')
        
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS('  ✅ Issues have been fixed. Please test again.'))
        else:
            self.stdout.write('  ℹ️  No issues found to fix.')