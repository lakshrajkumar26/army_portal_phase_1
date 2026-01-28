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
    options = models.JSONField(blank=True, null=True)  # Will be deprecated
    correct_answer = models.JSONField(blank=True, null=True)

    trade = models.ForeignKey(Trade, on_delete=models.SET_NULL, null=True, blank=True)

    # ✅ REQUIRED so exam can filter by Primary/Secondary correctly
    paper_type = models.CharField(max_length=20, choices=PaperType.choices, default="PRIMARY")

    # ✅ SECONDARY/common marker
    is_common = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields for enhanced functionality
    question_set = models.CharField(
        max_length=1, 
        choices=[(chr(i), chr(i)) for i in range(ord('A'), ord('Z')+1)],
        default='A',
        help_text="Question set identifier (A-Z)"
    )
    
    # New separate option fields (will replace options JSONField)
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True) 
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "QP Delete"
        verbose_name_plural = "3 QP Delete"
        indexes = [
            models.Index(fields=['trade', 'paper_type', 'question_set', 'is_active']),
            models.Index(fields=['question_set', 'part']),
        ]

    def __str__(self):
        return f"[{self.get_part_display()}] {self.text[:60]}..."


class QuestionSetActivation(models.Model):
    """Model to track which question sets are active for each trade and paper type"""
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE)
    paper_type = models.CharField(
        max_length=20, 
        choices=[('PRIMARY', 'Primary'), ('SECONDARY', 'Secondary')]
    )
    question_set = models.CharField(
        max_length=1,
        choices=[(chr(i), chr(i)) for i in range(ord('A'), ord('Z')+1)]
    )
    is_active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(auto_now=True)
    activated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        unique_together = [('trade', 'paper_type', 'question_set')]
        indexes = [
            models.Index(fields=['trade', 'paper_type', 'is_active']),
        ]
        verbose_name = "Question Set Activation"
        verbose_name_plural = "Question Set Activations"
    
    def __str__(self):
        return f"{self.trade} - {self.paper_type} - Set {self.question_set} ({'ACTIVE' if self.is_active else 'INACTIVE'})"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate all other sets for this trade and paper type
            QuestionSetActivation.objects.filter(
                trade=self.trade,
                paper_type=self.paper_type,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class GlobalPaperTypeControl(models.Model):
    """Model to manage global PRIMARY/SECONDARY activation"""
    paper_type = models.CharField(
        max_length=20,
        choices=[('PRIMARY', 'Primary'), ('SECONDARY', 'Secondary')],
        unique=True
    )
    is_active = models.BooleanField(default=False)
    last_activated = models.DateTimeField(auto_now=True)
    activated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Global Paper Type Control"
        verbose_name_plural = "Global Paper Type Controls"
    
    def __str__(self):
        return f"{self.paper_type} ({'ACTIVE' if self.is_active else 'INACTIVE'})"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate the other paper type
            GlobalPaperTypeControl.objects.exclude(pk=self.pk).update(is_active=False)
            
            # Update all trade activations to match this paper type
            with transaction.atomic():
                # Deactivate all activations for the opposite paper type
                opposite_type = 'SECONDARY' if self.paper_type == 'PRIMARY' else 'PRIMARY'
                
                # Update QuestionSetActivation records (new system)
                QuestionSetActivation.objects.filter(
                    paper_type=opposite_type,
                    is_active=True
                ).update(is_active=False)
                
                # Update TradePaperActivation records (legacy system - needed for can_start_exam)
                TradePaperActivation.objects.filter(
                    paper_type=opposite_type,
                    is_active=True
                ).update(is_active=False)
                
                # Deactivate QuestionPaper records for opposite type
                QuestionPaper.objects.filter(
                    question_paper=opposite_type
                ).update(is_active=False)
                
                # Create/activate QuestionPaper record for this paper type
                question_paper, created = QuestionPaper.objects.get_or_create(
                    question_paper=self.paper_type,
                    defaults={'is_active': True}
                )
                if not created:
                    question_paper.is_active = True
                    question_paper.save()
                
                # Activate for all trades with this paper type
                for trade in Trade.objects.all():
                    # Create/update QuestionSetActivation (new system)
                    qs_activation, created = QuestionSetActivation.objects.get_or_create(
                        trade=trade,
                        paper_type=self.paper_type,
                        question_set='A',
                        defaults={'is_active': True, 'activated_by': self.activated_by}
                    )
                    if not created:
                        qs_activation.is_active = True
                        qs_activation.activated_by = self.activated_by
                        qs_activation.save()
                    
                    # Create/update TradePaperActivation (legacy system - needed for can_start_exam)
                    tp_activation, created = TradePaperActivation.objects.get_or_create(
                        trade=trade,
                        paper_type=self.paper_type,
                        defaults={'is_active': True}
                    )
                    if not created:
                        tp_activation.is_active = True
                        tp_activation.save()
        
        super().save(*args, **kwargs)


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
        ✅ SAFE selection with Question Set filtering:
        - PRIMARY => paper_type=PRIMARY AND trade matches AND active question_set
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

            # Get active question set for this trade and paper type
            active_question_set = 'A'  # Default fallback
            if not is_secondary and trade:
                try:
                    active_set = QuestionSetActivation.objects.get(
                        trade=trade,
                        paper_type=self.question_paper,
                        is_active=True
                    )
                    active_question_set = active_set.question_set
                except QuestionSetActivation.DoesNotExist:
                    # If no active set found, use Set A as default
                    active_question_set = 'A'

            for part, count in dist.items():
                count = int(count)
                if count <= 0:
                    continue

                qs = Question.objects.filter(is_active=True, part=part)

                if is_secondary:
                    qs = qs.filter(paper_type="SECONDARY", is_common=True)
                else:
                    # Filter by trade, paper type, AND active question set
                    qs = qs.filter(
                        paper_type="PRIMARY", 
                        trade=trade,
                        question_set=active_question_set
                    )

                selected = list(qs.order_by("?")[:count])

                if len(selected) < count:
                    raise ValidationError(
                        f"Not enough questions for {trade} {self.question_paper} part {part} "
                        f"from question set {active_question_set}. "
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


class ActivateSets(models.Model):
    """
    Unified model for simple question set management interface.
    Provides a single interface for managing question sets per trade.
    """
    trade = models.OneToOneField(Trade, on_delete=models.CASCADE, primary_key=True)
    active_primary_set = models.CharField(
        max_length=1,
        choices=[(chr(i), chr(i)) for i in range(ord('A'), ord('Z')+1)],
        default='A',
        help_text="Active question set for PRIMARY papers"
    )
    active_secondary_set = models.CharField(
        max_length=1,
        choices=[(chr(i), chr(i)) for i in range(ord('A'), ord('Z')+1)],
        default='A',
        help_text="Active question set for SECONDARY papers"
    )
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Activate Sets"
        verbose_name_plural = "Activate Sets"
        ordering = ['trade__name']
    
    def __str__(self):
        return f"{self.trade.name} - PRIMARY: Set {self.active_primary_set}, SECONDARY: Set {self.active_secondary_set}"
    
    def save(self, *args, **kwargs):
        """
        Override save to sync with QuestionSetActivation model
        """
        with transaction.atomic():
            # Save the ActivateSets record first
            super().save(*args, **kwargs)
            
            # Sync PRIMARY set activation
            if self.active_primary_set:
                # Deactivate all PRIMARY sets for this trade
                QuestionSetActivation.objects.filter(
                    trade=self.trade,
                    paper_type='PRIMARY'
                ).update(is_active=False)
                
                # Activate the selected PRIMARY set
                activation, created = QuestionSetActivation.objects.get_or_create(
                    trade=self.trade,
                    paper_type='PRIMARY',
                    question_set=self.active_primary_set,
                    defaults={'is_active': True, 'activated_by': self.updated_by}
                )
                if not created:
                    activation.is_active = True
                    activation.activated_by = self.updated_by
                    activation.save()
            
            # Sync SECONDARY set activation
            if self.active_secondary_set:
                # Deactivate all SECONDARY sets for this trade
                QuestionSetActivation.objects.filter(
                    trade=self.trade,
                    paper_type='SECONDARY'
                ).update(is_active=False)
                
                # Activate the selected SECONDARY set
                activation, created = QuestionSetActivation.objects.get_or_create(
                    trade=self.trade,
                    paper_type='SECONDARY',
                    question_set=self.active_secondary_set,
                    defaults={'is_active': True, 'activated_by': self.updated_by}
                )
                if not created:
                    activation.is_active = True
                    activation.activated_by = self.updated_by
                    activation.save()
    
    @classmethod
    def get_or_create_for_trade(cls, trade, user=None):
        """
        Get or create ActivateSets record for a trade, syncing with existing QuestionSetActivation data
        """
        try:
            return cls.objects.get(trade=trade)
        except cls.DoesNotExist:
            # Create new record based on existing QuestionSetActivation data
            primary_set = 'A'
            secondary_set = 'A'
            
            # Check for existing PRIMARY activation
            try:
                primary_activation = QuestionSetActivation.objects.get(
                    trade=trade,
                    paper_type='PRIMARY',
                    is_active=True
                )
                primary_set = primary_activation.question_set
            except QuestionSetActivation.DoesNotExist:
                pass
            
            # Check for existing SECONDARY activation
            try:
                secondary_activation = QuestionSetActivation.objects.get(
                    trade=trade,
                    paper_type='SECONDARY',
                    is_active=True
                )
                secondary_set = secondary_activation.question_set
            except QuestionSetActivation.DoesNotExist:
                pass
            
            return cls.objects.create(
                trade=trade,
                active_primary_set=primary_set,
                active_secondary_set=secondary_set,
                updated_by=user
            )
    
    def get_available_sets(self, paper_type):
        """
        Get available question sets with paper-type-specific filtering
        """
        if paper_type == 'SECONDARY':
            # Secondary questions: filter by paper_type and is_common only (no trade filter)
            queryset = Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                is_active=True
            )
        else:
            # Primary questions: filter by trade and paper_type
            queryset = Question.objects.filter(
                trade=self.trade,
                paper_type=paper_type,
                is_active=True
            )
        
        available_sets = queryset.values_list('question_set', flat=True).distinct().order_by('question_set')
        return list(available_sets)
    
    def get_question_count(self, paper_type, question_set):
        """
        Get question count with paper-type-specific filtering
        """
        if paper_type == 'SECONDARY':
            return Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                question_set=question_set,
                is_active=True
            ).count()
        else:
            return Question.objects.filter(
                trade=self.trade,
                paper_type=paper_type,
                question_set=question_set,
                is_active=True
            ).count()


class ExamQuestion(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("session", "question")

    def __str__(self):
        return f"{self.session} - Q{self.order} ({self.question.pk})"
