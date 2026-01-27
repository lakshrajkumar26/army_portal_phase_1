from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import timedelta
from questions.models import TradePaperActivation
from reference.models import Trade


class Command(BaseCommand):
    help = "Create TradePaperActivation entries for all trades"

    def add_arguments(self, parser):
        parser.add_argument(
            '--activate-all',
            action='store_true',
            help='Activate all trade papers by default',
        )

    def handle(self, *args, **options):
        activate_all = options.get('activate_all', False)
        
        with transaction.atomic():
            trades = Trade.objects.all()
            created_count = 0
            updated_count = 0
            
            for trade in trades:
                # Create PRIMARY paper activation
                primary_activation, created = TradePaperActivation.objects.get_or_create(
                    trade=trade,
                    paper_type="PRIMARY",
                    defaults={
                        'is_active': activate_all,
                        'exam_duration': timedelta(hours=3)  # Default 3 hours
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Created PRIMARY activation for {trade}")
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"PRIMARY activation already exists for {trade}")
                    )
                
                # Create SECONDARY paper activation
                secondary_activation, created = TradePaperActivation.objects.get_or_create(
                    trade=trade,
                    paper_type="SECONDARY",
                    defaults={
                        'is_active': activate_all,
                        'exam_duration': timedelta(hours=3)  # Default 3 hours
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Created SECONDARY activation for {trade}")
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"SECONDARY activation already exists for {trade}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSummary: {created_count} created, {updated_count} already existed"
                )
            )
            
            if activate_all:
                self.stdout.write(
                    self.style.SUCCESS("All trade papers have been activated!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "Trade papers created but not activated. "
                        "Use --activate-all flag to activate them or activate manually in admin."
                    )
                )