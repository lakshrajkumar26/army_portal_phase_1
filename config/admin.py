"""
Custom admin site configuration with cleanup operations
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from io import StringIO
import sys


class CustomAdminSite(admin.AdminSite):
    """Custom admin site with cleanup operations"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('cleanup-questions/', self.admin_view(self.cleanup_questions_view), name='cleanup_questions'),
            path('cleanup-exam-data/', self.admin_view(self.cleanup_exam_data_view), name='cleanup_exam_data'),
            path('cleanup-everything/', self.admin_view(self.cleanup_everything_view), name='cleanup_everything'),
        ]
        return custom_urls + urls
    
    def cleanup_questions_view(self, request):
        """Clean only questions and question papers"""
        if request.method == 'POST':
            try:
                # Capture command output
                output = StringIO()
                call_command('cleanup_exam_data', '--level=questions', '--confirm', stdout=output)
                
                messages.success(request, 'Questions and question papers deleted successfully!')
                messages.info(request, f'Command output: {output.getvalue()}')
                
            except Exception as e:
                messages.error(request, f'Error during cleanup: {str(e)}')
            
            return redirect('admin:index')
        
        # Show confirmation page
        return render(request, 'admin/cleanup_confirmation.html', {
            'title': 'Clean Questions & Papers',
            'description': 'This will delete all questions and question papers only.',
            'action_url': 'admin:cleanup_questions',
            'button_text': 'Delete Questions & Papers',
            'button_class': 'btn-info'
        })
    
    def cleanup_exam_data_view(self, request):
        """Clean exam data but keep user registrations"""
        if request.method == 'POST':
            try:
                # Capture command output
                output = StringIO()
                call_command('cleanup_exam_data', '--level=exam-data', '--confirm', stdout=output)
                
                messages.success(request, 'Exam data deleted successfully! User registrations preserved.')
                messages.info(request, f'Command output: {output.getvalue()}')
                
            except Exception as e:
                messages.error(request, f'Error during cleanup: {str(e)}')
            
            return redirect('admin:index')
        
        # Show confirmation page
        return render(request, 'admin/cleanup_confirmation.html', {
            'title': 'Clean Exam Data',
            'description': 'This will delete all exam-related data but preserve user registrations.',
            'details': [
                'Questions and question papers',
                'Exam sessions and results', 
                'Uploaded question files',
                'Trade paper activations'
            ],
            'preserved': ['User registrations', 'Admin accounts'],
            'action_url': 'admin:cleanup_exam_data',
            'button_text': 'Delete Exam Data',
            'button_class': 'btn-warning'
        })
    
    def cleanup_everything_view(self, request):
        """Clean everything including user registrations"""
        if request.method == 'POST':
            try:
                # Capture command output
                output = StringIO()
                call_command('cleanup_exam_data', '--level=complete', '--confirm', stdout=output)
                
                messages.success(request, 'Complete system reset performed! All data deleted except admin accounts.')
                messages.info(request, f'Command output: {output.getvalue()}')
                
            except Exception as e:
                messages.error(request, f'Error during cleanup: {str(e)}')
            
            return redirect('admin:index')
        
        # Show confirmation page
        return render(request, 'admin/cleanup_confirmation.html', {
            'title': 'Complete System Reset',
            'description': 'This will delete ALL data including user registrations!',
            'details': [
                'All user registrations and profiles',
                'All exam data and sessions',
                'All questions and question papers',
                'All uploaded files',
                'All exam results and answers'
            ],
            'preserved': ['Admin/superuser accounts only'],
            'action_url': 'admin:cleanup_everything',
            'button_text': 'DELETE EVERYTHING',
            'button_class': 'btn-danger',
            'is_danger': True
        })


# Create custom admin site instance
admin_site = CustomAdminSite(name='custom_admin')

# Copy all registered models from default admin site
for model, admin_class in admin.site._registry.items():
    admin_site.register(model, admin_class.__class__)