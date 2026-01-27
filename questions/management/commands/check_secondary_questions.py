"""
Management command to check SECONDARY questions and fix data issues.
"""

from django.core.management.base import BaseCommand
from questions.models import Question, QuestionSetActivation, GlobalPaperTypeControl
from reference.models import Trade
from django.db import transaction


class Command(BaseCommand):
    help = 'Check SECONDARY questions and fix data issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix-data',
            action='store_true',
            help='Fix malformed question data',
        )
        parser.add_argument(
            '--create-activations',
            action='store_true',
            help='Create missing QuestionSetActivation records',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Checking SECONDARY Questions'))
        self.stdout.write('=' * 60)
        
        # 1. Check SECONDARY questions exist
        secondary_questions = Question.objects.filter(
            paper_type='SECONDARY',
            is_common=True,
            is_active=True
        )
        
        self.stdout.write(f"📊 SECONDARY Questions Found: {secondary_questions.count()}")
        
        if secondary_questions.count() == 0:
            self.stdout.write(self.style.WARNING('⚠️  No SECONDARY questions found!'))
            return
        
        # 2. Check question sets available
        question_sets = secondary_questions.values_list('question_set', flat=True).distinct().order_by('question_set')
        self.stdout.write(f"📋 Available Question Sets: {list(question_sets)}")
        
        # 3. Check for malformed data
        malformed_count = 0
        for question in secondary_questions[:10]:  # Check first 10
            if question.option_a and len(question.option_a) > 100:
                self.stdout.write(f"⚠️  Question {question.id} has malformed option_a: {question.option_a[:50]}...")
                malformed_count += 1
        
        if malformed_count > 0:
            self.stdout.write(f"⚠️  Found {malformed_count} questions with malformed options")
            
            if options['fix_data']:
                self.fix_malformed_options()
        
        # 4. Check QuestionSetActivation records for SECONDARY
        trades = Trade.objects.all()
        missing_activations = []
        
        for trade in trades:
            for question_set in question_sets:
                try:
                    activation = QuestionSetActivation.objects.get(
                        trade=trade,
                        paper_type='SECONDARY',
                        question_set=question_set
                    )
                    if activation.is_active:
                        self.stdout.write(f"✅ {trade.name} - SECONDARY Set {question_set}: ACTIVE")
                except QuestionSetActivation.DoesNotExist:
                    missing_activations.append((trade, question_set))
        
        if missing_activations:
            self.stdout.write(f"⚠️  Missing {len(missing_activations)} QuestionSetActivation records")
            
            if options['create_activations']:
                self.create_missing_activations(missing_activations)
        
        # 5. Check GlobalPaperTypeControl
        try:
            secondary_control = GlobalPaperTypeControl.objects.get(paper_type='SECONDARY')
            self.stdout.write(f"📋 SECONDARY Control: {'ACTIVE' if secondary_control.is_active else 'INACTIVE'}")
        except GlobalPaperTypeControl.DoesNotExist:
            self.stdout.write("⚠️  No SECONDARY GlobalPaperTypeControl found")
            
            if options['create_activations']:
                GlobalPaperTypeControl.objects.create(
                    paper_type='SECONDARY',
                    is_active=False
                )
                self.stdout.write("✅ Created SECONDARY GlobalPaperTypeControl")
        
        # 6. Sample question display
        self.stdout.write("\n📝 Sample SECONDARY Questions:")
        for question in secondary_questions[:3]:
            self.stdout.write(f"   ID {question.id}: Part {question.part}, Set {question.question_set}")
            self.stdout.write(f"   Text: {question.text[:80]}...")
            if question.option_a:
                self.stdout.write(f"   Option A: {question.option_a[:50]}...")
        
        self.stdout.write(self.style.SUCCESS('\n✅ SECONDARY questions check completed'))

    def fix_malformed_options(self):
        """Fix malformed question options"""
        self.stdout.write("\n🔧 Fixing malformed options...")
        
        fixed_count = 0
        with transaction.atomic():
            questions = Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                is_active=True
            )
            
            for question in questions:
                changed = False
                
                # Check each option field
                for field_name in ['option_a', 'option_b', 'option_c', 'option_d']:
                    option_value = getattr(question, field_name)
                    
                    if option_value and len(option_value) > 100:
                        # Check if it contains repetitive patterns
                        if 'Option' in option_value and ('for Q' in option_value or 'OCC' in option_value):
                            # Try to extract meaningful part
                            # Look for patterns like "OCC Option A for Q16 OCC Option B for Q16..."
                            parts = option_value.split('Option')
                            if len(parts) > 1:
                                # Find the cleanest part
                                for part in parts[1:]:  # Skip first empty part
                                    clean_part = part.strip()
                                    if clean_part and not clean_part.startswith(('A', 'B', 'C', 'D')):
                                        # Remove common prefixes
                                        clean_part = clean_part.replace('for Q', '').replace('OCC', '').strip()
                                        if len(clean_part) > 5 and len(clean_part) < 100:
                                            setattr(question, field_name, clean_part)
                                            changed = True
                                            self.stdout.write(f"  Fixed {field_name} for Question {question.id}")
                                            break
                
                if changed:
                    question.save()
                    fixed_count += 1
        
        self.stdout.write(f"✅ Fixed {fixed_count} questions")

    def create_missing_activations(self, missing_activations):
        """Create missing QuestionSetActivation records"""
        self.stdout.write("\n🔧 Creating missing activations...")
        
        created_count = 0
        with transaction.atomic():
            for trade, question_set in missing_activations:
                QuestionSetActivation.objects.create(
                    trade=trade,
                    paper_type='SECONDARY',
                    question_set=question_set,
                    is_active=False  # Start as inactive
                )
                created_count += 1
        
        self.stdout.write(f"✅ Created {created_count} QuestionSetActivation records")