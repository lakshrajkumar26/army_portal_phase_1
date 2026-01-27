# results/models.py
from django.db import models
from django.conf import settings

# Import lazily to avoid circular imports at import time
# We'll refer to app models by string in FKs if needed
# CandidateProfile is in registration app; QuestionPaper & Question in questions app

class CandidateAnswer(models.Model):
    candidate = models.ForeignKey(
        "registration.CandidateProfile",
        on_delete=models.CASCADE,
        related_name="answers",
    )
    # Make paper nullable and set to NULL when the QuestionPaper is deleted.
    paper = models.ForeignKey(
        "questions.QuestionPaper",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidate_answers",
    )
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.PROTECT,   # keep questions safe; answers remain referencing question
        related_name="candidate_answers",
    )
    answer = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # guard against paper being NULL
        paper_label = getattr(self.paper, "question_paper", "deleted-paper")
        army_no = getattr(self.candidate, "army_no", str(self.candidate)) if self.candidate else "unknown"
        return f"{army_no} - {paper_label} - {self.question_id}"

    @property
    def effective_category(self) -> str:
        """
        Computed label for downstream exports:
        - 'secondary' if the paper was common
        - 'primary' if the paper was trade-specific
        If paper is NULL, try to infer from question/paper history; fallback to 'unknown'
        """
        if self.paper is None:
            return "unknown"
        is_common = getattr(self.paper, "is_common", False)
        return "secondary" if is_common else "primary"
