from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Patient
from .models import ClinicUser

# Register models here 
admin.site.register(Patient, UserAdmin)
admin.site.register(ClinicUser, UserAdmin)
