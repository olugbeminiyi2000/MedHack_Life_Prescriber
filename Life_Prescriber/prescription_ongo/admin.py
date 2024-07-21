# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import Patient
# from .models import ClinicUser

# # Register models here 
# admin.site.register(Patient, UserAdmin)
# admin.site.register(ClinicUser, UserAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Patient, ClinicUser, Insurance, Prescribe

class PatientAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Extra Personal info', {'fields': ('middle_name', 'phone_number', 'insurance_id')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'middle_name', 'phone_number'),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)


class ClinicUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Extra Personal info', {'fields': ('designation', 'medical_institution')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'designation', 'medical_institution'),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('insurance_name', )
    search_fields = ('insurance_name', )



class PrescribeAdmin(admin.ModelAdmin):
    list_display = ('drug_name', 'prescribe_time', 'start_time', 'total_tablets', 'no_of_times_per_day', 'no_of_tablets_per_use')
    search_fields = ('prescribed_user__username', 'prescribed_user__first_name', 'prescribed_user__last_name', 'prescribed_user__middle_name','drug_name')
    list_filter = ('prescribe_time', 'start_time', 'initial_proposed_date', 'recent_proposed_date')

admin.site.register(Prescribe, PrescribeAdmin)
admin.site.register(Insurance, InsuranceAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(ClinicUser, ClinicUserAdmin)
