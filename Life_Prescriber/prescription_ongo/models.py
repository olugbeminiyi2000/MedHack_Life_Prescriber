from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import time
import uuid

# Validators for my phone number field
def validate_and_normalize_phone_number(value):
    if value == None:
        return value
    try:
        parsed_number = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(_('Invalid phone number.'))
        
        normalized_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return normalized_number
    except phonenumbers.NumberParseException:
        raise ValidationError(_('Invalid phone number.'))

# Create your models here.
class Patient(AbstractUser):
    middle_name = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=20, validators=[validate_and_normalize_phone_number], null=True, blank=True)
    insurance_id = models.CharField(max_length=700)

    def save(self, *args, **kwargs):
        """
        Normalize phone number before saving i.e when we want to save
        an instance of the patient class which inherits from the
        Abstract model class we interupt the abstract model class save
        method then we normalize phone number of that instance object
        again to international format because it could have being 
        in international format or local format but we want to save it
        in international format so we change the value of that object
        phone number.
        """
        self.phone_number = validate_and_normalize_phone_number(self.phone_number)
        super(Patient, self).save(*args, **kwargs)

    def __str__(self):
        return ("<{0}> class, middle_name <{1}>, phone number <{2}>".format(self.__class__.__name__, self.middle_name, self.phone_number)).capitalize()
    
    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    

class Prescribe(models.Model):
    prescribed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    drug_name = models.CharField(max_length=800)
    first_time = models.TimeField(default=time(0,0))
    prescribe_time = models.TimeField()
    start_time = models.DateTimeField()
    initial_proposed_date = models.DateTimeField()
    recent_proposed_date = models.DateTimeField()
    total_tablets = models.PositiveSmallIntegerField()
    total_tablets_dynamic = models.PositiveSmallIntegerField(default=0)
    no_of_times_per_day = models.PositiveSmallIntegerField()
    no_of_tablets_per_use = models.PositiveSmallIntegerField()
    general_description = models.TextField()
    reverse_value = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
       return ("<{0}> class, prescribe time <{1}>".format(self.__class__.__name__, self.prescribe_time))
    

# Create your models here.
class ClinicUser(AbstractUser):
    # overwrite the first_name, last_name, and email field
    first_name = models.CharField(max_length=300, blank=False)
    last_name = models.CharField(max_length=300, blank=False)
    email = models.EmailField(blank=False, unique=True)
    designation = models.CharField(max_length=300, null=True)
    medical_institution = models.CharField(max_length=500, null=True)

    # Define groups and user_permissions with unique related_name arguments
    groups = models.ManyToManyField('auth.Group', related_name='clinic_user_groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='clinic_user_permissions')

    class Meta:
        verbose_name = "Clinic User"
        verbose_name_plural = "Clinic Users"

class Insurance(models.Model):
    INSURANCE_CHOICES = [
        ("Prime", "Prime"),
        ("RSSB", "RSSB"),
        ("RADIANT", "RADIANT"),
        ("Old Mutual", "Old Mutual"),
        ("MUA", "MUA"),
        ("Falcon", "Falcon"),
        ("Eden Care", "Eden Care"),
        ("Britam", "Britam"),
        ("Sanlam Vie", "Sanlam Vie"),
    ]
    insurance_name = models.CharField(max_length=700, choices=INSURANCE_CHOICES, unique=True)

class OneTimeLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)