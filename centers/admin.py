from django.contrib import admin
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.urls import path
import json

from .models import Center, EXAM_CENTER_CHOICES
from .forms import CenterAdminForm


@admin.register(Center)
class CenterAdmin(admin.ModelAdmin):
    form = CenterAdminForm
    list_display = ("comd", "exam_Center", "is_active")
    list_filter = ("comd", "is_active")
    search_fields = ("comd", "exam_Center")

    class Media:
        js = ("admin/js/exam_center_filter.js",)

    def get_urls(self):
        """Add custom URL for AJAX requests"""
        urls = super().get_urls()
        custom_urls = [
            path('get-exam-centers/', self.admin_site.admin_view(self.get_exam_centers), name='get_exam_centers'),
        ]
        return custom_urls + urls

    def get_exam_centers(self, request):
        """AJAX endpoint to get exam centers based on command"""
        comd = request.GET.get('comd', '')
        if comd in EXAM_CENTER_CHOICES:
            centers = EXAM_CENTER_CHOICES[comd]
            return JsonResponse({'centers': centers})
        return JsonResponse({'centers': []})

    def render_change_form(self, request, context, *args, **kwargs):
        """Inject exam center choices for JavaScript"""
        # Add exam center choices to context
        extra_context = {
            'exam_center_choices_json': json.dumps(EXAM_CENTER_CHOICES)
        }
        context.update(extra_context)
        return super().render_change_form(request, context, *args, **kwargs)