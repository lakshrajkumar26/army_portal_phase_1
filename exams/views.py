# exams/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from exams.models import ExamAssignment, ExamAttempt

@login_required
def candidate_dashboard(request):
    user = request.user

    # Profile info
    profile = {
        "name": user.get_full_name(),
        "username": user.username,
    }

    # Exam registrations
    assignments = ExamAssignment.objects.filter(candidate=user).select_related(
        "center", "shift", "primary_paper", "common_paper"
    )

    # Exam results
    results = ExamAttempt.objects.filter(assignment__candidate=user)

    return render(request, "registration/dashboard.html", {
        "profile": profile,
        "assignments": assignments,
        "results": results,
    })
