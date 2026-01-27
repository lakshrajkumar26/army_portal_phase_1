# questions/admin.py
from django.contrib import admin, messages

from .models import (
    Question,
    QuestionUpload,
    TradePaperActivation,
    QuestionSetActivation,
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
# Trade Paper Activation (ONLY CONTROL PANEL)
# --------------------------------
@admin.register(TradePaperActivation)
class TradePaperActivationAdmin(admin.ModelAdmin):
    """
    This is the ONLY exam control screen admin should use.
    """
    list_display = ("trade", "paper_type", "is_active", "exam_duration")
    list_filter = ("paper_type", "is_active", "trade")
    ordering = ("trade__code", "paper_type")
    fields = ("trade", "paper_type", "is_active", "exam_duration")

    def has_add_permission(self, request):
        # 🔒 Prevent manual creation (rows will be auto-created)
        return False

    def has_delete_permission(self, request, obj=None):
        # 🔒 Prevent deletion
        return False


# --------------------------------
# Question Set Activation Management
# --------------------------------
@admin.register(QuestionSetActivation)
class QuestionSetActivationAdmin(admin.ModelAdmin):
    list_display = ['trade', 'paper_type', 'question_set', 'is_active', 'activated_at', 'activated_by']
    list_filter = ['paper_type', 'is_active', 'question_set', 'trade']
    search_fields = ['trade__name', 'trade__code']
    actions = ['activate_selected_sets', 'deactivate_selected_sets']
    ordering = ['trade__code', 'paper_type', 'question_set']
    
    def activate_selected_sets(self, request, queryset):
        """Bulk activate selected question sets"""
        activated_count = 0
        for activation in queryset:
            activation.is_active = True
            activation.activated_by = request.user
            activation.save()
            activated_count += 1
        
        self.message_user(
            request,
            f"Successfully activated {activated_count} question sets."
        )
    activate_selected_sets.short_description = "Activate selected question sets"
    
    def deactivate_selected_sets(self, request, queryset):
        """Bulk deactivate selected question sets"""
        deactivated_count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {deactivated_count} question sets."
        )
    deactivate_selected_sets.short_description = "Deactivate selected question sets"


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
