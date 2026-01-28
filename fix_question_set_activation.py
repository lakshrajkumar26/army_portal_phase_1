#!/usr/bin/env python3
"""
Fix question set activation issues by ensuring proper paper type activation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation, GlobalPaperTypeControl, TradePaperActivation
from reference.models import Trade
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_question_set_activation():
    """Fix question set activation by setting appropriate paper types per trade"""
    print("🔧 Fixing Question Set Activation...")
    print("=" * 60)
    
    # Get all trades
    trades = Trade.objects.all()
    
    # Check which trades have PRIMARY vs SECONDARY questions
    primary_trades = []
    secondary_only_trades = []
    
    for trade in trades:
        has_primary = Question.objects.filter(
            trade=trade,
            paper_type="PRIMARY",
            is_active=True
        ).exists()
        
        if has_primary:
            primary_trades.append(trade)
        else:
            secondary_only_trades.append(trade)
    
    print(f"📊 Analysis:")
    print(f"   Trades with PRIMARY questions: {len(primary_trades)}")
    for trade in primary_trades:
        print(f"     - {trade.name} ({trade.code})")
    
    print(f"   Trades with SECONDARY only: {len(secondary_only_trades)}")
    for trade in secondary_only_trades[:5]:  # Show first 5
        print(f"     - {trade.name} ({trade.code})")
    if len(secondary_only_trades) > 5:
        print(f"     ... and {len(secondary_only_trades) - 5} more")
    
    # Since most trades only have SECONDARY questions, let's activate SECONDARY globally
    print(f"\n🔄 Activating SECONDARY papers globally...")
    
    # Activate SECONDARY globally
    secondary_control, created = GlobalPaperTypeControl.objects.get_or_create(
        paper_type='SECONDARY',
        defaults={'is_active': True}
    )
    if not created:
        secondary_control.is_active = True
        secondary_control.save()
    
    # Deactivate PRIMARY
    GlobalPaperTypeControl.objects.filter(paper_type='PRIMARY').update(is_active=False)
    
    print("✅ SECONDARY papers activated globally")
    
    # Now set up proper question set activations for all trades
    print(f"\n🔧 Setting up question set activations...")
    
    for trade in trades:
        # For SECONDARY papers, activate Set C (as mentioned in the user's issue)
        activation, created = QuestionSetActivation.objects.get_or_create(
            trade=trade,
            paper_type='SECONDARY',
            question_set='C',
            defaults={'is_active': True}
        )
        if not created:
            activation.is_active = True
            activation.save()
        
        # Deactivate other SECONDARY sets for this trade
        QuestionSetActivation.objects.filter(
            trade=trade,
            paper_type='SECONDARY'
        ).exclude(question_set='C').update(is_active=False)
        
        # Also set up TradePaperActivation for backward compatibility
        tp_activation, created = TradePaperActivation.objects.get_or_create(
            trade=trade,
            paper_type='SECONDARY',
            defaults={'is_active': True}
        )
        if not created:
            tp_activation.is_active = True
            tp_activation.save()
        
        # Deactivate PRIMARY for this trade
        TradePaperActivation.objects.filter(
            trade=trade,
            paper_type='PRIMARY'
        ).update(is_active=False)
        
        print(f"   ✅ {trade.name}: SECONDARY Set C activated")
    
    print(f"\n✅ All trades now use SECONDARY papers with Set C activated")
    
    return True

def test_fixed_activation():
    """Test that the fix works"""
    print(f"\n🧪 Testing Fixed Activation...")
    print("=" * 40)
    
    # Test with a trade that previously failed (TTC)
    test_trade = Trade.objects.get(code='TTC')
    
    # Check active question set
    try:
        active_set = QuestionSetActivation.objects.get(
            trade=test_trade,
            paper_type='SECONDARY',
            is_active=True
        )
        print(f"✅ {test_trade.name} active set: {active_set.question_set}")
    except QuestionSetActivation.DoesNotExist:
        print(f"❌ No active set for {test_trade.name}")
        return False
    
    # Check available questions
    questions = Question.objects.filter(
        paper_type="SECONDARY",
        is_common=True,
        question_set=active_set.question_set,
        is_active=True
    )
    print(f"📊 Available SECONDARY questions in Set {active_set.question_set}: {questions.count()}")
    
    if questions.count() > 0:
        print("✅ Fix successful - questions are available!")
        return True
    else:
        print("❌ Fix failed - no questions available")
        return False

if __name__ == "__main__":
    print("🚀 Question Set Activation Fix")
    print("=" * 60)
    
    # Apply the fix
    success = fix_question_set_activation()
    
    if success:
        # Test the fix
        test_success = test_fixed_activation()
        
        print("\n" + "=" * 60)
        if test_success:
            print("✅ QUESTION SET ACTIVATION FIX SUCCESSFUL!")
            print("   All trades now use SECONDARY papers with Set C activated.")
            print("   Candidates will see questions from the correct question set.")
        else:
            print("❌ Fix applied but test failed.")
    else:
        print("❌ Fix failed to apply.")
    
    print("=" * 60)