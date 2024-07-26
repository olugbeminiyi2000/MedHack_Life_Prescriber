import os
from dotenv import load_dotenv
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms2 import ClinicUserLoginForm, ClinicUserCreationForm
from .forms import SecretInsuranceRegisterForm
from .models import ClinicUser, Patient, Prescribe
from .forms3 import ClinicUserPasswordCheck, ClinicUserPasswordResetForm, ClinicUserSetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
# Create your views here.

load_dotenv()

def custom_send_password_reset_link(custom_user):
    # Generate a password reset token
    token_generator = PasswordResetTokenGenerator()
    # encode the customer user primary key in base64
    uidb64 = urlsafe_base64_encode(force_bytes(custom_user.pk))
    # attach that token to the customer for later verification
    token = token_generator.make_token(custom_user)

    # Construct the password reset URL
    if settings.DEBUG:
        SITE_URL = os.getenv("LOCAL_HOST")
    else:
        SITE_URL = os.getenv("WEB_HOST")

    reset_url = f'{SITE_URL}/prescription_ongo/custom_reset/{uidb64}/{token}/'

    # # Construct the email subject and body
    subject = "Life Prescriber Clinic User Password Reset"
    message = render_to_string('prescription_ongo/custom_password_reset_email.html', {'reset_url': reset_url, 'email': custom_user.email})

    send_mail(subject, message, 'obolo.emmanuel31052000@gmail.com', [custom_user.email])


class CustomHome(View):
    template_name = "prescription_ongo/custom_home.html"
    def get(self, request):
        if request.user.is_authenticated:
            # TODO: make sure you do what is in the docstring
            """
            check if cookies is expired and redirect them login as
            get request and after authentication new cookies are added,
            and we are sent to custom_home.
            """
            if not (request.COOKIES.get("custom_session", None) == "session_cookie") or \
                    not (request.COOKIES.get("custom_time", None) == "time_cookie"):
                login_url = reverse("prescription:custom_login")
                return redirect(login_url)
            """
            we need to know the user authenticated either django user
            or custom user.
            """
            if not isinstance(request.user, ClinicUser):
                login_url = reverse("prescription:custom_login")
                return redirect(login_url)

            """
            If both case come out False render the custom home page
            will add some context soon.
            """
            context = {}
            
            if request.session.get("error_msg", None):
                context["error_msg"] = request.session["error_msg"]
                context["err_insurance_number"] = request.session["insurance_number"]
                insurance_name = request.session["insurance_name"]
                insurance_form = SecretInsuranceRegisterForm({"insurance_name": insurance_name})
                del request.session["error_msg"]
                del request.session["insurance_number"]
                del request.session["insurance_name"]
            elif request.session.get("success_msg", None):
                insurance_form = SecretInsuranceRegisterForm()
                context["success_msg"] = request.session["success_msg"]
                context["patient"] = Patient.objects.filter(
                    id=request.session["patient_id"],
                ).first()
                del request.session["success_msg"]
                del request.session["patient_id"]                
            else:
                insurance_form = SecretInsuranceRegisterForm()

            custom_logged_user = request.user
            context["insurance_form"] = insurance_form
            context["custom_logged_user"] = custom_logged_user
            return render(request, self.template_name, context)
        login_url = reverse("prescription:custom_login")
        return redirect(login_url)

class CustomLogin(View):
    # this template_name would be over written in the urls.py
    template_name = None
    # define the get request to this view
    def get(self, request):
        # create the custom login form
        custom_login_form = ClinicUserLoginForm()
        # create the context variable to take this form object
        context = {}
        context["custom_login_form"] = custom_login_form
        if request.session.get("add_user_success_msg", None):
            context["success_message"] = request.session["add_user_success_msg"]
            del request.session["add_user_success_msg"]
        return render(request, self.template_name, context)

    def post(self, request):
        # get the username_email and password first
        username_or_email = request.POST.get("username_or_email")
        password = request.POST.get("password")

        # now we have to authenticate using our already defined CustomBackend class
        authenticate_user = authenticate(
                request,
                username_or_email=username_or_email,
                password=password,
        )
        # check if the authenticated user is not None
        if authenticate_user is not None:
            # check to see that custom user is not active
            # then make the user active
            if authenticate_user.is_active:
                # log the custom user in
                login(request, authenticate_user)
                # display a flash message for successful login
                messages.success(request, "CustomUser logged in...😎")
                
                # TODO: make sure you do what is in the docstring
                """
                before you redirect custom_home add cookies to it.
                session cookies, and time period cookies.
                """
                response = redirect("/site/home.html")

                # set seesion cookie that will expire if browser is closed
                response.set_cookie("custom_session", "session_cookie", max_age=None)

                #set time cookie that will expire after about 2hours in seconds
                response.set_cookie("custom_time", "time_cookie", max_age=7200)

                # redirect the custom user to the custom_home
                return response
            else:
                # redirect to the user has been blocked
                return redirect(reverse("prescription:custom_ban"))
        context = {}
        custom_login_form = ClinicUserLoginForm(request.POST)
        context["custom_login_form"] = custom_login_form
        message = "Incorrect password, username or email or you are not a user on the platform"
        context["error_message"] = message
        return render(request, self.template_name, context)

class CustomLogout(View):
    # no template is being rendered
    # just logout the current user using the logout function
    # then redirect to a success page in this case back to the custom login
    def get(self, request):
        # logout the current user using logout(request) function
        logout(request)
        # add a flash message to the login file to indicate login succesful
        messages.success(request, "CustomUser successfully logged out 😎")
        # then redirect success page i.e out custom login
        return redirect(reverse("prescription:custom_login"))

class CustomPasswordResetWarning(View):
    template_name = "prescription_ongo/custom_password_reset_warning.html"
    
    def get(self, request):
        context = {}
        context["error_message"] = request.session.get("error_message", "You shouldn't be here User :|")
        if "error_message" in request.session:
            del request.session["error_message"]
        return render(request, self.template_name, context)


class CustomBan(View):
    template_name = "prescription_ongo/custom_ban.html"

    def get(self, request):
        context = {}
        context["error_message"] = request.session.get("error_message", "You shouldn't be here User :|")
        if "error_message" in request.session:
            del request.session["error_message"]
        return render(request, self.template_name, context)

class CustomResetDone(View):
    template_name = "prescription_ongo/custom_reset_done.html"
    def get(self, request):
        return render(request, self.template_name)

class CustomReset(View):
    template_name = "prescription_ongo/custom_reset_confirm_form.html"

    def get(self, request, uidb64, token):
        custom_password_check_form = ClinicUserPasswordCheck()

        # create context
        context = {}
        context["custom_password_check_form"] = custom_password_check_form

        # return render
        return render(request, self.template_name, context)

    def post(self, request, uidb64, token):
        # check if this was just a made up uidb64 not linked to a user
        # so decode uidb64 and extract the primarykey
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            custom_user = ClinicUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, ClinicUser.DoesNotExist):
            custom_user = None

        # check if user is not None and we also have to check if the token we got
        # attached user is the same with the user we got from the uid extraction
        if custom_user is not None and default_token_generator.check_token(custom_user, token):
            # check for form validation i.e if passwords match
            # but also but the custom user so we can save the new reset password
            # if the form is valid.
            custom_set_password_form = ClinicUserSetPasswordForm(custom_user, request.POST)

            if not custom_set_password_form.is_valid():
                # create context
                context = {}
                context["custom_password_check_form"] = ClinicUserPasswordCheck()
                context["custom_set_password_form"] = custom_set_password_form
                
                # return render
                return render(request, self.template_name, context)

            # save the new reset password 
            custom_set_password_form.save()
            
            # return redirect
            return redirect(reverse("prescription:custom_reset_done"))
        else:
            request.session["error_message"] = "You have no right to reset anything, be warned!!!"
            warning_page_url = reverse("prescription:custom_password_reset_warning")
            return redirect(warning_page_url)

class CustomPasswordResetDone(View):
    template_name = "prescription_ongo/custom_password_reset_done.html"

    def get(self, request):
        return render(request, self.template_name)

class CustomPasswordReset(View):
    template_name = "prescription_ongo/custom_password_reset_form.html"
    
    def get(self, request):
        custom_password_reset_form = ClinicUserPasswordResetForm()
        # create context
        context = {}
        context["custom_password_reset_form"] = custom_password_reset_form
        return render(request, self.template_name, context)

    def post(self, request):
        # check if the form is valid in terms of email validation
        # create a context first
        context = {}
        custom_password_reset_form = ClinicUserPasswordResetForm(request.POST)
        if not custom_password_reset_form.is_valid():
            context["custom_password_reset_form"] = custom_password_reset_form
            return render(request, self.template_name, context)

        # now check for the three cases needed to send reset pasword link to mail
        # 1. check if the email provided exists
        post_request_copy = request.POST.copy()
        get_email_address = post_request_copy.get("email")
        check_email_address_exists = ClinicUser.objects.filter(
            email=get_email_address,
        ).exists()
        if not check_email_address_exists:
            request.session["error_message"] = f"The user with email address {get_email_address} doesn't exist."
            warning_page_url = reverse("prescription:custom_password_reset_warning")
            return redirect(warning_page_url)

        # 2. check if user is still active maybe they have been kicked from the system
        check_user_still_active = ClinicUser.objects.filter(
            email=get_email_address,
        ).first()
        if not check_user_still_active.is_active:
            request.session["error_message"] = f"The user with email address {get_email_address} has been blocked"
            ban_page_url = reverse("prescription:custom_ban")
            return redirect(ban_page_url)

        # 3. check if user has usable password
        if not check_user_still_active.has_usable_password():
             request.session["error_message"] = f"The user with email address {get_email_address} has no password"
             warning_page_url = reverse("prescription:custom_password_reset_warning")
             return redirect(warning_page_url)

        # if case are justified time to send password reset link to user email
        custom_send_password_reset_link(check_user_still_active)
        return redirect(reverse("prescription:custom_password_reset_done"))

class SecretClinicUserAdd(View):
    template_name = "prescription_ongo/pharmacy_crud.html"
    def get(self, request):
        context_dict = {}
        context_dict["add_user"] = "add_user"

        # get pharmacist signup form
        signup_form = ClinicUserCreationForm()
        context_dict["signup_form"] = signup_form

        if request.session.get("delete_user_success_msg", None):
            context_dict["delete_user_success_msg"] = request.session["delete_user_success_msg"]
            del request.session["delete_user_success_msg"]

        return render(request, self.template_name, context_dict)
    
    def post(self, request):
        context_dict = {}
        context_dict["add_user"] = "add_user"
        # get the request.POST data inorder to validate it
        signup_form = ClinicUserCreationForm(request.POST)
        # validate form
        if not signup_form.is_valid():
            context_dict["add_user_err_msg"] = "An error occured in the form check form."
            context_dict["signup_form"] = signup_form
            return render(request, self.template_name, context_dict)
        # if form is valid save the form to database
        # signup_form.save()

        user_first_name = request.POST.get("first_name")
        user_last_name = request.POST.get("last_name")
        user_username = request.POST.get("username")
        user_email = request.POST.get("email")
        user_designation = request.POST.get("designation")
        user_medical_institution = request.POST.get("medical_institution")
        user_password = request.POST.get("password1")

        ClinicUser.objects.create_user(
            first_name=user_first_name.capitalize(),
            last_name=user_last_name.capitalize(),
            username=user_username,
            email=user_email,
            designation=user_designation.capitalize(),
            medical_institution=user_medical_institution.capitalize(),
            password=user_password,
        )


             
        # then save a success message in session then redirect to splash screen
        request.session["add_user_success_msg"] = "A new pharmacist has been created."
        return redirect("/site/splash_screen.html")
    

class SecretClinicUserDelete(View):
    template_name = "prescription_ongo/pharmacy_crud.html"
    def get(self, request):
        context_dict = {}
        context_dict["delete_user"] = "delete_user"

        return render(request, self.template_name, context_dict)
    
    def post(self, request):
        context_dict = {}
        context_dict["delete_user"] = "delete_user" 

        # check the username and see if it exists in the database if it doesn't not send an error
        get_username = request.POST.get("username")
        check_if_user_exists = ClinicUser.objects.filter(
            username=get_username,
        )
        if not check_if_user_exists.exists():
            context_dict["delete_user_error_msg"] = f"This staff with username {get_username} doesn't exist."
            context_dict["staff"] = get_username
            return render(request, self.template_name, context_dict)
        
        
        # add message to session
        request.session["delete_user_success_msg"] = f"User {check_if_user_exists.first().first_name} {check_if_user_exists.first().last_name} successfully deleted..."

        # if user exists remove user from database
        ClinicUser.objects.filter(
            username=get_username
        ).delete()

        # now return a redirect to clinicuseradd
        return redirect(reverse("prescription:secret_add_user"))
        

class PharmacySecretSearch(View):
    def get(self, request):
        return redirect("prescription:custom_home")
    
    def post(self, request):
        get_insurance_name = request.POST.get("insurance_name")
        get_insurance_number = request.POST.get("insurance_number")

        # remove all spaces in insurance name and insurance number
        clean_insurance_name = ""
        clean_insurance_number = ""

        for i in get_insurance_name:
            if i == "\n" or i == "\t" or i == " ":
                continue
            clean_insurance_name += i
        
        for j in get_insurance_number:
            if j == "\n" or j == "\t" or j == " ":
                continue
            clean_insurance_number += j
        
        # check if that insurance id exist
        insurance_id = clean_insurance_name.lower() + "-" + clean_insurance_number.lower()
        print(insurance_id)

        check_if_user_exist = Patient.objects.filter(
            insurance_id=insurance_id,
        )            

        if check_if_user_exist.exists():
            # now get the id of that patient and save a success message
            patient_id = check_if_user_exist.first().id
            request.session["patient_id"] = patient_id
            request.session["success_msg"] = f"User with insurance_number {insurance_id} exists."
            return redirect("prescription:custom_home")
        else:
            request.session["error_msg"] = f"User doesn't exist, create a new user or retry again."
            request.session["insurance_name"] = get_insurance_name
            request.session["insurance_number"] = get_insurance_number
            return redirect("prescription:custom_home")
    

class UserPrescription(View):
    template_name = "prescription_ongo/user_prescription.html"

    def get(self, request, patient_id):
        if request.user.is_authenticated:
            # TODO: make sure you do what is in the docstring
            """
            check if cookies is expired and redirect them login as
            get request and after authentication new cookies are added,
            and we are sent to custom_home.
            """
            if not (request.COOKIES.get("custom_session", None) == "session_cookie") or \
                    not (request.COOKIES.get("custom_time", None) == "time_cookie"):
                login_url = reverse("prescription:custom_login")
                return redirect(login_url)
            """
            we need to know the user authenticated either django user
            or custom user.
            """
            if not isinstance(request.user, ClinicUser):
                login_url = reverse("prescription:custom_login")
                return redirect(login_url)
            
            context_dict = {}
            # get the patient first then get the prescription(s) for that patient
            patient = Patient.objects.filter(
                id=patient_id,
            ).first()
            if patient:
                context_dict["patient_first_name"] = patient.first_name
                context_dict["patient_last_name"] = patient.last_name
            
            context_dict["patient"] = patient

            # extract the search query incase it was given
            # and use it to filter the prescription
            search_query = request.GET.get("search", "")
            
            all_prescriptions = Prescribe.objects.filter(
                prescribed_user=patient,
                drug_name__istartswith=search_query,
            ).all().order_by("-start_time")
            
            if not all_prescriptions and search_query:
                all_prescriptions = Prescribe.objects.filter(
                    prescribed_user=patient,
                    drug_name__istartswith="",
                ).all().order_by("-start_time")

            context_dict["all_prescriptions"] = all_prescriptions
            return render(request, self.template_name, context_dict)
                
        login_url = reverse("prescription:custom_login")
        return redirect(login_url)