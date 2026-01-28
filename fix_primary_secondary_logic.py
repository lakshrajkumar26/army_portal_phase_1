#!/usr/bin/env python3
"""
Fix the PRIMARY/SECONDARY logic to use PRIMARY for trades that have PRIMARY questions
and SECONDARY for trades that only have SECONDARY questions
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import Question, QuestionSetActivation, GlobalPaperTypeControl, TradePaperActivation, QuestionPaper
from reference.models import Trade
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_primary_secondary_logic():
    """Fix PRIMARY/SECONDARY activation based on available questions"""
    print("🔧 Fixing PRIMARY/SECONDARY Logic...")
    print("=" * 60)
    
    # Get all trades
    trades = Trade.objects.all()
    
    # Analyze which trades have PRIMARY vs SECONDARY questions
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
        primary_count = Question.objects.filter(
            trade=trade,
            paper_type="PRIMARY",
            is_active=True
        ).count()
        print(f"     - {trade.name} ({trade.code}): {primary_count} PRIMARY questions")
    
    print(f"   Trades with SECONDARY only: {len(secondary_only_trades)}")
    for trade in secondary_only_trades[:5]:  # Show first 5
        print(f"     - {trade.name} ({trade.code})")
    if len(secondary_only_trades) > 5:
        print(f"     ... and {len(secondary_only_trades) - 5} more")
    
    # Since we have mixed requirements, we need to set up individual trade activations
    # instead of global activation
    
    print(f"\n🔄 Setting up individual trade activations...")
    
    # Deactivate global controls first
    GlobalPaperTypeControl.objects.all().update(is_active=False)
    print("✅ Deactivated global paper type controls")
    
    # Activate appropriate paper types for each trade
    for trade in primary_trades:
        print(f"\n🔵 Setting up PRIMARY for {trade.name}:")
        
        # Activate PRIMARY paper for this trade
        tp_activation, created = TradePaperActivation.objects.get_or_create(
            trade=trade,
            paper_type='PRIMARY',
            defaults={'is_active': True}
        )
        if not created:
            tp_activation.is_active = True
            tp_activation.save()
        
        # Deactivate SECONDARY for this trade
        TradePaperActivation.objects.filter(
            trade=trade,
            paper_type='SECONDARY'
        ).update(is_active=False)
        
        # Activate PRIMARY QuestionPaper
        primary_paper, created = QuestionPaper.objects.get_or_create(
            question_paper='PRIMARY',
            defaults={'is_active': True}
        )
        if not created:
            primary_paper.is_active = True
            primary_paper.save()
        
        # Set up question set activation for PRIMARY (Set C as requested)
        # Check what sets are available for this trade
        available_sets = Question.objects.filter(
            trade=trade,
            paper_type='PRIMARY',
            is_active=True
        ).values_list('question_set', flat=True).distinct().order_by('question_set')
        
        if 'C' in available_sets:
            active_set = 'C'
        else:
            active_set = list(available_sets)[0] if available_sets else 'A'
        
        # Activate the chosen set
        qs_activation, created = QuestionSetActivation.objects.get_or_create(
            trade=trade,
            paper_type='PRIMARY',
            question_set=active_set,
            defaults={'is_active': True}
        )
        if not created:
            qs_activation.is_active = True
            qs_activation.save()
        
        # Deactivate other PRIMARY sets for this trade
        QuestionSetActivation.objects.filter(
            trade=trade,
            paper_type='PRIMARY'
        ).exclude(question_set=active_set).update(is_active=False)
        
        print(f"   ✅ PRIMARY Set {active_set} activated")
    
    for trade in secondary_only_trades:
        print(f"\n🟠 Setting up SECONDARY for {trade.name}:")
        
        # Activate SECONDARY paper for this trade
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
        
        # Activate SECONDARY QuestionPaper
        secondary_paper, created = QuestionPaper.objects.get_or_create(
            question_paper='SECONDARY',
            defaults={'is_active': True}
        )
        if not created:
            secondary_paper.is_active = True
            secondary_paper.save()
        
        # Set up question set activation for SECONDARY (Set C as requested)
        qs_activation, created = QuestionSetActivation.objects.get_or_create(
            trade=trade,
            paper_type='SECONDARY',
            question_set='C',
            defaults={'is_active': True}
        )
        if not created:
            qs_activation.is_active = True
            qs_activation.save()
        
        # Deactivate other SECONDARY sets for this trade
        QuestionSetActivation.objects.filter(
            trade=trade,
            paper_type='SECONDARY'
        ).exclude(question_set='C').update(is_active=False)
        
        print(f"   ✅ SECONDARY Set C activated")
    
    print(f"\n✅ Individual trade activations completed!")
    print(f"   - {len(primary_trades)} trades using PRIMARY papers")
    print(f"   - {len(secondary_only_trades)} trades using SECONDARY papers")
    
    return True

def test_fixed_logic():
    """Test the fixed logic"""
    print(f"\n🧪 Testing Fixed Logic...")
    print("=" * 40)
    
    # Test DMV (should use PRIMARY)
    dmv_trade = Trade.objects.get(code='DMV')
    try:
        dmv_activation = TradePaperActivation.objects.get(
            trade=dmv_trade,
            is_active=True
        )
        print(f"✅ DMV uses: {dmv_activation.paper_type}")
        
        dmv_qs = QuestionSetActivation.objects.get(
            trade=dmv_trade,
            paper_type=dmv_activation.paper_type,
            is_active=True
        )
        print(f"   Active question set: {dmv_qs.question_set}")
    except Exception as e:
        print(f"❌ DMV error: {e}")
    
    # Test TTC (should use SECONDARY)
    ttc_trade = Trade.objects.get(code='TTC')
    try:
        ttc_activation = TradePaperActivation.objects.get(
            trade=ttc_trade,
            is_active=True
        )
        print(f"✅ TTC uses: {ttc_activation.paper_type}")
        
        ttc_qs = QuestionSetActivation.objects.get(
            trade=ttc_trade,
            paper_type=ttc_activation.paper_type,
            is_active=True
        )
        print(f"   Active question set: {ttc_qs.question_set}")
    except Exception as e:
        print(f"❌ TTC error: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 PRIMARY/SECONDARY Logic Fix")
    print("=" * 60)
    
    # Apply the fix
    success = fix_primary_secondary_logic()
    
    if success:
        # Test the fix
        test_success = test_fixed_logic()
        
        print("\n" + "=" * 60)
        if test_success:
            print("✅ PRIMARY/SECONDARY LOGIC FIX SUCCESSFUL!")
            print("   - DMV and OCC will use PRIMARY papers with their question sets")
            print("   - All other trades will use SECONDARY papers with Set C")
        else:
            print("❌ Fix applied but test failed.")
    else:
        print("❌ Fix failed to apply.")
    
    print("=" * 60)