#!/usr/bin/env python
"""
Script to fix Global Paper Type Control and SECONDARY question issues.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation, GlobalPaperTypeControl
from reference.models import Trade
from django.db import transaction

def check_secondary_questions():
    """Check if SECONDARY questions exist and are properly configured"""
    print("🔍 Checking SECONDARY Questions...")
    print("=" * 50)
    
    # Check SECONDARY questions
    secondary_questions = Question.objects.filter(
        paper_type='SECONDARY',
        is_common=True,
        is_active=True
    )
    
    print(f"📊 Total SECONDARY questions: {secondary_questions.count()}")
    
    if secondary_questions.count() == 0:
        print("❌ No SECONDARY questions found!")
        return False
    
    # Check question sets
    question_sets = list(secondary_questions.values_list('question_set', flat=True).distinct().order_by('question_set'))
    print(f"📋 Available question sets: {question_sets}")
    
    # Check for malformed data
    malformed_count = 0
    sample_questions = secondary_questions[:5]
    
    print("\n📝 Sample SECONDARY questions:")
    for question in sample_questions:
        print(f"   ID {question.id}: Part {question.part}, Set {question.question_set}")
        print(f"   Text: {question.text[:60]}...")
        
        # Check for malformed options
        if question.option_a and len(question.option_a) > 100:
            print(f"   ⚠️  Option A is malformed: {question.option_a[:50]}...")
            malformed_count += 1
    
    if malformed_count > 0:
        print(f"\n⚠️  Found {malformed_count} questions with malformed options")
    
    return True

def fix_malformed_options():
    """Fix malformed question options"""
    print("\n🔧 Fixing Malformed Options...")
    print("=" * 50)
    
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
                        # Extract the actual option text
                        # Pattern: "OCC Option A for Q16 OCC Option B for Q16..."
                        
                        # Try to find a clean option
                        if field_name == 'option_a' and 'Option A' in option_value:
                            # Extract text after "Option A for QXX"
                            parts = option_value.split('Option A')
                            if len(parts) > 1:
                                clean_text = parts[1].split('Option B')[0].strip()
                                clean_text = clean_text.replace('for Q', '').replace('OCC', '').strip()
                                if len(clean_text) > 5 and len(clean_text) < 100:
                                    setattr(question, field_name, clean_text)
                                    changed = True
                        
                        elif field_name == 'option_b' and 'Option B' in option_value:
                            parts = option_value.split('Option B')
                            if len(parts) > 1:
                                clean_text = parts[1].split('Option C')[0].strip()
                                clean_text = clean_text.replace('for Q', '').replace('OCC', '').strip()
                                if len(clean_text) > 5 and len(clean_text) < 100:
                                    setattr(question, field_name, clean_text)
                                    changed = True
                        
                        elif field_name == 'option_c' and 'Option C' in option_value:
                            parts = option_value.split('Option C')
                            if len(parts) > 1:
                                clean_text = parts[1].split('Option D')[0].strip()
                                clean_text = clean_text.replace('for Q', '').replace('OCC', '').strip()
                                if len(clean_text) > 5 and len(clean_text) < 100:
                                    setattr(question, field_name, clean_text)
                                    changed = True
                        
                        elif field_name == 'option_d' and 'Option D' in option_value:
                            parts = option_value.split('Option D')
                            if len(parts) > 1:
                                clean_text = parts[1].strip()
                                clean_text = clean_text.replace('for Q', '').replace('OCC', '').strip()
                                if len(clean_text) > 5 and len(clean_text) < 100:
                                    setattr(question, field_name, clean_text)
                                    changed = True
            
            if changed:
                question.save()
                fixed_count += 1
                print(f"  ✅ Fixed Question {question.id}")
    
    print(f"✅ Fixed {fixed_count} questions with malformed options")
    return fixed_count

def setup_global_controls():
    """Setup GlobalPaperTypeControl records"""
    print("\n🔧 Setting up Global Paper Type Controls...")
    print("=" * 50)
    
    # Create PRIMARY control if it doesn't exist
    primary_control, created = GlobalPaperTypeControl.objects.get_or_create(
        paper_type='PRIMARY',
        defaults={'is_active': False}
    )
    if created:
        print("✅ Created PRIMARY GlobalPaperTypeControl")
    else:
        print(f"✅ PRIMARY control exists: {'ACTIVE' if primary_control.is_active else 'INACTIVE'}")
    
    # Create SECONDARY control if it doesn't exist
    secondary_control, created = GlobalPaperTypeControl.objects.get_or_create(
        paper_type='SECONDARY',
        defaults={'is_active': False}
    )
    if created:
        print("✅ Created SECONDARY GlobalPaperTypeControl")
    else:
        print(f"✅ SECONDARY control exists: {'ACTIVE' if secondary_control.is_active else 'INACTIVE'}")
    
    return True

def setup_question_set_activations():
    """Setup QuestionSetActivation records for SECONDARY questions"""
    print("\n🔧 Setting up Question Set Activations...")
    print("=" * 50)
    
    # Get all trades
    trades = Trade.objects.all()
    
    # Get available SECONDARY question sets
    question_sets = list(Question.objects.filter(
        paper_type='SECONDARY',
        is_common=True,
        is_active=True
    ).values_list('question_set', flat=True).distinct().order_by('question_set'))
    
    print(f"📋 Available SECONDARY question sets: {question_sets}")
    print(f"📋 Trades to configure: {trades.count()}")
    
    created_count = 0
    
    with transaction.atomic():
        for trade in trades:
            for question_set in question_sets:
                activation, created = QuestionSetActivation.objects.get_or_create(
                    trade=trade,
                    paper_type='SECONDARY',
                    question_set=question_set,
                    defaults={'is_active': False}
                )
                if created:
                    created_count += 1
                    print(f"  ✅ Created activation for {trade.name} - SECONDARY Set {question_set}")
    
    print(f"✅ Created {created_count} QuestionSetActivation records")
    return created_count

def test_secondary_fetching():
    """Test if SECONDARY questions can be fetched properly"""
    print("\n🧪 Testing SECONDARY Question Fetching...")
    print("=" * 50)
    
    # Test 1: Check if SECONDARY questions exist
    secondary_questions = Question.objects.filter(
        paper_type='SECONDARY',
        is_common=True,
        is_active=True
    )
    print(f"✅ SECONDARY questions available: {secondary_questions.count()}")
    
    # Test 2: Check question sets
    question_sets = list(secondary_questions.values_list('question_set', flat=True).distinct().order_by('question_set'))
    print(f"✅ Question sets available: {question_sets}")
    
    # Test 3: Check activations
    sample_trade = Trade.objects.first()
    if sample_trade:
        activations = QuestionSetActivation.objects.filter(
            trade=sample_trade,
            paper_type='SECONDARY'
        )
        print(f"✅ Activations for {sample_trade.name}: {activations.count()}")
        
        for activation in activations:
            count = Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                question_set=activation.question_set,
                is_active=True
            ).count()
            print(f"   Set {activation.question_set}: {count} questions ({'ACTIVE' if activation.is_active else 'INACTIVE'})")
    
    return True

def main():
    print("🔧 Global Paper Type Control & SECONDARY Questions Fix")
    print("=" * 60)
    
    try:
        # 1. Check SECONDARY questions
        has_secondary = check_secondary_questions()
        
        if not has_secondary:
            print("\n❌ No SECONDARY questions found. Please import SECONDARY questions first.")
            return
        
        # 2. Fix malformed options
        fixed_count = fix_malformed_options()
        
        # 3. Setup global controls
        setup_global_controls()
        
        # 4. Setup question set activations
        created_activations = setup_question_set_activations()
        
        # 5. Test fetching
        test_secondary_fetching()
        
        print("\n📊 Summary:")
        print("=" * 30)
        print(f"Questions fixed: {fixed_count}")
        print(f"Activations created: {created_activations}")
        print("Global controls: ✅ Setup")
        
        print("\n💡 Next Steps:")
        print("1. Visit: http://127.0.0.1:8000/admin/questions/globalpapertypecontrol/")
        print("2. Click 'Activate SECONDARY Globally' button")
        print("3. Select question sets for each trade")
        print("4. Test the interface by toggling between PRIMARY and SECONDARY")
        
        print("\n✅ Fix completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()