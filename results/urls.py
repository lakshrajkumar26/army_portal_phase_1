from django.urls import path
from . import views

urlpatterns = [
    path("export-csv/", views.export_answers_pdf, name="export_answers_pdf"),
]
