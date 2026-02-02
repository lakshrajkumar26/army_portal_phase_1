# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from exams.models import Shift
from django.core.validators import RegexValidator
from questions.models import TradePaperActivation
from django.core.exceptions import ValidationError

class CandidateProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile"
    )
    
    # Personal details
    army_no = models.CharField(max_length=50, unique=True)
    rank = models.CharField(max_length=50)
    unit = models.CharField(max_length=50, blank=True, null=True)
    brigade = models.CharField(max_length=100, blank=True, null=True)
    corps = models.CharField(max_length=100, blank=True, null=True)
    command = models.CharField(max_length=100, blank=True, null=True)
    trade = models.ForeignKey('reference.Trade', on_delete=models.SET_NULL, null=True, blank=True)
    
    name = models.CharField(max_length=150)
    dob = models.CharField(max_length=10, verbose_name="Date of Birth")
    doe = models.DateField(verbose_name="Date of Enrolment")
    aadhar_number = models.CharField(
        max_length=12,
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message="Aadhaar number must be exactly 12 digits."
            )
        ]
    )

    mobile_no = models.CharField(
        max_length=10,
        verbose_name="Mobile No (Linked to Aadhaar Card)",
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Enter a valid 10-digit mobile number."
            )
        ],
        null=True,
        blank=True
    )
    apaar_id = models.CharField(
        max_length=12,
        verbose_name="APAAR ID (12 digits)",
        validators=[
            RegexValidator(
                regex=r'^\d{12}$',
                message="APAAR ID must be exactly 12 digits."
            )
        ]
    )



    father_name = models.CharField(max_length=150)
    photograph = models.ImageField(upload_to="photos/", blank=True, null=True)
    
    # Exam details
    # qualification = models.CharField(max_length=150)
    nsqf_level = models.CharField(max_length=50, blank=True)
    exam_center = models.CharField(max_length=150, blank=True, null=True)
    
    training_center = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)

    primary_qualification = models.CharField(max_length=150, blank=True, null=True)
    primary_duration = models.CharField(max_length=50, blank=True, null=True)
    primary_credits = models.CharField(max_length=50, blank=True, null=True)

    secondary_qualification = models.CharField(max_length=150, blank=True, null=True)
    secondary_duration = models.CharField(max_length=50, blank=True, null=True)
    secondary_credits = models.CharField(max_length=50, blank=True, null=True)
    # Exam slot consumption (SEPARATE)
    primary_slot_consumed_at = models.DateTimeField(null=True, blank=True)
    secondary_slot_consumed_at = models.DateTimeField(null=True, blank=True)

    # duration = models.CharField(max_length=50, blank=True)
    # credits = models.CharField(max_length=50, blank=True)
    
    # Admin-side fields
    primary_viva_marks = models.IntegerField(null=True, blank=True)
    primary_practical_marks = models.IntegerField(null=True, blank=True)
    secondary_viva_marks = models.IntegerField(null=True, blank=True)
    secondary_practical_marks = models.IntegerField(null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, null=True, blank=True)
    
    # Exam slot management
    has_exam_slot = models.BooleanField(default=False, verbose_name="Has Exam Slot")
    slot_assigned_at = models.DateTimeField(null=True, blank=True, verbose_name="Slot Assigned At")
    slot_attempting_at = models.DateTimeField(null=True, blank=True, verbose_name="Exam Attempt Started At")
    slot_assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="assigned_slots",
        verbose_name="Slot Assigned By"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_primary_completed = models.BooleanField(default=False)
    is_secondary_completed = models.BooleanField(default=False)
    primary_bypass_allowed = models.BooleanField(
    default=False,
    help_text="Allow candidate to give SECONDARY without completing PRIMARY (legacy / failed earlier)"
)
    # Marks validation rules
    TRADE_MARKS = {
        "TTC": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "OCC": {"primary": {"prac": 20, "viva": 5}, "secondary": {"prac": 30, "viva": 10}},  
        "DTMN": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "EFS": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "DMV": {"primary": {"prac": 20, "viva": 5}, "secondary": {"prac": 30, "viva": 10}},
        "LMN": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "CLK SD": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "STEWARD": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "WASHERMAN": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "HOUSE KEEPER": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "CHEFCOM": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "MESS KEEPER": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "SKT": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "MUSICIAN": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "ARTSN WW": {"primary": {"prac": 30, "viva": 10}, "secondary": {"prac": 30, "viva": 10}},
        "HAIR DRESSER": {"secondary": {"prac": 30, "viva": 10}},  
        "SP STAFF": {"secondary": {"prac": 30, "viva": 10}},      
    }
    # Trades that do NOT have a PRIMARY exam
    TRADES_WITHOUT_PRIMARY = {
        "HAIR DRESSER",
        "MUSICIAN",
    }

    
    def _normalized_trade(self):
        """Normalize trade name for consistent comparison"""
        if not self.trade:
            return ""
        
        # Use the Trade name (or code if you prefer)
        trade = self.trade.name.strip().upper()
        
        # Handle variations
        if "WASHERMAN" in trade:
            return "WASHERMAN"
        elif "HOUSE KEEPER" in trade:
            return "HOUSE KEEPER"
        elif "MUSICIAN" in trade:
            return "MUSICIAN"
        elif "HAIR DRESSER" in trade:
            return "HAIR DRESSER"
        elif "SP STAFF" in trade:
            return "SP STAFF"
        elif "MESS KEEPER" in trade:
            return "MESS KEEPER"
        else:
            # For exact matches like TTC, OCC, DMV, etc.
            return trade

    def has_primary_exam(self):
        """
        Returns False for trades that do not have a PRIMARY exam.
        """
        normalized_trade = self._normalized_trade()
        return normalized_trade not in self.TRADES_WITHOUT_PRIMARY
    def can_skip_primary(self):
        """
        Returns True if candidate is allowed to bypass PRIMARY exam
        (legacy / failed earlier candidates).
        """
        return self.primary_bypass_allowed
    def get_next_exam_type(self):
        """
        Decide which exam should be taken next,
        respecting PRIMARY bypass.
        """
        if self.has_primary_exam():
            if self.is_primary_completed:
                return "SECONDARY"

            if self.can_skip_primary():
                return "SECONDARY"

            return "PRIMARY"

        return "SECONDARY"


    def get_marks_limits(self):
        """Get practical and viva marks limits for this trade"""
        normalized_trade = self._normalized_trade()
        
        if not normalized_trade:
            return None, None, None, None  # No trade specified
            
        trade_rules = self.TRADE_MARKS.get(normalized_trade)
        if not trade_rules:
            # Default limits for unknown trades
            return 30, 10, 30, 10
        
        # Primary limits
        primary_prac = trade_rules.get("primary", {}).get("prac")
        primary_viva = trade_rules.get("primary", {}).get("viva")
        
        # Secondary limits  
        secondary_prac = trade_rules.get("secondary", {}).get("prac")
        secondary_viva = trade_rules.get("secondary", {}).get("viva")
        
        return primary_prac, primary_viva, secondary_prac, secondary_viva
    
    def clean(self):
        super().clean()
        
        # Get limits for this trade
        primary_prac_max, primary_viva_max, secondary_prac_max, secondary_viva_max = self.get_marks_limits()
        
        # Validate primary practical marks
        if (primary_prac_max is not None and 
            self.primary_practical_marks is not None and 
            self.primary_practical_marks > primary_prac_max):
            raise ValidationError({
                "primary_practical_marks": f"Primary practical marks cannot exceed {primary_prac_max} for {self.trade} trade."
            })
        
        # Validate primary viva marks
        if (primary_viva_max is not None and 
            self.primary_viva_marks is not None and 
            self.primary_viva_marks > primary_viva_max):
            raise ValidationError({
                "primary_viva_marks": f"Primary viva marks cannot exceed {primary_viva_max} for {self.trade} trade."
            })
        
        # Validate secondary practical marks
        if (secondary_prac_max is not None and 
            self.secondary_practical_marks is not None and 
            self.secondary_practical_marks > secondary_prac_max):
            raise ValidationError({
                "secondary_practical_marks": f"Secondary practical marks cannot exceed {secondary_prac_max} for {self.trade} trade."
            })
        
        # Validate secondary viva marks
        if (secondary_viva_max is not None and 
            self.secondary_viva_marks is not None and 
            self.secondary_viva_marks > secondary_viva_max):
            raise ValidationError({
                "secondary_viva_marks": f"Secondary viva marks cannot exceed {secondary_viva_max} for {self.trade} trade."
            })
        
        # Validate marks are not negative
        if self.primary_practical_marks is not None and self.primary_practical_marks < 0:
            raise ValidationError({"primary_practical_marks": "Marks cannot be negative."})
        
        if self.primary_viva_marks is not None and self.primary_viva_marks < 0:
            raise ValidationError({"primary_viva_marks": "Marks cannot be negative."})
            
        if self.secondary_practical_marks is not None and self.secondary_practical_marks < 0:
            raise ValidationError({"secondary_practical_marks": "Marks cannot be negative."})
        
        if self.secondary_viva_marks is not None and self.secondary_viva_marks < 0:
            raise ValidationError({"secondary_viva_marks": "Marks cannot be negative."})
        # PRIMARY completion
        # PRIMARY completion (do not unset if already completed via exam)
        if self.primary_practical_marks is not None and self.primary_viva_marks is not None:
            self.is_primary_completed = True


        # SECONDARY completion
        if self.secondary_practical_marks is not None and self.secondary_viva_marks is not None:
            self.is_secondary_completed = True
        else:
            self.is_secondary_completed = False

    
    @property
    def can_start_exam(self):
        if not self.has_exam_slot:
            return False

        if not self.trade:
            return False

        exam_type = self.get_next_exam_type()


        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            paper_type=exam_type,
            is_active=True
        ).first()


        if not activation:
            return False

        # ❌ Prevent reattempts
        if activation.paper_type == "PRIMARY" and self.is_primary_completed:
            return False

        if activation.paper_type == "SECONDARY" and self.is_secondary_completed:
            return False

        # ❌ Block SECONDARY without PRIMARY
        if (
            activation.paper_type == "SECONDARY"
            and self.has_primary_exam()
            and not self.is_primary_completed
            and not self.can_skip_primary()
        ):
            return False

        return True

    
    def start_exam_attempt(self):
        # ❌ Prevent any attempt if already submitted
        exam_type = self.get_next_exam_type()


        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            paper_type=exam_type,
            is_active=True
        ).first()


        if activation:
            if activation.paper_type == "PRIMARY" and self.is_primary_completed:
                raise ValidationError("Primary exam already completed.")
            if activation.paper_type == "SECONDARY" and self.is_secondary_completed:
                raise ValidationError("Secondary exam already completed.")

    

        exam_type = self.get_next_exam_type()


        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            paper_type=exam_type,
            is_active=True
        ).first()


        if activation and activation.paper_type == "SECONDARY":
            if (
                self.has_primary_exam()
                and not self.is_primary_completed
                and not self.can_skip_primary()
            ):
                raise ValidationError(
                    "Primary exam not completed. Cannot start secondary exam."
                )



        if self.has_exam_slot and self.slot_attempting_at is None:
            self.slot_attempting_at = timezone.now()
            self.save(update_fields=['slot_attempting_at'])
            return True
        return False

    
    def consume_exam_slot(self):
        if not self.has_exam_slot:
            return False

        exam_type = self.get_next_exam_type()


        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            paper_type=exam_type,
            is_active=True
        ).first()


        if not activation:
            return False

        now = timezone.now()

        if activation.paper_type == "PRIMARY":
            self.is_primary_completed = True
            self.primary_slot_consumed_at = now

        elif activation.paper_type == "SECONDARY":
            self.is_secondary_completed = True
            self.secondary_slot_consumed_at = now

        self.has_exam_slot = False
        self.slot_attempting_at = None
        self.save()
        return True



        
    def assign_exam_slot(self, assigned_by_user=None):
        if self.has_exam_slot:
            raise ValidationError("Candidate already has an active exam slot.")

        exam_type = self.get_next_exam_type()


        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            paper_type=exam_type,
            is_active=True
        ).first()


        if not activation:
            raise ValidationError("No active exam available for this trade.")

        # ❌ Block PRIMARY reattempt
        if activation.paper_type == "PRIMARY" and self.is_primary_completed:
            raise ValidationError("Primary exam already completed.")

        # ❌ Block SECONDARY reattempt
        if activation.paper_type == "SECONDARY" and self.is_secondary_completed:
            raise ValidationError("Secondary exam already completed.")

        # ❌ Block SECONDARY if PRIMARY not completed
        if (
            activation.paper_type == "SECONDARY"
            and self.has_primary_exam()
            and not self.is_primary_completed
            and not self.can_skip_primary()
        ):
            raise ValidationError(
                "Primary exam not completed. Cannot assign secondary slot."
            )

        # ✅ ASSIGN SLOT (no slot_consumed_at logic here)
        self.has_exam_slot = True
        self.slot_assigned_at = timezone.now()
        self.slot_attempting_at = None
        self.slot_assigned_by = assigned_by_user
        self.save()

        return True

    
    def reset_exam_slot(self):
        exam_type = self.get_next_exam_type()


        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            paper_type=exam_type,
            is_active=True
        ).first()


        if activation:
            if activation.paper_type == "PRIMARY" and self.primary_slot_consumed_at:
                raise ValidationError("Primary exam already submitted. Reset not allowed.")

            if activation.paper_type == "SECONDARY" and self.secondary_slot_consumed_at:
                raise ValidationError("Secondary exam already submitted. Reset not allowed.")

        from questions.models import ExamSession
        ExamSession.objects.filter(
            user=self.user,
            completed_at__isnull=True
        ).delete()

        self.has_exam_slot = False
        self.slot_assigned_at = None
        self.slot_attempting_at = None
        self.slot_assigned_by = None
        self.save()
        return True
    
    @property
    def slot_status(self):
        if self.primary_slot_consumed_at:
            return f"Primary submitted on {self.primary_slot_consumed_at:%Y-%m-%d %H:%M}"

        if self.secondary_slot_consumed_at:
            return f"Secondary submitted on {self.secondary_slot_consumed_at:%Y-%m-%d %H:%M}"

        if not self.has_exam_slot:
            return "No Slot"

        if self.slot_attempting_at:
            return f"Attempting since {self.slot_attempting_at:%Y-%m-%d %H:%M}"

        if self.slot_assigned_at:
            return f"Available (assigned {self.slot_assigned_at:%Y-%m-%d %H:%M})"

        return "Available"


    def __str__(self):
        return f"{self.army_no} - {self.name}"