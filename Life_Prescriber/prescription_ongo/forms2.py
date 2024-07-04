from django.contrib.auth.forms import UserCreationForm
from .models import ClinicUser
from django import forms


class ClinicUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ClinicUser
        fields = ("first_name", "last_name", "email") + UserCreationForm.Meta.fields

class ClinicUserLoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username/Email', max_length=300)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)