"""
Management command to check and fix question display issues.
"""

from django.core.management.base import BaseCommand
from questions.models import Question
from reference.models import Trade


class Command(BaseCommand):
    help = 'Check and display question data to identify display issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--trade',
            type=str,
            help='Filter by trade code (e.g., OCC)',
        )
        parser.add_argument(
            '--paper-type',
            type=str,
            choices=['PRIMARY', 'SECONDARY'],
            help='Filter by paper type',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit number of questions to display',
        )
        parser.add_argument(
            '--fix-options',
            action='store_true',
            help='Fix malformed question options',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Checking Question Display Issues'))
        self.stdout.write('=' * 60)
        
        # Build query
        queryset = Question.objects.all()
        
        if options['trade']:
            try:
                trade = Trade.objects.get(code__iexact=options['trade'])
                queryset = queryset.filter(trade=trade)
                self.stdout.write(f"Filtering by trade: {trade.name} ({trade.code})")
            except Trade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Trade '{options['trade']}' not found"))
                return
        
        if options['paper_type']:
            queryset = queryset.filter(paper_type=options['paper_type'])
            self.stdout.write(f"Filtering by paper type: {options['paper_type']}")
        
        # Order by ID and limit
        queryset = queryset.order_by('id')[:options['limit']]
        
        if not queryset.exists():
            self.stdout.write(self.style.WARNING('No questions found matching criteria'))
            return
        
        self.stdout.write(f"\nDisplaying {queryset.count()} questions:")
        self.stdout.write('-' * 60)
        
        issues_found = 0
        
        for question in queryset:
            self.stdout.write(f"\n📝 Question ID: {question.id}")
            self.stdout.write(f"   Part: {question.part} | Marks: {question.marks}")
            self.stdout.write(f"   Trade: {question.trade} | Paper: {question.paper_type}")
            self.stdout.write(f"   Set: {question.question_set} | Active: {question.is_active}")
            self.stdout.write(f"   Text: {question.text[:100]}...")
            
            # Check options
            has_new_options = any([question.option_a, question.option_b, question.option_c, question.option_d])
            has_legacy_options = question.options is not None
            
            if has_new_options:
                self.stdout.write("   📋 New Format Options:")
                if question.option_a:
                    self.stdout.write(f"      A: {question.option_a[:50]}...")
                if question.option_b:
                    self.stdout.write(f"      B: {question.option_b[:50]}...")
                if question.option_c:
                    self.stdout.write(f"      C: {question.option_c[:50]}...")
                if question.option_d:
                    self.stdout.write(f"      D: {question.option_d[:50]}...")
            
            if has_legacy_options:
                self.stdout.write(f"   📋 Legacy Options: {question.options}")
            
            if question.correct_answer:
                self.stdout.write(f"   ✅ Correct Answer: {question.correct_answer}")
            
            # Check for issues
            if not has_new_options and not has_legacy_options and question.part in ['A', 'B']:
                self.stdout.write(self.style.WARNING("   ⚠️  MCQ question missing options!"))
                issues_found += 1
            
            # Check for malformed options
            if has_new_options:
                for opt_field, opt_value in [
                    ('option_a', question.option_a),
                    ('option_b', question.option_b), 
                    ('option_c', question.option_c),
                    ('option_d', question.option_d)
                ]:
                    if opt_value and len(opt_value) > 200:
                        self.stdout.write(self.style.WARNING(f"   ⚠️  {opt_field} is unusually long ({len(opt_value)} chars)"))
                        issues_found += 1
                        
                        if options['fix_options']:
                            # Try to extract meaningful option text
                            if 'Option' in opt_value:
                                # Extract the part after "Option X for QY"
                                parts = opt_value.split('Option')
                                if len(parts) > 1:
                                    cleaned = parts[-1].strip()
                                    if len(cleaned) < len(opt_value):
                                        setattr(question, opt_field, cleaned)
                                        self.stdout.write(self.style.SUCCESS(f"      ✅ Fixed {opt_field}"))
        
        if options['fix_options'] and issues_found > 0:
            # Save all changes
            for question in queryset:
                question.save()
            self.stdout.write(self.style.SUCCESS(f"\n✅ Fixed {issues_found} option issues"))
        
        self.stdout.write(f"\n📊 Summary:")
        self.stdout.write(f"   Total questions checked: {queryset.count()}")
        self.stdout.write(f"   Issues found: {issues_found}")
        
        if issues_found > 0 and not options['fix_options']:
            self.stdout.write(f"\n💡 Run with --fix-options to automatically fix option issues")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Question display check completed'))