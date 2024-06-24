# forms.py
from django import forms
from .models import Prescribe, Patient

class PrescribeForm(forms.ModelForm):
    class Meta:
        model = Prescribe
        fields = ["prescribe_time", "drug_name", "total_tablets", "no_of_times_per_day", "no_of_tablets_per_use", "general_description"]

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["username"]
