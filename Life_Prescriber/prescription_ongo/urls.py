from django.urls import path
from . import views2
from . import views

app_name = "prescription_ongo"

urlpatterns = [
    # clinic user functions
    path('prescribe/', views.PrescribeView.as_view(), name="prescribe"),
    path('change_prescribe/', views.ChangePrescribeView.as_view(), name="change_prescribe"),
    path('drug_used/<str:token>/', views.DrugUsedView.as_view(), name="drug_used"),
    # clinic user authentication
    path("custom_login/", views2.CustomLogin.as_view(template_name="prescription_ongo/custom_login.html"), name="custom_login"),
    path("custom_home/", views2.CustomHome.as_view(), name="custom_home"),
    path("custom_logout/", views2.CustomLogout.as_view(), name="custom_logout"),
    path("custom_ban/", views2.CustomBan.as_view(), name="custom_ban"),
    path("custom_password_reset/", views2.CustomPasswordReset.as_view(), name="custom_password_reset"),
    path("custom_password_reset_done/", views2.CustomPasswordResetDone.as_view(), name="custom_password_reset_done"),
    path("custom_reset/<str:uidb64>/<str:token>/", views2.CustomReset.as_view(), name="custom_reset"),
    path("custom_reset_done/", views2.CustomResetDone.as_view(), name="custom_reset_done"),
    path("custom_password_reset_warning/", views2.CustomPasswordResetWarning.as_view(), name="custom_password_reset_warning"),
]