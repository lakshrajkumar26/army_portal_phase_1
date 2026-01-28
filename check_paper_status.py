#!/usr/bin/env python
"""
Check current paper activation status
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import QuestionPaper, TradePaperActivation, QuestionSetActivation
from reference.models import Trade

def check_paper_status():
    """Check current paper and activation status"""
    
    print("=== PAPER STATUS CHECK ===\n")
    
    # Check QuestionPaper status
    papers = QuestionPaper.objects.all()
    print("QuestionPaper status:")
    for paper in papers:
        print(f"  {paper.question_paper}: {'ACTIVE' if paper.is_active else 'INACTIVE'}")
    
    # Check OCC trade activations
    try:
        occ_trade = Trade.objects.get(code='OCC')
        print(f"\nOCC Trade activations:")
        
        activations = TradePaperActivation.objects.filter(trade=occ_trade)
        for activation in activations:
            print(f"  {activation.paper_type}: {'ACTIVE' if activation.is_active else 'INACTIVE'}")
        
        # Check question set activations
        print(f"\nOCC Question set activations:")
        qs_activations = QuestionSetActivation.objects.filter(trade=occ_trade)
        for qs in qs_activations:
            print(f"  {qs.paper_type} Set {qs.question_set}: {'ACTIVE' if qs.is_active else 'INACTIVE'}")
            
    except Trade.DoesNotExist:
        print("OCC trade not found!")

if __name__ == '__main__':
    check_paper_status()