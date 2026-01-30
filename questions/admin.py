# questions/admin.py
from django.contrib import admin, messages
from django.urls import path
from django.utils.html import format_html
import logging
from datetime import timedelta
from questions.models import TradePaperActivation

logger = logging.getLogger(__name__)

from .models import (
    Question,
    QuestionUpload,
    GlobalPaperTypeControl,
    ActivateSets,
    QuestionSetActivation,
    UniversalSetActivation,
)
from .forms import QuestionUploadForm


# --------------------------------
# Question Bank (QP Delete)
# --------------------------------
# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "part",
#         "short_text",
#         "formatted_options",
#         "correct_answer_display",
#         "trade",
#         "paper_type",
#         "question_set",
#         "is_active",
#         "created_at",
#     )
#     list_filter = ("paper_type", "is_active", "trade", "part", "question_set")
#     search_fields = ("text", "option_a", "option_b", "option_c", "option_d")
#     ordering = ("-created_at",)
#     list_per_page = 50
    
#     # Fix for template variable errors
#     filter_input_length = 10  # Add missing attribute
    
#     fieldsets = (
#         ('Question Details', {
#             'fields': ('text', 'part', 'marks', 'trade', 'paper_type', 'question_set')
#         }),
#         ('Options (New Format)', {
#             'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
#             'classes': ('collapse',)
#         }),
#         ('Legacy Options', {
#             'fields': ('options', 'correct_answer'),
#             'classes': ('collapse',)
#         }),
#         ('Status', {
#             'fields': ('is_common', 'is_active')
#         }),
#     )

#     def short_text(self, obj):
#         return obj.text[:80] + "..." if len(obj.text) > 80 else obj.text
#     short_text.short_description = "Question Text"

#     def formatted_options(self, obj):
#         """Display options in a clean format"""
#         if obj.part not in ['A', 'B']:  # Only show options for MCQ questions
#             return "-"
        
#         options = []
#         if obj.option_a:
#             options.append(f"A: {obj.option_a[:30]}...")
#         if obj.option_b:
#             options.append(f"B: {obj.option_b[:30]}...")
#         if obj.option_c:
#             options.append(f"C: {obj.option_c[:30]}...")
#         if obj.option_d:
#             options.append(f"D: {obj.option_d[:30]}...")
        
#         if options:
#             return " | ".join(options)
#         elif obj.options:
#             return f"Legacy: {str(obj.options)[:50]}..."
#         else:
#             return "No options"
#     formatted_options.short_description = "Options"

#     def correct_answer_display(self, obj):
#         """Display correct answer in a clean format"""
#         if obj.correct_answer:
#             if isinstance(obj.correct_answer, str):
#                 return obj.correct_answer
#             elif isinstance(obj.correct_answer, dict):
#                 return str(obj.correct_answer)
#             else:
#                 return str(obj.correct_answer)
#         return "-"
#     correct_answer_display.short_description = "Correct Answer"


# --------------------------------
# QP Upload (SIMPLIFIED)
# --------------------------------
@admin.register(QuestionUpload)
class QuestionUploadAdmin(admin.ModelAdmin):
    """
    Admin ONLY uploads unified DAT here.
    - Trade is taken from Excel
    - Uploaded_at hidden
    """
    form = QuestionUploadForm

    fields = ("file", "decryption_password")   # 🔥 ONLY REQUIRED FIELDS
    list_display = ("file",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(
            request,
            "Question paper uploaded and imported successfully.",
        )


# --------------------------------
# Trade Paper Activation (REMOVED - Replaced by QuestionSetActivation)
# --------------------------------
# The TradePaperActivation admin has been removed as it's been replaced
# by the more advanced QuestionSetActivation and GlobalPaperTypeControl system.
# The model still exists for backward compatibility but is no longer exposed in admin.


# --------------------------------
# Question Set Activation Management (REMOVED FROM ADMIN)
# --------------------------------
# The QuestionSetActivation admin interface has been removed to simplify
# the admin panel. All question set management is now handled through
# the GlobalPaperTypeControl interface, which provides master control
# over PRIMARY/SECONDARY paper activation and automatically manages
# the underlying QuestionSetActivation records.
#
# The QuestionSetActivation model still exists and functions normally
# for programmatic access and the GlobalPaperTypeControl system.


# --------------------------------
# Unified Question Set Management (ActivateSets)
# --------------------------------
@admin.register(ActivateSets)
class ActivateSetsAdmin(admin.ModelAdmin):
    """
    Unified admin interface for question set management.
    Provides simple dropdown interface for selecting active question sets per trade.
    """
    list_display = ['trade', 'active_primary_set', 'active_secondary_set', 'last_updated', 'updated_by']
    list_filter = ['active_primary_set', 'active_secondary_set', 'last_updated']
    search_fields = ['trade__name', 'trade__code']
    readonly_fields = ['last_updated']
    
    # Fix for template variable errors
    filter_input_length = 10  # Add missing attribute
    
    def changelist_view(self, request, extra_context=None):
        """
        Custom changelist view that provides the unified question set management interface
        """
        from reference.models import Trade
        
        # Handle POST requests for question set changes
        if request.method == 'POST':
            return self._handle_post_request(request)
        
        # Get current global paper type
        active_paper_type = None
        try:
            active_control = GlobalPaperTypeControl.objects.get(is_active=True)
            active_paper_type = active_control.paper_type
        except GlobalPaperTypeControl.DoesNotExist:
            pass
        
        # Get universal set activation settings
        universal_settings = {}
        try:
            if active_paper_type:
                universal_activation = UniversalSetActivation.objects.get(paper_type=active_paper_type)
                universal_settings = {
                    'universal_set_label': universal_activation.universal_set_label,
                    'universal_duration_minutes': universal_activation.universal_duration_minutes,
                    'is_universal_set_active': universal_activation.is_universal_set_active,
                    'is_universal_duration_active': universal_activation.is_universal_duration_active,
                }
        except UniversalSetActivation.DoesNotExist:
            universal_settings = {
                'universal_set_label': None,
                'universal_duration_minutes': None,
                'is_universal_set_active': False,
                'is_universal_duration_active': False,
            }
        
        # Get all trades and their question set data
        trade_data = []
        for trade in Trade.objects.all().order_by('name'):
            # Get or create ActivateSets record for this trade
            activate_sets = ActivateSets.get_or_create_for_trade(trade, request.user)
            
            # Get available question sets for current active paper type
            available_sets = []
            question_count = 0
            active_set = None
            
            if active_paper_type:
                available_sets = activate_sets.get_available_sets(active_paper_type)
                if active_paper_type == 'PRIMARY':
                    active_set = activate_sets.active_primary_set
                    question_count = activate_sets.get_question_count('PRIMARY', active_set)
                else:
                    active_set = activate_sets.active_secondary_set
                    question_count = activate_sets.get_question_count('SECONDARY', active_set)
            
            trade_data.append({
                'trade': trade,
                'activate_sets': activate_sets,
                'available_sets': available_sets,
                'active_set': active_set,
                'question_count': question_count,
            })
        
        # Get global paper type controls
        controls = list(GlobalPaperTypeControl.objects.all().order_by('paper_type'))
        
        # Get available question sets for universal activator
        available_question_sets = ['A', 'B', 'C', 'D', 'E']  # Standard question sets
        
        extra_context = extra_context or {}
        extra_context.update({
            'trade_data': trade_data,
            'active_paper_type': active_paper_type,
            'controls': controls,
            'available_question_sets': available_question_sets,
            'universal_settings': universal_settings,
            'title': 'Unified Question Set Management',
        })
        
        return super().changelist_view(request, extra_context)
    
    def _handle_post_request(self, request):
        """Handle POST requests for question set activation and global controls"""
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        action = request.POST.get('action')
        
        if action == 'activate_primary_globally':
            # Activate PRIMARY globally
            primary_control, created = GlobalPaperTypeControl.objects.get_or_create(
                paper_type='PRIMARY',
                defaults={'is_active': True, 'activated_by': request.user}
            )
            if not created:
                primary_control.is_active = True
                primary_control.activated_by = request.user
                primary_control.save()
            
            # Deactivate SECONDARY
            GlobalPaperTypeControl.objects.filter(paper_type='SECONDARY').update(is_active=False)
            
            messages.success(request, "✅ PRIMARY papers activated globally for all trades.")
            
        elif action == 'activate_secondary_globally':
            # Activate SECONDARY globally
            secondary_control, created = GlobalPaperTypeControl.objects.get_or_create(
                paper_type='SECONDARY',
                defaults={'is_active': True, 'activated_by': request.user}
            )
            if not created:
                secondary_control.is_active = True
                secondary_control.activated_by = request.user
                secondary_control.save()
            
            # Deactivate PRIMARY
            GlobalPaperTypeControl.objects.filter(paper_type='PRIMARY').update(is_active=False)
            
            messages.success(request, "✅ SECONDARY papers activated globally for all trades.")
            
        elif action == 'activate_universal_set':
            # Handle universal question set activation
            return self._handle_universal_activation(request)
        
        elif action == 'activate_universal_duration':
            # Handle universal duration activation
            return self._handle_universal_duration_activation(request)
            
        elif 'trade_id' in request.POST and 'question_set' in request.POST:
            # Handle individual trade question set activation
            trade_id = request.POST.get('trade_id')
            question_set = request.POST.get('question_set')
            paper_type = request.POST.get('paper_type')
            
            # Handle duration from new format (hours, minutes, seconds)
            duration_hours = request.POST.get('duration_hours')
            duration_minutes = request.POST.get('duration_minutes')
            duration_seconds = request.POST.get('duration_seconds')
            
            if trade_id and question_set and paper_type:
                try:
                    from reference.models import Trade
                    trade = Trade.objects.get(id=trade_id)
                    activate_sets = ActivateSets.get_or_create_for_trade(trade, request.user)
                    
                    # Update the appropriate field based on paper type
                    if paper_type == 'PRIMARY':
                        activate_sets.active_primary_set = question_set
                    else:
                        activate_sets.active_secondary_set = question_set
                    
                    activate_sets.updated_by = request.user
                    activate_sets.save()

                    # -----------------------------
                    # SAVE EXAM DURATION (UPDATED)
                    # -----------------------------

                    exam_duration = None
                    if duration_hours or duration_minutes or duration_seconds:
                        try:
                            hours = int(duration_hours) if duration_hours else 0
                            minutes = int(duration_minutes) if duration_minutes else 0
                            seconds = int(duration_seconds) if duration_seconds else 0
                            
                            # Validate ranges
                            if hours < 0 or hours > 8:
                                messages.error(request, "❌ Hours must be between 0 and 8.")
                                return HttpResponseRedirect(request.get_full_path())
                            if minutes < 0 or minutes > 59:
                                messages.error(request, "❌ Minutes must be between 0 and 59.")
                                return HttpResponseRedirect(request.get_full_path())
                            if seconds < 0 or seconds > 59:
                                messages.error(request, "❌ Seconds must be between 0 and 59.")
                                return HttpResponseRedirect(request.get_full_path())
                            
                            exam_duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                            
                        except ValueError:
                            messages.error(
                                request,
                                "❌ Invalid duration format. Please enter valid numbers."
                            )
                            return HttpResponseRedirect(request.get_full_path())

                    TradePaperActivation.objects.update_or_create(
                        trade=trade,
                        paper_type=paper_type,
                        defaults={
                            "is_active": True,
                            "exam_duration": exam_duration,
                        }
                    )
                    
                    messages.success(
                        request, 
                        f"✅ Activated question set {question_set} for {trade.name} {paper_type} papers."
                    )
                    
                except Exception as e:
                    messages.error(request, f"❌ Error activating question set: {str(e)}")
        
        # Redirect back to the same page
        return HttpResponseRedirect(request.get_full_path())
    
    def _handle_universal_activation(self, request):
        """Handle smart universal question set activation for all trades"""
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.db import transaction
        from reference.models import Trade
        
        question_set = request.POST.get('universal_question_set')
        
        # Input validation
        if not question_set or question_set not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            messages.error(request, "❌ Please select a valid question set.")
            return HttpResponseRedirect(request.get_full_path())
        
        # Get active paper type
        active_paper_type = self._get_active_paper_type()
        if not active_paper_type:
            messages.error(request, "❌ Please activate a paper type first.")
            return HttpResponseRedirect(request.get_full_path())
        
        # Smart activation: only activate for trades that have the requested set
        updated_count = 0
        skipped_count = 0
        skipped_trades = []
        
        try:
            with transaction.atomic():
                # Create or update universal set activation setting
                universal_activation, created = UniversalSetActivation.objects.get_or_create(
                    paper_type=active_paper_type,
                    defaults={
                        'universal_set_label': question_set,
                        'is_universal_set_active': True,
                        'activated_by': request.user
                    }
                )
                
                if not created:
                    universal_activation.universal_set_label = question_set
                    universal_activation.is_universal_set_active = True
                    universal_activation.activated_by = request.user
                    universal_activation.save()  # This will trigger the universal application
                
                # Get all trades in one query for better performance
                trades = list(Trade.objects.all())
                
                # Process each trade individually
                for trade in trades:
                    # Get or create ActivateSets record for this trade
                    activate_sets = ActivateSets.get_or_create_for_trade(trade, request.user)
                    
                    # Check if this trade has the requested question set available
                    available_sets = activate_sets.get_available_sets(active_paper_type)
                    
                    if question_set in available_sets:
                        # Trade has this set available - activate it
                        if active_paper_type == 'PRIMARY':
                            activate_sets.active_primary_set = question_set
                        else:
                            activate_sets.active_secondary_set = question_set
                        
                        activate_sets.updated_by = request.user
                        activate_sets.save()  # This will sync with QuestionSetActivation automatically
                        updated_count += 1
                    else:
                        # Trade doesn't have this set - skip it
                        skipped_count += 1
                        skipped_trades.append(trade.name)
                
                logger.info(f"Smart universal activation completed: Set {question_set} activated for {updated_count} trades, skipped {skipped_count} trades ({active_paper_type} papers)")
            
            # Prepare success message
            success_msg = f"🚀 Smart activation completed: Set {question_set} activated for {updated_count} trades ({active_paper_type} papers)."
            
            if skipped_count > 0:
                if skipped_count <= 5:
                    # Show specific trade names if few
                    skipped_list = ", ".join(skipped_trades)
                    success_msg += f" Skipped {skipped_count} trades without Set {question_set}: {skipped_list}."
                else:
                    # Just show count if many
                    success_msg += f" Skipped {skipped_count} trades that don't have Set {question_set} available."
            
            messages.success(request, success_msg)
            
        except Exception as e:
            messages.error(request, f"❌ Error during smart universal activation: {str(e)}")
            logger.error(f"Smart universal activation failed: {str(e)}", exc_info=True)
        
        return HttpResponseRedirect(request.get_full_path())
    
    def _handle_universal_duration_activation(self, request):
        """Handle universal duration activation for all trades"""
        from django.contrib import messages
        from django.http import HttpResponseRedirect
        from django.db import transaction
        from reference.models import Trade
        from datetime import timedelta
        
        # Get duration from either the new format (hours, minutes, seconds) or old format (total minutes)
        duration_minutes = request.POST.get('universal_duration_minutes')
        duration_hours = request.POST.get('duration_hours')
        duration_mins = request.POST.get('duration_minutes') 
        duration_secs = request.POST.get('duration_seconds')
        
        # Calculate total minutes
        total_minutes = 0
        
        if duration_minutes:
            # Old format - direct minutes input
            try:
                total_minutes = int(duration_minutes)
            except ValueError:
                messages.error(request, "❌ Please enter a valid duration.")
                return HttpResponseRedirect(request.get_full_path())
        elif duration_hours is not None or duration_mins is not None or duration_secs is not None:
            # New format - hours:minutes:seconds
            try:
                hours = int(duration_hours) if duration_hours else 0
                minutes = int(duration_mins) if duration_mins else 0
                seconds = int(duration_secs) if duration_secs else 0
                
                # Validate ranges
                if hours < 0 or hours > 8:
                    messages.error(request, "❌ Hours must be between 0 and 8.")
                    return HttpResponseRedirect(request.get_full_path())
                if minutes < 0 or minutes > 59:
                    messages.error(request, "❌ Minutes must be between 0 and 59.")
                    return HttpResponseRedirect(request.get_full_path())
                if seconds < 0 or seconds > 59:
                    messages.error(request, "❌ Seconds must be between 0 and 59.")
                    return HttpResponseRedirect(request.get_full_path())
                
                # Convert to total minutes (with fractional seconds)
                total_minutes = (hours * 60) + minutes + (seconds / 60.0)
                
            except ValueError:
                messages.error(request, "❌ Please enter valid numbers for hours, minutes, and seconds.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            messages.error(request, "❌ Please enter a valid duration.")
            return HttpResponseRedirect(request.get_full_path())
        
        if total_minutes <= 0:
            messages.error(request, "❌ Please enter a duration greater than 0.")
            return HttpResponseRedirect(request.get_full_path())
        
        # Get active paper type
        active_paper_type = self._get_active_paper_type()
        if not active_paper_type:
            messages.error(request, "❌ Please activate a paper type first.")
            return HttpResponseRedirect(request.get_full_path())
        
        try:
            with transaction.atomic():
                # Create or update universal duration setting
                universal_activation, created = UniversalSetActivation.objects.get_or_create(
                    paper_type=active_paper_type,
                    defaults={
                        'universal_duration_minutes': int(total_minutes),
                        'is_universal_duration_active': True,
                        'activated_by': request.user
                    }
                )
                
                if not created:
                    universal_activation.universal_duration_minutes = int(total_minutes)
                    universal_activation.is_universal_duration_active = True
                    universal_activation.activated_by = request.user
                    universal_activation.save()
                
                # Apply to all trades
                duration = timedelta(minutes=total_minutes)
                updated_count = 0
                
                for trade in Trade.objects.all():
                    TradePaperActivation.objects.update_or_create(
                        trade=trade,
                        paper_type=active_paper_type,
                        defaults={
                            'is_active': True,
                            'exam_duration': duration,
                        }
                    )
                    updated_count += 1
                
                # Format duration for display
                display_hours = int(total_minutes // 60)
                display_minutes = int(total_minutes % 60)
                display_seconds = int((total_minutes % 1) * 60)
                
                if display_hours > 0:
                    duration_display = f"{display_hours}h {display_minutes}m"
                    if display_seconds > 0:
                        duration_display += f" {display_seconds}s"
                else:
                    duration_display = f"{display_minutes}m"
                    if display_seconds > 0:
                        duration_display += f" {display_seconds}s"
                
                messages.success(
                    request, 
                    f"✅ Set exam duration to {duration_display} for all {updated_count} trades ({active_paper_type} papers)."
                )
                
        except Exception as e:
            messages.error(request, f"❌ Error setting universal duration: {str(e)}")
            logger.error(f"Universal duration activation failed: {str(e)}", exc_info=True)
        
        return HttpResponseRedirect(request.get_full_path())
    
    def _get_active_paper_type(self):
        """Get the currently active paper type"""
        try:
            active_control = GlobalPaperTypeControl.objects.get(is_active=True)
            return active_control.paper_type
        except GlobalPaperTypeControl.DoesNotExist:
            return None
    
    def has_add_permission(self, request):
        # Prevent manual addition - records are auto-created
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of activation records
        return False


# --------------------------------
# Global Paper Type Control (Master Control) - REPLACED BY ActivateSets
# --------------------------------
# The GlobalPaperTypeControl admin has been replaced by the unified ActivateSets interface
# which provides better user experience and simpler management.
# The model and functionality still exist but are managed through ActivateSets.

# @admin.register(GlobalPaperTypeControl)
# class GlobalPaperTypeControlAdmin(admin.ModelAdmin):
#     list_display = ['paper_type', 'is_active', 'last_activated', 'activated_by']
#     actions = ['activate_primary_globally', 'activate_secondary_globally']
#     
#     def activate_primary_globally(self, request, queryset):
#         """Activate PRIMARY papers for all trades"""
#         primary_control, created = GlobalPaperTypeControl.objects.get_or_create(
#             paper_type='PRIMARY',
#             defaults={'is_active': True, 'activated_by': request.user}
#         )
#         if not created:
#             primary_control.is_active = True
#             primary_control.activated_by = request.user
#             primary_control.save()
#         
#         # Deactivate SECONDARY
#         GlobalPaperTypeControl.objects.filter(paper_type='SECONDARY').update(is_active=False)
#         
#         self.message_user(request, "✅ PRIMARY papers activated globally. Use 'Activate Sets' to manage question sets per trade.")
#     activate_primary_globally.short_description = "🔵 Activate PRIMARY globally"
#     
#     def activate_secondary_globally(self, request, queryset):
#         """Activate SECONDARY papers for all trades"""
#         secondary_control, created = GlobalPaperTypeControl.objects.get_or_create(
#             paper_type='SECONDARY',
#             defaults={'is_active': True, 'activated_by': request.user}
#         )
#         if not created:
#             secondary_control.is_active = True
#             secondary_control.activated_by = request.user
#             secondary_control.save()
#         
#         # Deactivate PRIMARY
#         GlobalPaperTypeControl.objects.filter(paper_type='PRIMARY').update(is_active=False)
#         
#         self.message_user(request, "✅ SECONDARY papers activated globally. Use 'Activate Sets' to manage question sets per trade.")
#     activate_secondary_globally.short_description = "🟠 Activate SECONDARY globally"
#     
#     def has_add_permission(self, request):
#         # Only allow PRIMARY and SECONDARY entries
#         return GlobalPaperTypeControl.objects.count() < 2
#     
#     def has_delete_permission(self, request, obj=None):
#         # Prevent deletion of control entries
#         return False

# --------------------------------
# Global Paper Type Control (Master Control) - REMOVED FROM ADMIN
# --------------------------------
# The GlobalPaperTypeControl admin interface has been removed to avoid duplication
# with the ActivateSets interface. All functionality is now available through
# the unified ActivateSets admin page at /admin/questions/activatesets/
#
# The GlobalPaperTypeControl model still exists and functions normally for
# programmatic access and backend operations, but is no longer exposed in admin.
#
# To manage paper types and question sets, use the ActivateSets interface which
# provides the same functionality with a better user experience.