from django.contrib.auth.forms import UserCreationForm
from .models import ClinicUser
from django import forms


class ClinicUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ClinicUser
        fields = ("first_name", "last_name", "email") + UserCreationForm.Meta.fields + ("designation", "medical_institution")


class StaffInviteForm(forms.Form):
    ROLE_CHOICES = [("staff", "Staff"), ("head", "Head (admin privileges)")]

    invited_email = forms.EmailField(
        label="Staff Email Address",
        widget=forms.EmailInput(attrs={"placeholder": "staff@institution.com"}),
    )
    role = forms.ChoiceField(
        label="Role",
        choices=ROLE_CHOICES,
        initial="staff",
    )


class StaffSelfRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ClinicUser
        fields = ("first_name", "last_name", "email") + UserCreationForm.Meta.fields + ("designation",)

class ClinicUserLoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username/Email', max_length=300)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)