# at top of your views.py - ensure these imports exist (add any you don't already have)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.views.decorators.cache import never_cache
from django.db.models import Count
from .models import CandidateProfile
from reference.models import Trade
from .forms import CandidateRegistrationForm
from django.contrib import messages
from django.db import transaction
from questions.models import QuestionPaper, Question, ExamSession
from results.models import CandidateAnswer
from django.db.models import Q
# other imports you already had
from django.http import FileResponse, Http404
import os, tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.pdfencrypt import StandardEncryption
from django.conf import settings
from django.utils import timezone
from questions.models import TradePaperActivation
from django.contrib.auth.views import LoginView
from django.urls import reverse

class CandidateLoginView(LoginView):
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        unified_enabled = bool(getattr(settings, "EXAM_UNIFIED_DAT_ENABLED", False))

        if unified_enabled:
            any_exam_active = TradePaperActivation.objects.filter(is_active=True).exists()
        else:
            any_exam_active = QuestionPaper.objects.filter(is_active=True).exists()

        # Check for specific no-slot or slot-consumed messages
        no_slot_msg = self.request.GET.get("no_slot")
        slot_consumed_msg = self.request.GET.get("slot_consumed")
        
        ctx["show_no_exam_banner"] = (not any_exam_active) or (
            self.request.GET.get("no_exam") == "1"
        )
        ctx["show_no_slot_banner"] = no_slot_msg == "1"
        ctx["show_slot_consumed_banner"] = slot_consumed_msg == "1"
        
        return ctx


@login_required
def candidate_dashboard(request):
    candidate_profile = get_object_or_404(CandidateProfile, user=request.user)
    exams_scheduled, upcoming_exams, completed_exams, results = [], [], [], []
    return render(request, "registration/dashboard.html", {
        "candidate": candidate_profile,
        "exams_scheduled": exams_scheduled,
        "upcoming_exams": upcoming_exams,
        "completed_exams": completed_exams,
        "results": results,
    })


def register_candidate(request):
    if request.method == "POST":
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")
        else:
            print("Registration form invalid:", form.errors)
    else:
        form = CandidateRegistrationForm()
    return render(request, "registration/register_candidate.html", {"form": form})


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from questions.models import QuestionPaper, Question
from results.models import CandidateAnswer
from registration.models import CandidateProfile

# registration/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from questions.models import Question, QuestionPaper
from results.models import CandidateAnswer
from registration.models import CandidateProfile
from django.views.decorators.cache import never_cache

@never_cache
@login_required
def exam_interface(request):
    try:
        candidate = get_object_or_404(CandidateProfile, user=request.user)
        trade = candidate.trade

        if not trade:
            messages.error(request, "Trade not assigned. Contact admin.")
            logout(request)
            return redirect("login")

        # Check if candidate can start exam (includes slot validation)
        if not candidate.can_start_exam:
            if not candidate.has_exam_slot:
                messages.error(request, "No exam slot assigned. Contact admin to assign an exam slot.")
                logout(request)
                return redirect(f"{reverse('login')}?no_slot=1")
            elif candidate.slot_consumed_at:
                # Check if this is a fresh slot (assigned after consumption)
                if candidate.slot_assigned_at and candidate.slot_consumed_at and candidate.slot_assigned_at > candidate.slot_consumed_at:
                    # Fresh slot assigned after consumption - allow exam
                    pass
                else:
                    messages.error(request, f"Exam slot already used on {candidate.slot_consumed_at.strftime('%Y-%m-%d %H:%M')}. Contact admin to assign a new slot.")
                    logout(request)
                    return redirect(f"{reverse('login')}?slot_consumed=1")
            else:
                messages.error(request, f"No active exam found for trade {trade}. Contact admin.")
                logout(request)
                return redirect("login")

        unified_enabled = bool(getattr(settings, "EXAM_UNIFIED_DAT_ENABLED", False))

        # -----------------------------
        # STEP 1: Resolve activation
        # -----------------------------
        activation = TradePaperActivation.objects.filter(
            trade=trade,
            is_active=True
        ).order_by(
            # PRIMARY preferred over SECONDARY
            "paper_type"
        ).first()

        if not activation:
            messages.error(request, f"No active exam found for trade {trade}. Contact admin.")
            return redirect(f"{reverse('login')}?no_exam=1")

        # -----------------------------
        # STEP 2: Resolve paper
        # -----------------------------
        paper = QuestionPaper.objects.filter(
            question_paper=activation.paper_type,
            is_active=True
        ).first()

        if not paper:
            messages.error(request, f"Exam paper configuration missing for {activation.paper_type}. Contact admin.")
            logout(request)
            return redirect("login")

        # -----------------------------
        # STEP 3: Ensure questions exist (CRITICAL)
        # -----------------------------
        if activation.paper_type == "PRIMARY":
            q_count = Question.objects.filter(
                trade=trade,
                paper_type="PRIMARY",
                is_active=True
            ).count()
        else:
            q_count = Question.objects.filter(
                paper_type="SECONDARY",
                is_common=True,
                is_active=True
            ).count()

        if q_count == 0:
            messages.error(
                request,
                f"No questions configured for {trade} ({activation.paper_type}). Contact admin."
            )
            logout(request)
            return redirect("login")

        # -----------------------------
        # STEP 4: Resume or create session
        # -----------------------------
        session = ExamSession.objects.filter(
            user=request.user,
            paper=paper,
            completed_at__isnull=True
        ).order_by("-started_at").first()

        if not session:
            try:
                # MARK EXAM ATTEMPT START (FIRST TIME LOGIN TO EXAM)
                if not candidate.start_exam_attempt():
                    # If already attempting, that's fine - continue with existing attempt
                    pass
                
                session = paper.generate_for_candidate(
                    user=request.user,
                    trade=trade
                )

                if activation.exam_duration:
                    session.duration = activation.exam_duration
                    session.save(update_fields=["duration"])
            except ValidationError as e:
                messages.error(request, f"Error creating exam session: {str(e)}")
                logout(request)
                return redirect("login")

        # -----------------------------
        # STEP 5: Prevent reattempt
        # -----------------------------
        if session.completed_at:
            messages.info(request, "Exam already submitted.")
            logout(request)
            return redirect("exam_success")

        duration_seconds = int(
            session.duration.total_seconds()
            if session.duration else paper.exam_duration.total_seconds()
        )

        # -----------------------------
        # STEP 6: SUBMISSION
        # -----------------------------
        if request.method == "POST":
            with transaction.atomic():
                # Check if exam was terminated
                exam_terminated = request.POST.get('exam_terminated') == 'true'
                termination_reason = request.POST.get('termination_reason', 'Normal submission')
                
                for key, value in request.POST.items():
                    if key.startswith("question_"):
                        qid = key.split("_")[1]
                        try:
                            question = Question.objects.get(id=qid)
                            CandidateAnswer.objects.update_or_create(
                                candidate=candidate,
                                paper=paper,
                                question=question,
                                defaults={"answer": value},
                            )
                        except Question.DoesNotExist:
                            continue

                session.completed_at = timezone.now()
                session.save(update_fields=["completed_at"])
                
                # CONSUME SLOT ONLY WHEN EXAM IS ACTUALLY SUBMITTED/COMPLETED
                candidate.consume_exam_slot()
                
                # Log termination if applicable
                if exam_terminated:
                    # You can add additional logging here if needed
                    messages.warning(request, f"Exam was terminated: {termination_reason}")

            logout(request)
            # Show success message
            messages.success(request, "🎉 Your exam has been submitted successfully! Thank you for participating.")
            return redirect("exam_success")

        # -----------------------------
        # STEP 7: RENDER EXAM
        # -----------------------------
        
        return render(request, "registration/exam_interface.html", {
            "candidate": candidate,
            "paper": paper,
            "session": session,
            "questions": session.questions,
            "duration_seconds": duration_seconds,
        })
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("login")

# @login_required
# def exam_success(request):
#     return render(request, "registration/exam_success.html")


# views.py
from django.shortcuts import render
from django.views.decorators.cache import never_cache
def exam_success(request):
    # Your existing success view is fine; @never_cache adds no-store headers.
    return render(request, "registration/exam_success.html")

@never_cache
def exam_goodbye(request):
    # NEW: the goodbye view (non-cacheable)
    return render(request, "registration/exam_goodbye.html")

def export_answers_pdf(request, candidate_id):
    try:
        answers = CandidateAnswer.objects.filter(candidate_id=candidate_id).select_related(
            "candidate", "paper", "question"
        )
        if not answers.exists():
            raise Http404("No answers found for this candidate.")

        candidate = answers[0].candidate
        army_no = getattr(candidate, "army_no", candidate.user.username)
        candidate_name = candidate.user.get_full_name()

        filename = f"{army_no}_answers.pdf"
        tmp_path = os.path.join(tempfile.gettempdir(), filename)

        enc = StandardEncryption(
            userPassword=army_no,
            ownerPassword="sarthak",
            canPrint=1,
            canModify=0,
            canCopy=0,
            canAnnotate=0
        )

        c = canvas.Canvas(tmp_path, pagesize=A4, encrypt=enc)
        width, height = A4
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "Candidate Answers Export")
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, height - 1.5 * inch, f"Army No: {army_no}")
        c.drawString(1 * inch, height - 1.8 * inch, f"Name: {candidate_name}")
        c.drawString(1 * inch, height - 2.1 * inch, f"Trade: {candidate.trade}")
        c.drawString(1 * inch, height - 2.4 * inch, f"Paper: {answers[0].paper.title}")

        y = height - 3 * inch
        c.setFont("Helvetica", 11)
        for idx, ans in enumerate(answers, start=1):
            question_text = (ans.question.text[:80] + "...") if len(ans.question.text) > 80 else ans.question.text
            c.drawString(1 * inch, y, f"Q{idx}: {question_text}")
            y -= 0.3 * inch
            c.drawString(1.2 * inch, y, f"Answer: {ans.answer}")
            y -= 0.5 * inch
            if y < 1.5 * inch:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = height - 1 * inch

        c.save()
        return FileResponse(open(tmp_path, "rb"), as_attachment=True, filename=filename)

    except Exception as e:
        raise Http404(f"Error exporting candidate answers: {e}")
    



# views.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CandidateProfile  # adjust to your model

@login_required
def clear_shift_and_start_exam(request):
    # Direct redirect to exam interface - no need to clear shift
    return redirect("exam_interface")

@login_required
def debug_exam(request):
    """Debug view to test exam data structure"""
    try:
        candidate = get_object_or_404(CandidateProfile, user=request.user)
        trade = candidate.trade

        if not trade:
            return render(request, "registration/debug_exam.html", {
                "error": "Trade not assigned"
            })

        # Get activation
        activation = TradePaperActivation.objects.filter(
            trade=trade,
            is_active=True
        ).order_by("paper_type").first()

        if not activation:
            return render(request, "registration/debug_exam.html", {
                "error": "No active exam found"
            })

        # Get paper
        paper = QuestionPaper.objects.filter(
            question_paper=activation.paper_type,
            is_active=True
        ).first()

        if not paper:
            return render(request, "registration/debug_exam.html", {
                "error": "No paper found"
            })

        # Get or create session
        session = ExamSession.objects.filter(
            user=request.user,
            paper=paper,
            completed_at__isnull=True
        ).order_by("-started_at").first()

        if not session:
            session = paper.generate_for_candidate(
                user=request.user,
                trade=trade
            )

        return render(request, "registration/debug_exam.html", {
            "candidate": candidate,
            "paper": paper,
            "session": session,
            "questions": session.questions.all(),
            "activation": activation,
        })
        
    except Exception as e:
        import traceback
        return render(request, "registration/debug_exam.html", {
            "error": f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        })
@login_required
def simple_exam_test(request):
    """Simple test view to isolate the question display issue"""
    try:
        candidate = get_object_or_404(CandidateProfile, user=request.user)
        trade = candidate.trade

        if not trade:
            return render(request, "registration/simple_exam_test.html", {
                "error": "Trade not assigned"
            })

        # Get activation
        activation = TradePaperActivation.objects.filter(
            trade=trade,
            is_active=True
        ).order_by("paper_type").first()

        if not activation:
            return render(request, "registration/simple_exam_test.html", {
                "error": "No active exam found"
            })

        # Get paper
        paper = QuestionPaper.objects.filter(
            question_paper=activation.paper_type,
            is_active=True
        ).first()

        if not paper:
            return render(request, "registration/simple_exam_test.html", {
                "error": "No paper found"
            })

        # Get or create session
        session = ExamSession.objects.filter(
            user=request.user,
            paper=paper,
            completed_at__isnull=True
        ).order_by("-started_at").first()

        if not session:
            session = paper.generate_for_candidate(
                user=request.user,
                trade=trade
            )

        return render(request, "registration/simple_exam_test.html", {
            "candidate": candidate,
            "paper": paper,
            "session": session,
            "questions": session.questions.all(),
        })
        
    except Exception as e:
        import traceback
        return render(request, "registration/simple_exam_test.html", {
            "error": f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        })