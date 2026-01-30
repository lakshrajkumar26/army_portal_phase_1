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
    aadhar_number = models.CharField(max_length=12, blank=True)
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
                message="Enter a valid 12-digit APAAR ID."
            )
        ],
        null=True,
        blank=True
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
    slot_consumed_at = models.DateTimeField(null=True, blank=True, verbose_name="Submitted At")
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
        # First check if candidate has an available exam slot
        if not self.has_exam_slot:
            return False
            
        # Check if slot is fully consumed (exam completed)
        if self.slot_consumed_at:
            if self.slot_assigned_at and self.slot_assigned_at > self.slot_consumed_at:
                # Fresh slot assigned after consumption - allow exam
                pass
            else:
                # Slot consumed and no fresh assignment
                return False
        
        # Allow access if slot is available or currently being attempted
        # (slot_attempting_at is set but slot_consumed_at is not)
            
        # Check if there's an active exam for this candidate's trade
        if not self.trade:
            return False
        # ✅ BLOCK SECONDARY EXAM IF PRIMARY NOT COMPLETED
        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            is_active=True
        ).first()

        if (
            activation
            and activation.paper_type == "SECONDARY"
            and self.has_primary_exam()
            and not self.is_primary_completed
        ):
            return False


        
        active_exam = TradePaperActivation.objects.filter(
            trade=self.trade,
            is_active=True
        ).exists()
        
        return active_exam
    
    def start_exam_attempt(self):
        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            is_active=True
        ).first()

        if activation and activation.paper_type == "SECONDARY":
            if self.has_primary_exam() and not self.is_primary_completed:
                raise ValidationError(
                    "Primary exam not completed. Cannot start secondary exam."
                )


        if self.has_exam_slot and self.slot_attempting_at is None:
            self.slot_attempting_at = timezone.now()
            self.save(update_fields=['slot_attempting_at'])
            return True
        return False

    
    def consume_exam_slot(self):
        if self.has_exam_slot and self.slot_consumed_at is None:
            active_paper = TradePaperActivation.objects.filter(
                trade=self.trade,
                is_active=True
            ).order_by("paper_type").first()

            if active_paper:
                if active_paper.paper_type == "PRIMARY":
                    self.is_primary_completed = True
                elif active_paper.paper_type == "SECONDARY":
                    self.is_secondary_completed = True

            self.slot_consumed_at = timezone.now()
            self.slot_attempting_at = None

            self.save(update_fields=[
                'slot_consumed_at',
                'slot_attempting_at',
                'is_primary_completed',
                'is_secondary_completed'
            ])

            return True
        return False


    
    def assign_exam_slot(self, assigned_by_user=None):
        """
        Assign exam slot safely.
        SECONDARY slot is allowed ONLY if PRIMARY is completed.
        """
        # ❌ Prevent overwriting an active slot
        if self.has_exam_slot and self.slot_consumed_at is None:
            raise ValidationError("Candidate already has an active exam slot.")

        # Check active paper
        activation = TradePaperActivation.objects.filter(
            trade=self.trade,
            is_active=True
        ).order_by("paper_type").first()

        if activation and activation.paper_type == "SECONDARY":
            if self.has_primary_exam() and not self.is_primary_completed:
                raise ValidationError(
                    f"Cannot assign SECONDARY exam slot to {self.name} "
                    f"(Army No: {self.army_no}) because PRIMARY exam is not completed."
                )


        # Existing logic (unchanged)
        self.has_exam_slot = True
        self.slot_assigned_at = timezone.now()
        self.slot_consumed_at = None
        self.slot_attempting_at = None
        self.slot_assigned_by = assigned_by_user
        self.save()
        return True
    
    def reset_exam_slot(self):
        """
        Reset/clear the exam slot
        CRITICAL FIX: Clear incomplete exam sessions to prevent old question set persistence
        """
        from questions.models import ExamSession
        
        # Clear any incomplete exam sessions to prevent old question set binding
        incomplete_sessions = ExamSession.objects.filter(
            user=self.user,
            completed_at__isnull=True
        )
        cleared_count = incomplete_sessions.count()
        if cleared_count > 0:
            incomplete_sessions.delete()
            print(f"✅ Cleared {cleared_count} incomplete sessions for {self.army_no} during slot reset")
        
        self.has_exam_slot = False
        self.slot_assigned_at = None
        self.slot_consumed_at = None
        self.slot_attempting_at = None
        self.slot_assigned_by = None
        self.save(update_fields=['has_exam_slot', 'slot_assigned_at', 'slot_consumed_at', 'slot_attempting_at', 'slot_assigned_by'])
        return True
    
    @property
    def slot_status(self):
        """Get human-readable slot status"""
        try:
            if not self.has_exam_slot:
                return "No Slot"
            elif self.slot_consumed_at:
                try:
                    return f"Consumed on {self.slot_consumed_at.strftime('%Y-%m-%d %H:%M')}"
                except (AttributeError, TypeError):
                    return "Consumed (date unknown)"
            elif self.slot_attempting_at:
                try:
                    return f"Attempting since {self.slot_attempting_at.strftime('%Y-%m-%d %H:%M')}"
                except (AttributeError, TypeError):
                    return "Currently Attempting"
            elif self.slot_assigned_at:
                try:
                    return f"Available (assigned {self.slot_assigned_at.strftime('%Y-%m-%d %H:%M')})"
                except (AttributeError, TypeError):
                    return "Available (assignment date unknown)"
            else:
                return "Available (no assignment date)"
        except Exception as e:
            # Fallback for any unexpected errors
            return f"Status Error: {str(e)}"

    def __str__(self):
        return f"{self.army_no} - {self.name}"