# registration/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import logging

from questions.models import (
    QuestionPaper,
    ExamSession,
    TradePaperActivation,
)
from reference.models import Trade
from results.models import CandidateAnswer

logger = logging.getLogger(__name__)


@login_required
def exam_interface(request):
    """
    Main exam interface.

    SAFETY GUARANTEES:
    - Does NOT break legacy flow when unified flag is OFF
    - Uses per-trade activation ONLY when enabled
    - Submission + result logic remains unchanged
    """

    user = request.user

    # ------------------------------------------------
    # Fetch candidate trade (existing behavior)
    # ------------------------------------------------
    try:
        trade_obj = user.candidateprofile.trade
    except Exception:
        trade_obj = None

    # ------------------------------------------------
    # Helper: pick paper safely
    # ------------------------------------------------
    def pick_paper_for_trade(trade):
        """
        Paper selection logic.

        Priority:
        1) If unified flag OFF → legacy global behavior
        2) If unified flag ON → per-trade activation
            - Prefer PRIMARY
            - Else SECONDARY
        """

        # ---------- LEGACY MODE ----------
        if not getattr(settings, "EXAM_UNIFIED_DAT_ENABLED", False):
            paper = QuestionPaper.objects.filter(
                question_paper="PRIMARY",
                is_active=True,
            ).first()

            if not paper:
                paper = QuestionPaper.objects.filter(
                    question_paper="SECONDARY",
                    is_active=True,
                ).first()

            return paper

        # ---------- UNIFIED MODE ----------
        if not trade:
            return None

        primary_active = TradePaperActivation.objects.filter(
            trade=trade,
            paper_type="PRIMARY",
            is_active=True,
        ).first()

        if primary_active:
            return QuestionPaper.objects.filter(question_paper="PRIMARY").first()

        secondary_active = TradePaperActivation.objects.filter(
            trade=trade,
            paper_type="SECONDARY",
            is_active=True,
        ).first()

        if secondary_active:
            return QuestionPaper.objects.filter(question_paper="SECONDARY").first()

        return None

    # ------------------------------------------------
    # Pick paper
    # ------------------------------------------------
    paper = pick_paper_for_trade(trade_obj)

    logger.info(
        "Exam selection | user=%s trade=%s unified=%s paper=%s",
        user.username,
        getattr(trade_obj, "code", None),
        getattr(settings, "EXAM_UNIFIED_DAT_ENABLED", False),
        getattr(paper, "question_paper", None) if paper else None,
    )

    if not paper:
        messages.error(request, "No exam is active for your trade at the moment.")
        return redirect("logout")

    # ------------------------------------------------
    # Resume or create session
    # ------------------------------------------------
    session = ExamSession.objects.filter(
        user=user,
        paper=paper,
        completed_at__isnull=True,
    ).first()

    if not session:
        session = paper.generate_for_candidate(
            user=user,
            trade=trade_obj,
        )

    # ------------------------------------------------
    # Duration handling (per-trade override)
    # ------------------------------------------------
    duration_seconds = None

    if getattr(settings, "EXAM_UNIFIED_DAT_ENABLED", False) and trade_obj:
        activation = TradePaperActivation.objects.filter(
            trade=trade_obj,
            paper_type=paper.question_paper,
        ).first()

        if activation and activation.exam_duration:
            duration_seconds = int(activation.exam_duration.total_seconds())

    if duration_seconds is None:
        if session.duration:
            duration_seconds = int(session.duration.total_seconds())
        else:
            duration_seconds = int(paper.exam_duration.total_seconds())

    # ------------------------------------------------
    # Handle submission
    # ------------------------------------------------
    if request.method == "POST":
        for eq in session.questions:
            q = eq.question
            answer = request.POST.get(f"question_{q.id}")

            if answer is not None:
                CandidateAnswer.objects.update_or_create(
                    candidate=user,
                    paper=paper,
                    question=q,
                    defaults={
                        "answer": answer,
                        "submitted_at": timezone.now(),
                    },
                )

        session.finish()
        messages.success(request, "Exam submitted successfully.")
        return redirect("logout")

    # ------------------------------------------------
    # Render exam
    # ------------------------------------------------
    context = {
        "paper": paper,
        "session": session,
        "questions": session.questions,
        "duration_seconds": duration_seconds,
    }

    return render(request, "registration/exam_interface.html", context)
