"""
Management command for bulk exam slot operations
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from registration.models import CandidateProfile
from reference.models import Trade

User = get_user_model()


class Command(BaseCommand):
    help = 'Manage exam slots for candidates'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['assign', 'reset', 'reassign', 'status'],
            help='Action to perform: assign, reset, reassign, or status'
        )
        parser.add_argument(
            '--trade',
            type=str,
            help='Filter by trade name (optional)'
        )
        parser.add_argument(
            '--army-no',
            type=str,
            help='Specific army number (optional)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--admin-user',
            type=str,
            default='admin',
            help='Username of admin assigning slots (default: admin)'
        )

    def handle(self, *args, **options):
        action = options['action']
        trade_filter = options.get('trade')
        army_no_filter = options.get('army_no')
        dry_run = options.get('dry_run', False)
        admin_username = options.get('admin_user', 'admin')

        # Get admin user for slot assignment tracking
        try:
            admin_user = User.objects.get(username=admin_username)
        except User.DoesNotExist:
            admin_user = None
            if action == 'assign' or action == 'reassign':
                self.stdout.write(
                    self.style.WARNING(f'Admin user "{admin_username}" not found. Slots will be assigned without tracking.')
                )

        # Build queryset
        queryset = CandidateProfile.objects.all()
        
        if trade_filter:
            try:
                trade = Trade.objects.get(name__iexact=trade_filter)
                queryset = queryset.filter(trade=trade)
                self.stdout.write(f'Filtering by trade: {trade.name}')
            except Trade.DoesNotExist:
                raise CommandError(f'Trade "{trade_filter}" not found')
        
        if army_no_filter:
            queryset = queryset.filter(army_no=army_no_filter)
            self.stdout.write(f'Filtering by army number: {army_no_filter}')

        candidates = queryset.select_related('trade', 'user')
        total_count = candidates.count()

        if total_count == 0:
            self.stdout.write(self.style.WARNING('No candidates found matching the criteria.'))
            return

        self.stdout.write(f'Found {total_count} candidates')

        if action == 'status':
            self._show_status(candidates)
        elif action == 'assign':
            self._assign_slots(candidates, admin_user, dry_run)
        elif action == 'reset':
            self._reset_slots(candidates, dry_run)
        elif action == 'reassign':
            self._reassign_slots(candidates, admin_user, dry_run)

    def _show_status(self, candidates):
        """Show slot status for all candidates"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write('EXAM SLOT STATUS REPORT')
        self.stdout.write('='*80)
        
        no_slot_count = 0
        available_count = 0
        consumed_count = 0
        
        for candidate in candidates:
            status = candidate.slot_status
            if "No Slot" in status:
                no_slot_count += 1
                status_color = self.style.ERROR
            elif "Consumed" in status:
                consumed_count += 1
                status_color = self.style.WARNING
            else:  # Available
                available_count += 1
                status_color = self.style.SUCCESS
            
            self.stdout.write(
                f'{candidate.army_no:<15} {candidate.name:<25} {candidate.trade.name if candidate.trade else "No Trade":<15} '
                f'{status_color(status)}'
            )
        
        self.stdout.write('\n' + '-'*80)
        self.stdout.write(f'Summary:')
        self.stdout.write(f'  No Slot: {no_slot_count}')
        self.stdout.write(f'  Available: {available_count}')
        self.stdout.write(f'  Consumed: {consumed_count}')
        self.stdout.write(f'  Total: {no_slot_count + available_count + consumed_count}')

    def _assign_slots(self, candidates, admin_user, dry_run):
        """Assign slots to candidates who don't have them"""
        count = 0
        for candidate in candidates:
            if not candidate.has_exam_slot:
                if dry_run:
                    self.stdout.write(f'Would assign slot to: {candidate.army_no} - {candidate.name}')
                else:
                    candidate.assign_exam_slot(assigned_by_user=admin_user)
                    self.stdout.write(
                        self.style.SUCCESS(f'Assigned slot to: {candidate.army_no} - {candidate.name}')
                    )
                count += 1
        
        if dry_run:
            self.stdout.write(f'\nDry run: Would assign {count} slots')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nAssigned {count} exam slots'))

    def _reset_slots(self, candidates, dry_run):
        """Reset slots for all candidates"""
        count = 0
        for candidate in candidates:
            if candidate.has_exam_slot:
                if dry_run:
                    self.stdout.write(f'Would reset slot for: {candidate.army_no} - {candidate.name}')
                else:
                    candidate.reset_exam_slot()
                    self.stdout.write(
                        self.style.WARNING(f'Reset slot for: {candidate.army_no} - {candidate.name}')
                    )
                count += 1
        
        if dry_run:
            self.stdout.write(f'\nDry run: Would reset {count} slots')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nReset {count} exam slots'))

    def _reassign_slots(self, candidates, admin_user, dry_run):
        """Reset and reassign slots for all candidates"""
        count = 0
        for candidate in candidates:
            if dry_run:
                self.stdout.write(f'Would reassign slot for: {candidate.army_no} - {candidate.name}')
            else:
                candidate.reset_exam_slot()
                candidate.assign_exam_slot(assigned_by_user=admin_user)
                self.stdout.write(
                    self.style.SUCCESS(f'Reassigned slot for: {candidate.army_no} - {candidate.name}')
                )
            count += 1
        
        if dry_run:
            self.stdout.write(f'\nDry run: Would reassign {count} slots')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nReassigned {count} exam slots'))