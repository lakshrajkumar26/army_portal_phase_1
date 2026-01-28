#!/usr/bin/env python
"""
Fix OCC trade activation to use PRIMARY paper type with Set D
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from questions.models import TradePaperActivation, QuestionSetActivation, GlobalPaperTypeControl, QuestionPaper
from reference.models import Trade

def fix_occ_activation():
    """Fix OCC trade to use PRIMARY paper type with Set D"""
    
    try:
        occ_trade = Trade.objects.get(code='OCC')
        print(f"Found OCC trade: {occ_trade}")
        
        # 1. Set global paper type to PRIMARY
        print("\n1. Setting global paper type to PRIMARY...")
        primary_control, created = GlobalPaperTypeControl.objects.get_or_create(
            paper_type='PRIMARY',
            defaults={'is_active': True}
        )
        if not created:
            primary_control.is_active = True
            primary_control.save()
        
        # Deactivate SECONDARY
        secondary_control, created = GlobalPaperTypeControl.objects.get_or_create(
            paper_type='SECONDARY',
            defaults={'is_active': False}
        )
        if not created:
            secondary_control.is_active = False
            secondary_control.save()
        
        print("✅ Global paper type set to PRIMARY")
        
        # 2. Activate PRIMARY paper for OCC trade
        print("\n2. Activating PRIMARY paper for OCC trade...")
        occ_primary, created = TradePaperActivation.objects.get_or_create(
            trade=occ_trade,
            paper_type='PRIMARY',
            defaults={'is_active': True}
        )
        if not created:
            occ_primary.is_active = True
            occ_primary.save()
        
        # Deactivate SECONDARY for OCC
        occ_secondary, created = TradePaperActivation.objects.get_or_create(
            trade=occ_trade,
            paper_type='SECONDARY',
            defaults={'is_active': False}
        )
        if not created:
            occ_secondary.is_active = False
            occ_secondary.save()
        
        print("✅ OCC trade set to PRIMARY")
        
        # 3. Set question set D as active for OCC PRIMARY
        print("\n3. Setting question set D as active for OCC PRIMARY...")
        
        # Deactivate all other sets for OCC PRIMARY
        QuestionSetActivation.objects.filter(
            trade=occ_trade,
            paper_type='PRIMARY'
        ).update(is_active=False)
        
        # Activate Set D
        occ_set_d, created = QuestionSetActivation.objects.get_or_create(
            trade=occ_trade,
            paper_type='PRIMARY',
            question_set='D',
            defaults={'is_active': True}
        )
        if not created:
            occ_set_d.is_active = True
            occ_set_d.save()
        
        print("✅ Question set D activated for OCC PRIMARY")
        
        # 4. Ensure PRIMARY QuestionPaper is active
        print("\n4. Ensuring PRIMARY QuestionPaper is active...")
        primary_paper, created = QuestionPaper.objects.get_or_create(
            question_paper='PRIMARY',
            defaults={'is_active': True}
        )
        if not created:
            primary_paper.is_active = True
            primary_paper.save()
        
        # Deactivate SECONDARY QuestionPaper
        try:
            secondary_paper = QuestionPaper.objects.get(question_paper='SECONDARY')
            secondary_paper.is_active = False
            secondary_paper.save()
        except QuestionPaper.DoesNotExist:
            pass
        
        print("✅ PRIMARY QuestionPaper activated")
        
        print("\n=== VERIFICATION ===")
        
        # Verify the changes
        occ_activations = TradePaperActivation.objects.filter(trade=occ_trade)
        for activation in occ_activations:
            print(f"OCC {activation.paper_type}: {'ACTIVE' if activation.is_active else 'INACTIVE'}")
        
        occ_question_sets = QuestionSetActivation.objects.filter(trade=occ_trade)
        for qs in occ_question_sets:
            print(f"OCC {qs.paper_type} Set {qs.question_set}: {'ACTIVE' if qs.is_active else 'INACTIVE'}")
        
        papers = QuestionPaper.objects.all()
        for paper in papers:
            print(f"QuestionPaper {paper.question_paper}: {'ACTIVE' if paper.is_active else 'INACTIVE'}")
        
        print("\n✅ OCC activation fixed successfully!")
        
    except Trade.DoesNotExist:
        print("OCC trade not found!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_occ_activation()