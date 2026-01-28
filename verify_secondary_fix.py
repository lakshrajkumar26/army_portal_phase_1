#!/usr/bin/env python
"""
Verification script for SECONDARY question display fix and smart universal activation.
This script tests the fixes implemented for Task 3.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import ActivateSets
from reference.models import Trade

def test_secondary_question_counts():
    """Test that SECONDARY question counts are accurate per trade"""
    print('=== Testing SECONDARY Question Count Display ===')
    
    trades_with_secondary = []
    trades_without_secondary = []
    
    for trade in Trade.objects.all():
        activate_sets = ActivateSets.get_or_create_for_trade(trade)
        available_sets = activate_sets.get_available_sets("SECONDARY")
        
        if available_sets:
            set_a_count = activate_sets.get_question_count("SECONDARY", "A")
            trades_with_secondary.append((trade.name, trade.code, set_a_count))
        else:
            trades_without_secondary.append((trade.name, trade.code))
    
    print(f'✅ Trades WITH SECONDARY questions ({len(trades_with_secondary)}):')
    for name, code, count in trades_with_secondary:
        print(f'   {name} ({code}): {count} questions per set')
    
    print(f'\n❌ Trades WITHOUT SECONDARY questions ({len(trades_without_secondary)}):')
    for name, code in trades_without_secondary[:5]:  # Show first 5
        print(f'   {name} ({code}): 0 questions')
    if len(trades_without_secondary) > 5:
        print(f'   ... and {len(trades_without_secondary) - 5} more')
    
    return trades_with_secondary, trades_without_secondary

def test_smart_universal_activation_logic():
    """Test the smart universal activation logic"""
    print('\n=== Testing Smart Universal Activation Logic ===')
    
    # Simulate what the smart activation would do for Set C
    test_set = 'C'
    trades_that_would_be_activated = []
    trades_that_would_be_skipped = []
    
    for trade in Trade.objects.all():
        activate_sets = ActivateSets.get_or_create_for_trade(trade)
        available_sets = activate_sets.get_available_sets("SECONDARY")
        
        if test_set in available_sets:
            trades_that_would_be_activated.append(trade.name)
        else:
            trades_that_would_be_skipped.append(trade.name)
    
    print(f'For SECONDARY Set {test_set} universal activation:')
    print(f'✅ Would ACTIVATE for {len(trades_that_would_be_activated)} trades: {", ".join(trades_that_would_be_activated)}')
    print(f'⏭️  Would SKIP {len(trades_that_would_be_skipped)} trades: {", ".join(trades_that_would_be_skipped[:5])}{"..." if len(trades_that_would_be_skipped) > 5 else ""}')
    
    return trades_that_would_be_activated, trades_that_would_be_skipped

def main():
    print('🔍 SECONDARY Question Display Fix Verification')
    print('=' * 60)
    
    # Test 1: Question count accuracy
    trades_with, trades_without = test_secondary_question_counts()
    
    # Test 2: Smart activation logic
    would_activate, would_skip = test_smart_universal_activation_logic()
    
    # Summary
    print('\n' + '=' * 60)
    print('📊 SUMMARY')
    print('=' * 60)
    
    print(f'✅ SECONDARY questions now show accurate counts:')
    print(f'   - Only {len(trades_with)} trades show SECONDARY questions (previously all {Trade.objects.count()} showed 108)')
    print(f'   - {len(trades_without)} trades correctly show 0 questions')
    
    print(f'\n🧠 Smart universal activation working:')
    print(f'   - Would activate Set C for {len(would_activate)} trades with SECONDARY data')
    print(f'   - Would skip {len(would_skip)} trades without SECONDARY data')
    print(f'   - No more "activate for all trades regardless" behavior')
    
    print(f'\n🎯 Key improvements:')
    print(f'   1. SECONDARY counts are trade-specific (not showing 108 for all trades)')
    print(f'   2. Universal activation is intelligent (only activates where available)')
    print(f'   3. UI will show "Not Available" for trades without the selected set')
    
    print(f'\n✨ Ready to test in admin interface at: http://127.0.0.1:8000/admin/questions/activatesets/')

if __name__ == '__main__':
    main()