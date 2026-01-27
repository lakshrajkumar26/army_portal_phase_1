from django.contrib import admin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import path
from django.http import HttpResponseRedirect
from django.core.management import call_command
from io import StringIO
from .models import ExamDataCleanup, CompleteCleanup, ExamSlotCleanup


@admin.register(ExamDataCleanup)
class ExamDataCleanupAdmin(admin.ModelAdmin):
    """Admin interface for exam data cleanup"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view with cleanup buttons"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Exam Data Cleanup'
        extra_context['has_add_permission'] = False
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clean-questions/', self.admin_site.admin_view(self.clean_questions_view), name='deletedata_examdatacleanup_clean_questions'),
            path('clean-exam-data/', self.admin_site.admin_view(self.clean_exam_data_view), name='deletedata_examdatacleanup_clean_exam_data'),
            path('clean-exam-slots/', self.admin_site.admin_view(self.clean_exam_slots_view), name='deletedata_examdatacleanup_clean_exam_slots'),
            path('delete-candidates/', self.admin_site.admin_view(self.delete_candidates_view), name='deletedata_examdatacleanup_delete_candidates'),
        ]
        return custom_urls + urls
    
    def clean_questions_view(self, request):
        """Clean only questions and question papers"""
        try:
            output = StringIO()
            call_command('cleanup_exam_data', '--level=questions', '--confirm', stdout=output)
            messages.success(request, 'Questions and question papers deleted successfully!')
            messages.info(request, f'Details: {output.getvalue()}')
        except Exception as e:
            messages.error(request, f'Error during cleanup: {str(e)}')
        
        return redirect('admin:deletedata_examdatacleanup_changelist')
    
    def clean_exam_data_view(self, request):
        """Clean all exam data but keep user registrations"""
        try:
            output = StringIO()
            call_command('cleanup_exam_data', '--level=exam-data', '--confirm', stdout=output)
            messages.success(request, 'Exam data deleted successfully! User registrations preserved.')
            messages.info(request, f'Details: {output.getvalue()}')
        except Exception as e:
            messages.error(request, f'Error during cleanup: {str(e)}')
        
        return redirect('admin:deletedata_examdatacleanup_changelist')
    
    def clean_exam_slots_view(self, request):
        """Clean only exam slots"""
        try:
            from registration.models import CandidateProfile
            count = CandidateProfile.objects.filter(has_exam_slot=True).count()
            CandidateProfile.objects.update(
                has_exam_slot=False,
                slot_assigned_at=None,
                slot_consumed_at=None,
                slot_assigned_by=None
            )
            messages.success(request, f'Reset {count} exam slots successfully!')
        except Exception as e:
            messages.error(request, f'Error resetting exam slots: {str(e)}')
        
        return redirect('admin:deletedata_examdatacleanup_changelist')
    
    def delete_candidates_view(self, request):
        """Delete all candidate registrations and profiles"""
        try:
            output = StringIO()
            call_command('cleanup_exam_data', '--level=candidates', '--confirm', stdout=output)
            messages.success(request, 'All candidate registrations deleted successfully! Questions and exam data preserved.')
            messages.info(request, f'Details: {output.getvalue()}')
        except Exception as e:
            messages.error(request, f'Error deleting candidates: {str(e)}')
        
        return redirect('admin:deletedata_examdatacleanup_changelist')


@admin.register(CompleteCleanup)
class CompleteCleanupAdmin(admin.ModelAdmin):
    """Admin interface for complete cleanup"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Custom changelist view with cleanup buttons"""
        extra_context = extra_context or {}
        extra_context['title'] = 'Complete System Cleanup'
        extra_context['has_add_permission'] = False
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clean-everything/', self.admin_site.admin_view(self.clean_everything_view), name='deletedata_completecleanup_clean_everything'),
        ]
        return custom_urls + urls
    
    def clean_everything_view(self, request):
        """Clean everything - complete reset"""
        try:
            output = StringIO()
            call_command('cleanup_exam_data', '--level=everything', '--confirm', stdout=output)
            messages.success(request, 'Complete system reset performed! All data deleted except admin accounts.')
            messages.info(request, f'Details: {output.getvalue()}')
        except Exception as e:
            messages.error(request, f'Error during complete cleanup: {str(e)}')
        
        return redirect('admin:deletedata_completecleanup_changelist')