from django.contrib import admin
from .models import ExamDayAvailability, Shift

# @admin.register(ExamDayAvailability)
# class ExamDayAvailabilityAdmin(admin.ModelAdmin):
#     list_display = ['date']
#     filter_horizontal = ['trades']  # if categories is ManyToMany


# admin.py
from django import forms
from django.contrib import admin
from exams.models import Shift
from registration.models import CandidateProfile
from reference.models import Trade   # adjust if your Trade app is different


class ShiftAdminForm(forms.ModelForm):
    trade_selector = forms.ModelChoiceField(
        queryset=Trade.objects.all(),
        required=False,
        empty_label="-- Select Trade --",
        help_text="Pick a trade to assign candidates. Or leave blank to assign manually."
    )
    all_trades = forms.BooleanField(
        required=False,
        label="All Trades",
        help_text="Tick this to assign ALL candidates to this shift, ignoring trade."
    )

    class Meta:
        model = Shift
        fields = "__all__"


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    form = ShiftAdminForm
    list_display = ("exam_center", "date", "start_time")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        trade = form.cleaned_data.get("trade_selector")
        all_trades = form.cleaned_data.get("all_trades")

        if all_trades:
            # assign all candidates to this shift
            CandidateProfile.objects.update(shift=obj)
        elif trade:
            # assign only candidates of selected trade
            CandidateProfile.objects.filter(trade=trade).update(shift=obj)
