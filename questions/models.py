# questions/models.py
from django.db import models, transaction
from django.core.exceptions import ValidationError
from reference.models import Trade
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.utils import timezone
import re

User = get_user_model()


def validate_dat_file(value):
    """Validate that only .dat files are uploaded"""
    if not value.name.lower().endswith(".dat"):
        raise ValidationError("Only .dat files are allowed.")


# ---------------------------
# Hard-coded trade & distribution config
# ---------------------------
HARD_CODED_TRADE_CONFIG = {
    "TTC": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "OCC": {"total_questions": 54, "part_distribution": {"A": 20, "B": 0, "C": 5, "D": 15, "E": 4, "F": 10}},
    "DTMN": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "EFS": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "DMV": {"total_questions": 54, "part_distribution": {"A": 20, "B": 0, "C": 5, "D": 15, "E": 4, "F": 10}},
    "LMN": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "CLK SD": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "STEWARD": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "WASHERMAN": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "HOUSE KEEPER": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "CHEFCOM": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "MESS KEEPER": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "SKT": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "MUSICIAN": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "ARTSN WW": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "HAIR DRESSER": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
    "SP STAFF": {"total_questions": 43, "part_distribution": {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}},
}

HARD_CODED_COMMON_DISTRIBUTION = {"A": 15, "B": 0, "C": 5, "D": 10, "E": 3, "F": 10}


def _normalize_trade_name(name: str) -> str:
    if not name:
        return ""
    return re.sub(r"\s+", " ", name.strip()).upper()


# ------------------------------
# MODELS
# ------------------------------
class Question(models.Model):
    class Part(models.TextChoices):
        A = "A", "Part A - MCQ (Single Choice)"
        B = "B", "Part B - MCQ (Multiple Choice)"
        C = "C", "Part C - Short answer (20-30 words)"
        D = "D", "Part D - Fill in the blanks"
        E = "E", "Part E - Long answer (100-120 words)"
        F = "F", "Part F - True/False"

    class PaperType(models.TextChoices):
        PRIMARY = "PRIMARY", "Primary"
        SECONDARY = "SECONDARY", "Secondary"

    text = models.TextField()
    part = models.CharField(max_length=1, choices=Part.choices, default="A")
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.JSONField(blank=True, null=True)

    trade = models.ForeignKey(Trade, on_delete=models.SET_NULL, null=True, blank=True)

    # ✅ REQUIRED so exam can filter by Primary/Secondary correctly
    paper_type = models.CharField(max_length=20, choices=PaperType.choices, default="PRIMARY")

    # ✅ SECONDARY/common marker
    is_common = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "QP Delete"
        verbose_name_plural = "3 QP Delete"

    def __str__(self):
        return f"[{self.get_part_display()}] {self.text[:60]}..."


class QuestionUpload(models.Model):
    file = models.FileField(upload_to="uploads/questions/", validators=[validate_dat_file])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    decryption_password = models.CharField(max_length=255, default="default123")

    class Meta:
        verbose_name = "QP Upload"
        verbose_name_plural = "1 QP Upload"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.file.name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"


class QuestionPaper(models.Model):
    PAPER_TYPE_CHOICES = [
        ("PRIMARY", "Primary"),
        ("SECONDARY", "Secondary"),
    ]

    question_paper = models.CharField(max_length=20, choices=PAPER_TYPE_CHOICES, unique=True)
    is_active = models.BooleanField(default=False)
    exam_duration = models.DurationField(default=timedelta(hours=3))

    class Meta:
        verbose_name = "QP Mapping"
        verbose_name_plural = "2 QP Mappings"
        ordering = ["-id"]

    def __str__(self):
        return self.question_paper

    def _get_hardcoded_for_trade(self, trade_obj):
        if not trade_obj:
            return None

        possible = []
        for fld in ("name", "code", "slug"):
            val = getattr(trade_obj, fld, None)
            if val:
                possible.append(_normalize_trade_name(str(val)))

        seen = set()
        possible = [x for x in possible if not (x in seen or seen.add(x))]

        for key in possible:
            cfg = HARD_CODED_TRADE_CONFIG.get(key)
            if cfg:
                return cfg["part_distribution"].copy(), int(cfg["total_questions"])
            cfg = HARD_CODED_TRADE_CONFIG.get(key.replace(" ", ""))
            if cfg:
                return cfg["part_distribution"].copy(), int(cfg["total_questions"])
        return None

    def generate_for_candidate(self, user, trade=None, shuffle_within_parts=True):
        """
        ✅ SAFE selection:
        - PRIMARY => paper_type=PRIMARY AND trade matches
        - SECONDARY => paper_type=SECONDARY AND is_common=True
        - HARD FAIL if cannot build required questions
        """
        import random

        is_secondary = (self.question_paper == "SECONDARY")

        if is_secondary:
            dist = HARD_CODED_COMMON_DISTRIBUTION.copy()
        else:
            cfg = self._get_hardcoded_for_trade(trade)
            dist = cfg[0] if cfg else HARD_CODED_COMMON_DISTRIBUTION.copy()

        with transaction.atomic():
            session = ExamSession.objects.create(
                paper=self,
                user=user,
                trade=None if is_secondary else trade,
                started_at=timezone.now(),
                duration=self.exam_duration,
            )

            order = 1
            total_selected = 0

            for part, count in dist.items():
                count = int(count)
                if count <= 0:
                    continue

                qs = Question.objects.filter(is_active=True, part=part)

                if is_secondary:
                    qs = qs.filter(paper_type="SECONDARY", is_common=True)
                else:
                    qs = qs.filter(paper_type="PRIMARY", trade=trade)

                selected = list(qs.order_by("?")[:count])

                if len(selected) < count:
                    raise ValidationError(
                        f"Not enough questions for {trade} {self.question_paper} part {part}. "
                        f"Required {count}, found {len(selected)}."
                    )

                if shuffle_within_parts:
                    random.shuffle(selected)

                for q in selected:
                    ExamQuestion.objects.create(session=session, question=q, order=order)
                    order += 1
                    total_selected += 1

            if total_selected == 0:
                raise ValidationError("No questions selected. Check trade tagging and paper_type.")

            session.total_questions = total_selected
            session.save(update_fields=["total_questions"])
            return session


# ✅ THIS MODEL WAS MISSING — REQUIRED FOR ADMIN IMPORTS
class TradePaperActivation(models.Model):
    PAPER_TYPE_CHOICES = [
        ("PRIMARY", "Primary"),
        ("SECONDARY", "Secondary"),
    ]

    trade = models.ForeignKey(Trade, on_delete=models.CASCADE)
    paper_type = models.CharField(max_length=20, choices=PAPER_TYPE_CHOICES)
    is_active = models.BooleanField(default=False)
    exam_duration = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ("trade", "paper_type")
        ordering = ["trade__name", "paper_type"]
        verbose_name = "Trade Paper Activation"
        verbose_name_plural = "Trade Paper Activations"

    def __str__(self):
        return f"{self.trade} - {self.paper_type} ({'ACTIVE' if self.is_active else 'INACTIVE'})"


class ExamSession(models.Model):
    paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trade = models.ForeignKey(Trade, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"ExamSession: {self.user} - {self.paper} ({self.started_at})"

    @property
    def questions(self):
        return self.examquestion_set.select_related("question").order_by("order")

    def finish(self):
        self.completed_at = timezone.now()
        self.save(update_fields=["completed_at"])


class ExamQuestion(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("session", "question")

    def __str__(self):
        return f"{self.session} - Q{self.order} ({self.question.pk})"
