# forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import CandidateProfile
from reference.models import Trade

User = get_user_model()

class CandidateRegistrationForm(forms.ModelForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    trade = forms.ModelChoiceField(
        queryset=Trade.objects.all().order_by("name"),
        empty_label="-- Select Trade --",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    class Meta:
        model = CandidateProfile
        fields = [
        "army_no", "rank", "trade", "name", "unit", "dob", "doe",
        "aadhar_number", "mobile_no", "apaar_id", "father_name", "photograph", "brigade", "corps", "command",
        "primary_qualification", "primary_duration", "primary_credits",
        "secondary_qualification", "secondary_duration", "secondary_credits",
        "nsqf_level", "exam_center", "training_center",
        "state", "district", "shift",
        ]
        widgets = {
            # "dob": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "doe": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Create a temporary instance to validate trade-specific rules
        # Note: This only validates the fields that are in the registration form
        # Marks validation will happen when marks are entered later in admin
        
        return cleaned_data

    def save(self, commit=True):
        # Create the User first
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        # create_user will hash the password
        user = User.objects.create_user(username=username, password=password)

        # Create CandidateProfile instance but don't save to DB yet
        candidate = super().save(commit=False)
        candidate.user = user

        if commit:
            candidate.save()  # will also save file fields (photograph) provided request.FILES passed into form
        return candidate


# -------------------------
# Admin Form for Marks Entry (if needed separately)
# -------------------------
class CandidateMarksForm(forms.ModelForm):
    """Form specifically for entering marks with validation"""
    
    class Meta:
        model = CandidateProfile
        fields = [
            "primary_practical_marks", "primary_viva_marks",
            "secondary_practical_marks", "secondary_viva_marks"
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text based on trade
        if self.instance and self.instance.trade:
            trade_name = self.instance.trade.name.strip().upper()
            if trade_name in ["OCC", "DMV"]:
                self.fields['primary_practical_marks'].help_text = "Maximum: 20 marks"
                self.fields['primary_viva_marks'].help_text = "Maximum: 5 marks"
            else:
                self.fields['primary_practical_marks'].help_text = "Maximum: 30 marks"
                self.fields['primary_viva_marks'].help_text = "Maximum: 10 marks"
            
            # Secondary is always 30/10 for all trades that have it
            self.fields['secondary_practical_marks'].help_text = "Maximum: 30 marks"
            self.fields['secondary_viva_marks'].help_text = "Maximum: 10 marks"
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Update instance with form data before validation
        instance = self.instance
        for field_name in ['primary_practical_marks', 'primary_viva_marks', 
                          'secondary_practical_marks', 'secondary_viva_marks']:
            if field_name in cleaned_data:
                setattr(instance, field_name, cleaned_data[field_name])
        
        # Run model validation
        try:
            instance.full_clean()
        except ValidationError as e:
            # Convert model validation errors to form errors
            if hasattr(e, 'message_dict'):
                for field, messages in e.message_dict.items():
                    for message in messages:
                        self.add_error(field, message)
            else:
                raise forms.ValidationError(str(e))
        
        return cleaned_data