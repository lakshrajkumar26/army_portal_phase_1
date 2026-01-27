# questions/admin.py
from django.contrib import admin, messages
from django.urls import path
from django.utils.html import format_html

from .models import (
    Question,
    QuestionUpload,
    GlobalPaperTypeControl,
)
from .forms import QuestionUploadForm


# --------------------------------
# Question Bank (QP Delete)
# --------------------------------
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "part",
        "short_text",
        "trade",
        "paper_type",
        "question_set",
        "is_active",
        "created_at",
    )
    list_filter = ("paper_type", "is_active", "trade", "part", "question_set")
    search_fields = ("text",)
    ordering = ("-created_at",)
    list_per_page = 50
    
    fieldsets = (
        ('Question Details', {
            'fields': ('text', 'part', 'marks', 'trade', 'paper_type', 'question_set')
        }),
        ('Options (New Format)', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
            'classes': ('collapse',)
        }),
        ('Legacy Options', {
            'fields': ('options', 'correct_answer'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_common', 'is_active')
        }),
    )

    def short_text(self, obj):
        return obj.text[:80]

    short_text.short_description = "Question"


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
# Global Paper Type Control (Master Control)
# --------------------------------
@admin.register(GlobalPaperTypeControl)
class GlobalPaperTypeControlAdmin(admin.ModelAdmin):
    list_display = ['paper_type', 'is_active', 'last_activated', 'activated_by']
    actions = ['activate_primary_globally', 'activate_secondary_globally']
    
    def activate_primary_globally(self, request, queryset):
        """Activate PRIMARY papers for all trades"""
        from .models import GlobalPaperTypeControl
        primary_control, created = GlobalPaperTypeControl.objects.get_or_create(
            paper_type='PRIMARY',
            defaults={'is_active': True, 'activated_by': request.user}
        )
        if not created:
            primary_control.is_active = True
            primary_control.activated_by = request.user
            primary_control.save()
        
        self.message_user(request, "PRIMARY papers activated globally for all trades.")
    activate_primary_globally.short_description = "Activate PRIMARY globally"
    
    def activate_secondary_globally(self, request, queryset):
        """Activate SECONDARY papers for all trades"""
        from .models import GlobalPaperTypeControl
        secondary_control, created = GlobalPaperTypeControl.objects.get_or_create(
            paper_type='SECONDARY',
            defaults={'is_active': True, 'activated_by': request.user}
        )
        if not created:
            secondary_control.is_active = True
            secondary_control.activated_by = request.user
            secondary_control.save()
        
        self.message_user(request, "SECONDARY papers activated globally for all trades.")
    activate_secondary_globally.short_description = "Activate SECONDARY globally"
    
    def has_add_permission(self, request):
        # Only allow PRIMARY and SECONDARY entries
        return GlobalPaperTypeControl.objects.count() < 2
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of control entries
        return False
