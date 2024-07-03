
from django.shortcuts import render, redirect
from django.views import View
# from django.http import HttpResponse
# from django.utils.http import urlencode
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms2 import ClinicUserLoginForm
from .models import ClinicUser
from .forms3 import ClinicUserPasswordCheck, ClinicUserPasswordResetForm, ClinicUserSetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
# Create your views here.

def custom_send_password_reset_link(custom_user):
    # Generate a password reset token
    token_generator = PasswordResetTokenGenerator()
    # encode the customer user primary key in base64
    uidb64 = urlsafe_base64_encode(force_bytes(custom_user.pk))
    # attach that token to the customer for later verification
    token = token_generator.make_token(custom_user)

    # Construct the password reset URL
    reset_url = f'http://127.0.0.1:8000/prescription_ongo/custom_reset/{uidb64}/{token}/'

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
            custom_logged_user = request.user
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
                # response = redirect(reverse("prescription:custom_home"))
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
        message = "Incorrect details password or username_email wrong or you are not a user on the platform"
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