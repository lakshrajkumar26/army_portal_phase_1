
from django.db import models
from django.conf import settings
from centers.models import Center
from reference.models import Trade
from questions.models import QuestionPaper
from django.utils import timezone
from questions.models import Question


class ExamDayAvailability(models.Model):
    """
    Which trades' papers are available on a given date (6 or 7 per day).
    """
    date = models.DateField()
    trades = models.ManyToManyField(Trade, related_name="available_on")

    class Meta:
        verbose_name = "Exam day availability"
        verbose_name_plural = "Exam day availabilities"
        unique_together = ("date",)

    def _str_(self):
        return f"{self.date} ({self.trades.count()} trades)"


class Shift(models.Model):
    """
    A batch/shift of up to ~40 candidates at a center.
    """
    exam_center = models.ForeignKey(Center, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    # capacity = models.PositiveSmallIntegerField(default=40)

    class Meta:
        verbose_name = "Exam slot"
        verbose_name_plural = "Exam slots"
        unique_together = ("exam_center", "date", "start_time")

    def __str__(self):
        return f"{self.exam_center.comd} {self.date} {self.start_time}"


class ExamAssignment(models.Model):
    """
    Assign the two papers (Primary-I & Common) to a candidate in a shift.
    """
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_assignments"
    )
    center = models.ForeignKey(Center, on_delete=models.PROTECT)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT)
    primary_paper = models.ForeignKey(
        QuestionPaper,
        on_delete=models.PROTECT,
        related_name="primary_assignments"
    )
    common_paper = models.ForeignKey(
        QuestionPaper,
        on_delete=models.PROTECT,
        related_name="common_assignments"
    )

    scheduled_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        default="SCHEDULED"
    )  # SCHEDULED/STARTED/SUBMITTED/EVALUATED/VETTED

    class Meta:
        verbose_name = "Exam assignment"
        verbose_name_plural = "Exam assignments"
        unique_together = ("candidate", "shift")

    def _str_(self):
        return f"Assignment of {self.candidate} in {self.shift}"


class ExamAttempt(models.Model):
    assignment = models.OneToOneField(
        ExamAssignment,
        on_delete=models.CASCADE,
        related_name="attempt"
    )
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    objective_score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    practical_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    viva_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def mark_started(self):
        if not self.started_at:
            self.started_at = timezone.now()
            self.save(update_fields=["started_at"])

    class Meta:
        verbose_name = "Exam attempt"
        verbose_name_plural = "Exam attempts"

    def _str_(self):
        return f"Attempt of {self.assignment.candidate} on {self.assignment.shift}"


class Answer(models.Model):
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    # Given answer stored textually/JSON; for MCQ store selected option; for T/F store true/false; for subjective store text.
    given = models.JSONField(null=True, blank=True)
    text_answer = models.TextField(blank=True)  # for D/E
    auto_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # objective auto-eval
    evaluator_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # subjective
    final_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        unique_together = ("attempt", "question")

    def _str_(self):
        return f"Answer to {self.question} by {self.attempt.assignment.candidate}"
