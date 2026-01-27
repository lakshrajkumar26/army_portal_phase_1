"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from config.admin_views import cleanup_questions_view, cleanup_exam_data_view, cleanup_everything_view

def home(request):
    return redirect('candidate/login/')

# Add custom admin URLs
admin_custom_urls = [
    path('cleanup-questions/', cleanup_questions_view, name='cleanup_questions'),
    path('cleanup-exam-data/', cleanup_exam_data_view, name='cleanup_exam_data'),
    path('cleanup-everything/', cleanup_everything_view, name='cleanup_everything'),
]

# Monkey patch the admin site to add our custom URLs
original_get_urls = admin.site.get_urls

def get_urls_with_custom():
    return admin_custom_urls + original_get_urls()

admin.site.get_urls = get_urls_with_custom

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home),
    path("candidate/", include("registration.urls")),
    path("results/", include("results.urls")),
    


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
