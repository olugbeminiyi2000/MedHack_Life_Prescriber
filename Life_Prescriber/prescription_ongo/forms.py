# forms.py
from django import forms
from .models import Prescribe, Patient, Insurance

class PrescribeForm(forms.ModelForm):
    class Meta:
        model = Prescribe
        fields = ["prescribe_time", "drug_name", "total_tablets", "no_of_times_per_day", "no_of_tablets_per_use", "general_description"]

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["username"]

class SecretPatientRegisterForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "middle_name", "last_name", "username", "email", "insurance_id"]

class SecretInsuranceRegisterForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ["insurance_name"]