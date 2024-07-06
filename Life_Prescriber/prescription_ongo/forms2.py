from django.contrib.auth.forms import UserCreationForm
from .models import ClinicUser
from django import forms


class ClinicUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ClinicUser
        fields = ("first_name", "last_name", "email") + UserCreationForm.Meta.fields + ("designation", "medical_institution")

class ClinicUserLoginForm(forms.Form):
    username_or_email = forms.CharField(max_length=300)
    password = forms.CharField(widget=forms.PasswordInput)