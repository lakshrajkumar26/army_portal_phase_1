#!/usr/bin/env python3
"""
Check current activation status
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import QuestionSetActivation, TradePaperActivation, GlobalPaperTypeControl
from reference.models import Trade

def check_activations():
    """Check current activation status"""
    print("🔍 Current Activation Status")
    print("=" * 60)
    
    # Check global controls
    print("🌐 Global Paper Type Controls:")
    for control in GlobalPaperTypeControl.objects.all():
        status = "ACTIVE" if control.is_active else "INACTIVE"
        print(f"   {control.paper_type}: {status}")
    
    # Check trade paper activations
    print(f"\n📋 Trade Paper Activations:")
    activations = TradePaperActivation.objects.filter(is_active=True).select_related('trade')
    for activation in activations.order_by('trade__name'):
        print(f"   {activation.trade.name} ({activation.trade.code}): {activation.paper_type}")
    
    # Check question set activations
    print(f"\n🎯 Question Set Activations:")
    qs_activations = QuestionSetActivation.objects.filter(is_active=True).select_related('trade')
    for qs_activation in qs_activations.order_by('trade__name', 'paper_type'):
        print(f"   {qs_activation.trade.name} ({qs_activation.trade.code}) - {qs_activation.paper_type}: Set {qs_activation.question_set}")

if __name__ == "__main__":
    check_activations()