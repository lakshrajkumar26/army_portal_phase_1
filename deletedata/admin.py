from django.contrib import admin
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import path
from django.http import HttpResponseRedirect
from django.core.management import call_command
from io import StringIO
from .models import ExamDataCleanup


@admin.register(ExamDataCleanup)
class ExamDataCleanupAdmin(admin.ModelAdmin):
    """Admin interface for data management - no database interaction"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj=None):
        return True
    
    def get_queryset(self, request):
        # Return empty queryset to prevent database access
        return ExamDataCleanup.objects.none()
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view with cleanup buttons"""
        extra_context = extra_context or {}
        extra_context.update({
            'title': 'Data Management System',
            'has_add_permission': False,
            'has_change_permission': False,
            'has_delete_permission': False,
        })
        return render(request, 'admin/deletedata/examdatacleanup/change_list.html', extra_context)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('clean-exam-data/', self.admin_site.admin_view(self.clean_exam_data_view), name='deletedata_examdatacleanup_clean_exam_data'),
            path('clean-everything/', self.admin_site.admin_view(self.clean_everything_view), name='deletedata_examdatacleanup_clean_everything'),
        ]
        return custom_urls + urls
    
    def clean_exam_data_view(self, request):
        """Clean all exam data but keep user registrations"""
        try:
            output = StringIO()
            call_command('cleanup_exam_data', '--level=exam-data', '--confirm', '--debug', stdout=output)
            messages.success(request, 'Exam data deleted successfully! User registrations preserved.')
            messages.info(request, f'Debug Details: {output.getvalue()}')
        except Exception as e:
            messages.error(request, f'Error during cleanup: {str(e)}')
            # Add debug information to help troubleshoot
            import traceback
            messages.error(request, f'Debug traceback: {traceback.format_exc()}')
        
        return redirect('admin:deletedata_examdatacleanup_changelist')
    
    def clean_everything_view(self, request):
        """Clean everything - complete reset"""
        try:
            output = StringIO()
            call_command('cleanup_exam_data', '--level=everything', '--confirm', '--debug', stdout=output)
            messages.success(request, 'Complete system reset performed! All data deleted except admin accounts.')
            messages.info(request, f'Debug Details: {output.getvalue()}')
        except Exception as e:
            messages.error(request, f'Error during complete cleanup: {str(e)}')
            # Add debug information to help troubleshoot
            import traceback
            messages.error(request, f'Debug traceback: {traceback.format_exc()}')
        
        return redirect('admin:deletedata_examdatacleanup_changelist')

# Remove the CompleteCleanup admin since we're consolidating everything into ExamDataCleanup