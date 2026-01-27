from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("register/", views.register_candidate, name="register_candidate"),
    path("login/", views.CandidateLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="registration/login.html"), name="logout"),
    path("dashboard/", views.candidate_dashboard, name="candidate_dashboard"),
    path("exam_interface/", views.exam_interface, name="exam_interface"),  # New URL pattern
    path("export-candidate/<int:candidate_id>/", views.export_answers_pdf, name="export_candidate_pdf"),
    path("exam_success/", views.exam_success, name="exam_success"),
    path("exam/goodbye/", views.exam_goodbye, name="exam_goodbye"),
    path("start-exam/", views.clear_shift_and_start_exam, name="clear_shift_and_start_exam"),
    path("debug_exam/", views.debug_exam, name="debug_exam"),
    path("simple_exam_test/", views.simple_exam_test, name="simple_exam_test"),
]
