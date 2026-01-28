# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime
from exams.models import Shift
from django.core.validators import RegexValidator

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
    slot_consumed_at = models.DateTimeField(null=True, blank=True, verbose_name="Slot Consumed At")
    slot_assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="assigned_slots",
        verbose_name="Slot Assigned By"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
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

    @property
    def can_start_exam(self):
        # First check if candidate has an available exam slot
        if not self.has_exam_slot:
            return False
            
        # Check if slot is consumed but a fresh slot was assigned after consumption
        if self.slot_consumed_at:
            if self.slot_assigned_at and self.slot_assigned_at > self.slot_consumed_at:
                # Fresh slot assigned after consumption - allow exam
                pass
            else:
                # Slot consumed and no fresh assignment
                return False
            
        # Check if there's an active exam for this candidate's trade
        if not self.trade:
            return False
        
        from questions.models import TradePaperActivation
        active_exam = TradePaperActivation.objects.filter(
            trade=self.trade,
            is_active=True
        ).exists()
        
        return active_exam
    
    def consume_exam_slot(self):
        """Mark the exam slot as consumed when user enters exam interface"""
        if self.has_exam_slot and self.slot_consumed_at is None:
            self.slot_consumed_at = timezone.now()
            self.save(update_fields=['slot_consumed_at'])
            return True
        return False
    
    def assign_exam_slot(self, assigned_by_user=None):
        """Assign a new exam slot to the candidate"""
        self.has_exam_slot = True
        self.slot_assigned_at = timezone.now()
        self.slot_consumed_at = None  # Clear any previous consumption
        self.slot_assigned_by = assigned_by_user
        self.save(update_fields=['has_exam_slot', 'slot_assigned_at', 'slot_consumed_at', 'slot_assigned_by'])
        return True
    
    def reset_exam_slot(self):
        """Reset/clear the exam slot"""
        self.has_exam_slot = False
        self.slot_assigned_at = None
        self.slot_consumed_at = None
        self.slot_assigned_by = None
        self.save(update_fields=['has_exam_slot', 'slot_assigned_at', 'slot_consumed_at', 'slot_assigned_by'])
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