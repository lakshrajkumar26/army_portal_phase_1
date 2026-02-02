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
        ✅ FIXED: Question Set Assignment with Persistence
        - Uses ActivateSets model for reliable question set assignment
        - PRIMARY => paper_type=PRIMARY AND trade matches AND active question_set
        - SECONDARY => paper_type=SECONDARY AND is_common=True AND active question_set
        - Question set assignment persists through slot changes and resets
        - HARD FAIL if cannot build required questions
        """
        import random

        # Determine paper type based on global activation (not individual trade)
        try:
            # Check what paper type is globally active
            global_control = GlobalPaperTypeControl.objects.get(is_active=True)
            paper_type = global_control.paper_type
            is_secondary = (paper_type == "SECONDARY")
        except GlobalPaperTypeControl.DoesNotExist:
            # Fallback: use the paper type from this QuestionPaper instance
            is_secondary = (self.question_paper == "SECONDARY")
            paper_type = self.question_paper

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
                exam_type=paper_type, 
                started_at=timezone.now(),
                duration=self.exam_duration,
            )

            order = 1
            total_selected = 0

            # ✅ CRITICAL FIX: Get active question set from ActivateSets model
            # This ensures the selected question set persists through slot changes
            active_question_set = 'A'  # Default fallback
            if trade:
                try:
                    # Use ActivateSets model for reliable question set retrieval
                    activate_sets = ActivateSets.objects.get(trade=trade)
                    if is_secondary:
                        active_question_set = activate_sets.active_secondary_set
                    else:
                        active_question_set = activate_sets.active_primary_set
                except ActivateSets.DoesNotExist:
                    # Create default ActivateSets record if it doesn't exist
                    activate_sets = ActivateSets.objects.create(
                        trade=trade,
                        active_primary_set='A',
                        active_secondary_set='A'
                    )
                    active_question_set = 'A'

            # Log the question set being used for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Generating exam for {user.username}, Trade: {trade}, Paper: {paper_type}, Question Set: {active_question_set}")

            for part, count in dist.items():
                count = int(count)
                if count <= 0:
                    continue

                qs = Question.objects.filter(is_active=True, part=part)

                if is_secondary:
                    # For SECONDARY questions, filter by trade code in question text
                    # to ensure only trade-specific questions are selected
                    qs = qs.filter(
                        paper_type="SECONDARY", 
                        is_common=True,
                        question_set=active_question_set,
                        
                    )
                else:
                    # ✅ CRITICAL: Filter by trade, paper type, AND active question set
                    qs = qs.filter(
                        paper_type="PRIMARY", 
                        trade=trade,
                        question_set=active_question_set
                    )

                selected = list(qs.order_by("?")[:count])

                # if len(selected) < count:
                #     # Enhanced error message with debugging info
                #     available_sets = Question.objects.filter(
                #         is_active=True, 
                #         part=part,
                #         paper_type=paper_type,
                #         trade=trade if not is_secondary else None
                #     ).values_list('question_set', flat=True).distinct()
                    
                #     raise ValidationError(
                #         f"❌ CRITICAL: Not enough questions for {trade} {paper_type} part {part} "
                #         f"from question set {active_question_set}. "
                #         f"Required {count}, found {len(selected)}. "
                #         f"Available sets for this trade: {list(available_sets)}. "
                #         f"Check question set activation in admin."
                #     )

                if shuffle_within_parts:
                    random.shuffle(selected)

                for q in selected:
                    ExamQuestion.objects.create(session=session, question=q, order=order)
                    order += 1
                    total_selected += 1

            if total_selected == 0:
                raise ValidationError(
                    f"❌ CRITICAL: No questions selected for {trade} {paper_type} "
                    f"with question set {active_question_set}. "
                    f"Check trade tagging, paper_type, and question set activation."
                )

            session.total_questions = total_selected
            session.save(update_fields=["total_questions"])
            
            # Log successful generation
            logger.info(f"✅ Successfully generated {total_selected} questions for {user.username} from question set {active_question_set}")
            
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
    exam_type = models.CharField(
        max_length=20,
        choices=[("PRIMARY", "Primary"), ("SECONDARY", "Secondary")]
    )
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


class UniversalSetActivation(models.Model):
    """
    Model for universal question set and duration management.
    Provides both universal activation (same set for all trades) and universal duration options.
    """
    paper_type = models.CharField(
        max_length=20,
        choices=[('PRIMARY', 'Primary'), ('SECONDARY', 'Secondary')],
        unique=True
    )
    universal_set_label = models.CharField(
        max_length=1,
        choices=[(chr(i), chr(i)) for i in range(ord('A'), ord('Z')+1)],
        null=True,
        blank=True,
        help_text="Universal question set for all trades (leave blank for individual trade selection)"
    )
    universal_duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Universal exam duration in minutes for all trades (leave blank for individual trade durations)"
    )
    is_universal_set_active = models.BooleanField(
        default=False,
        help_text="Enable universal set activation (same set for all trades)"
    )
    is_universal_duration_active = models.BooleanField(
        default=False,
        help_text="Enable universal duration (same duration for all trades)"
    )
    activated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    activated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Universal Set Activation"
        verbose_name_plural = "Universal Set Activations"
    
    def __str__(self):
        universal_info = []
        if self.is_universal_set_active and self.universal_set_label:
            universal_info.append(f"Set {self.universal_set_label}")
        if self.is_universal_duration_active and self.universal_duration_minutes:
            universal_info.append(f"{self.universal_duration_minutes}min")
        
        if universal_info:
            return f"{self.paper_type} - Universal: {', '.join(universal_info)}"
        else:
            return f"{self.paper_type} - Individual Settings"
    
    def save(self, *args, **kwargs):
        """
        Override save to apply universal settings to all trades when activated
        """
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            if self.is_universal_set_active and self.universal_set_label:
                # Apply universal set to all trades
                from reference.models import Trade
                
                for trade in Trade.objects.all():
                    # Update ActivateSets record
                    activate_sets, created = ActivateSets.objects.get_or_create(
                        trade=trade,
                        defaults={'updated_by': self.activated_by}
                    )
                    
                    if self.paper_type == 'PRIMARY':
                        activate_sets.active_primary_set = self.universal_set_label
                    else:
                        activate_sets.active_secondary_set = self.universal_set_label
                    
                    activate_sets.updated_by = self.activated_by
                    activate_sets.save()  # This will sync with QuestionSetActivation
            
            if self.is_universal_duration_active and self.universal_duration_minutes:
                # Apply universal duration to all trades
                from reference.models import Trade
                from datetime import timedelta
                
                duration = timedelta(minutes=self.universal_duration_minutes)
                
                for trade in Trade.objects.all():
                    TradePaperActivation.objects.update_or_create(
                        trade=trade,
                        paper_type=self.paper_type,
                        defaults={
                            'is_active': True,
                            'exam_duration': duration,
                        }
                    )


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
        CRITICAL FIX: Clear incomplete exam sessions when question sets change
        """
        # Check if question sets are changing
        sets_changed = False
        if self.pk:  # Existing record
            try:
                old_instance = ActivateSets.objects.get(pk=self.pk)
                if (old_instance.active_primary_set != self.active_primary_set or 
                    old_instance.active_secondary_set != self.active_secondary_set):
                    sets_changed = True
            except ActivateSets.DoesNotExist:
                pass
        
        with transaction.atomic():
            # Save the ActivateSets record first
            super().save(*args, **kwargs)
            
            # If question sets changed, clear incomplete sessions for this trade
            if sets_changed:
                from registration.models import CandidateProfile
                candidates = CandidateProfile.objects.filter(trade=self.trade)
                total_cleared = 0
                
                for candidate in candidates:
                    # Import here to avoid circular imports
                    incomplete_sessions = ExamSession.objects.filter(
                        user=candidate.user,
                        completed_at__isnull=True
                    )
                    cleared_count = incomplete_sessions.count()
                    if cleared_count > 0:
                        incomplete_sessions.delete()
                        total_cleared += cleared_count
                
                if total_cleared > 0:
                    print(f"✅ Cleared {total_cleared} incomplete sessions for {self.trade.name} due to question set change")
            
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
            # For SECONDARY questions, check if this trade actually has SECONDARY data
            # by looking for questions that mention the trade code in their text
            
            queryset = Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                is_active=True,
                
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
            # For SECONDARY questions, check if this trade actually has SECONDARY data
            # by looking for questions that mention the trade code in their text
            trade_code = self.trade.code.upper()
            secondary_count = Question.objects.filter(
                paper_type='SECONDARY',
                is_common=True,
                question_set=question_set,
                is_active=True,
                
            ).count()
            return secondary_count
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
