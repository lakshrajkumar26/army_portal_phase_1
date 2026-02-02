# results/models.py
from django.db import models
from django.conf import settings

# Import lazily to avoid circular imports at import time
# We'll refer to app models by string in FKs if needed
# CandidateProfile is in registration app; QuestionPaper & Question in questions app

class CandidateAnswer(models.Model):
    EXAM_TYPES = (
        ("PRIMARY", "Primary"),
        ("SECONDARY", "Secondary"),
    )

    candidate = models.ForeignKey(
        "registration.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="answers",
    )

    paper = models.ForeignKey(
        "questions.QuestionPaper",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidate_answers",
    )

    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.PROTECT,
        related_name="candidate_answers",
    )

    answer = models.TextField(blank=True, null=True)

    # ✅ ADD THIS (MOST IMPORTANT)
    exam_type = models.CharField(
        max_length=10,
        choices=EXAM_TYPES,
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = (
            "candidate",
            "paper",
            "question",
            "exam_type",
        )
        indexes = [
            models.Index(fields=["candidate", "exam_type"]),
            models.Index(fields=["paper", "exam_type"]),
        ]
    def __str__(self):
        paper_label = getattr(self.paper, "question_paper", "deleted-paper")
        army_no = getattr(self.candidate, "army_no", str(self.candidate)) if self.candidate else "unknown"
        return f"{army_no} - {self.exam_type} - {self.question_id}"


