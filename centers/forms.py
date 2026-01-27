from django import forms
from .models import Center, EXAM_CENTER_CHOICES


class CenterAdminForm(forms.ModelForm):
    class Meta:
        model = Center
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make exam_Center field dynamic based on comd selection
        self.fields['exam_Center'].widget = forms.Select()
        
        # Get the comd value from initial data or form data
        comd_value = None
        
        # Check if we have an instance (editing existing record)
        if self.instance and self.instance.pk:
            comd_value = self.instance.comd
        # Check if comd is in the form data (during form submission)
        elif 'comd' in self.data:
            comd_value = self.data.get('comd')
        # Check if comd is in initial data
        elif 'comd' in self.initial:
            comd_value = self.initial.get('comd')
        
        # Set choices based on comd value
        if comd_value and comd_value in EXAM_CENTER_CHOICES:
            self.fields['exam_Center'].choices = [('', 'Select Exam Center')] + EXAM_CENTER_CHOICES[comd_value]
        else:
            self.fields['exam_Center'].choices = [('', 'Select Command first')]
        
        # Add data attribute to comd field for JavaScript
        self.fields['comd'].widget.attrs.update({
            'onchange': 'updateExamCenters(this.value)',
            'class': 'comd-select'
        })
        
        # Add data attribute to exam_Center field for JavaScript
        self.fields['exam_Center'].widget.attrs.update({
            'class': 'exam-center-select'
        })