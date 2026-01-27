# questions/admin.py
from django.contrib import admin, messages

from .models import (
    Question,
    QuestionUpload,
    TradePaperActivation,
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
        "is_active",
        "created_at",
    )
    list_filter = ("paper_type", "is_active", "trade", "part")
    search_fields = ("text",)
    ordering = ("-created_at",)
    list_per_page = 50

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
