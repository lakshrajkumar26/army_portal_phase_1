# questions/management/commands/manage_question_sets.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db import models
from questions.models import Question, QuestionSetActivation
from reference.models import Trade


class Command(BaseCommand):
    help = 'Manage question sets - view current status and activate specific sets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-status',
            action='store_true',
            help='Show current question set activation status'
        )
        parser.add_argument(
            '--activate-set',
            type=str,
            help='Activate a specific question set (A, B, C, D, etc.)'
        )
        parser.add_argument(
            '--trade',
            type=str,
            help='Trade code/name to activate set for (required with --activate-set)'
        )
        parser.add_argument(
            '--paper-type',
            type=str,
            choices=['PRIMARY', 'SECONDARY'],
            default='PRIMARY',
            help='Paper type (PRIMARY or SECONDARY)'
        )
        parser.add_argument(
            '--list-available-sets',
            action='store_true',
            help='List all available question sets in the database'
        )

    def handle(self, *args, **options):
        if options['show_status']:
            self.show_activation_status()
        
        if options['list_available_sets']:
            self.list_available_sets()
        
        if options['activate_set']:
            if not options['trade']:
                self.stdout.write(
                    self.style.ERROR('--trade is required when using --activate-set')
                )
                return
            
            self.activate_question_set(
                options['activate_set'],
                options['trade'],
                options['paper_type']
            )

    def show_activation_status(self):
        """Show current question set activation status"""
        self.stdout.write(self.style.SUCCESS('\n=== QUESTION SET ACTIVATION STATUS ===\n'))
        
        activations = QuestionSetActivation.objects.select_related('trade').order_by(
            'trade__name', 'paper_type', 'question_set'
        )
        
        current_trade = None
        for activation in activations:
            if current_trade != activation.trade.name:
                current_trade = activation.trade.name
                self.stdout.write(f"\n📋 {current_trade}:")
            
            status = "🟢 ACTIVE" if activation.is_active else "⚪ INACTIVE"
            self.stdout.write(
                f"  {activation.paper_type} Set {activation.question_set}: {status}"
            )
        
        if not activations.exists():
            self.stdout.write(self.style.WARNING('No question set activations found.'))

    def list_available_sets(self):
        """List all available question sets in the database"""
        self.stdout.write(self.style.SUCCESS('\n=== AVAILABLE QUESTION SETS ===\n'))
        
        # Get unique combinations of trade, paper_type, and question_set
        sets = Question.objects.values(
            'trade__name', 'paper_type', 'question_set'
        ).distinct().order_by('trade__name', 'paper_type', 'question_set')
        
        current_trade = None
        for item in sets:
            trade_name = item['trade__name'] or 'No Trade'
            if current_trade != trade_name:
                current_trade = trade_name
                self.stdout.write(f"\n📚 {trade_name}:")
            
            # Count questions in this set
            count = Question.objects.filter(
                trade__name=trade_name,
                paper_type=item['paper_type'],
                question_set=item['question_set'],
                is_active=True
            ).count()
            
            self.stdout.write(
                f"  {item['paper_type']} Set {item['question_set']}: {count} questions"
            )

    def activate_question_set(self, question_set, trade_name, paper_type):
        """Activate a specific question set for a trade"""
        try:
            # Find the trade
            trade = Trade.objects.filter(
                models.Q(name__icontains=trade_name) | 
                models.Q(code__icontains=trade_name)
            ).first()
            
            if not trade:
                self.stdout.write(
                    self.style.ERROR(f'Trade "{trade_name}" not found.')
                )
                return
            
            # Check if questions exist for this combination
            question_count = Question.objects.filter(
                trade=trade,
                paper_type=paper_type,
                question_set=question_set.upper(),
                is_active=True
            ).count()
            
            if question_count == 0:
                self.stdout.write(
                    self.style.ERROR(
                        f'No questions found for {trade.name} {paper_type} Set {question_set.upper()}'
                    )
                )
                return
            
            with transaction.atomic():
                # Deactivate all other sets for this trade and paper type
                QuestionSetActivation.objects.filter(
                    trade=trade,
                    paper_type=paper_type,
                    is_active=True
                ).update(is_active=False)
                
                # Activate the requested set
                activation, created = QuestionSetActivation.objects.get_or_create(
                    trade=trade,
                    paper_type=paper_type,
                    question_set=question_set.upper(),
                    defaults={'is_active': True}
                )
                
                if not created:
                    activation.is_active = True
                    activation.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Activated {trade.name} {paper_type} Set {question_set.upper()} '
                        f'({question_count} questions)'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error activating question set: {str(e)}')
            )