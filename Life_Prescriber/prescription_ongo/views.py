from django.shortcuts import render, redirect
from django.urls import reverse
from .models import ClinicUser
from django.views import View
from .models import Patient, Prescribe
from .forms import PatientForm, PrescribeForm, SecretInsuranceRegisterForm, SecretPatientRegisterForm
from datetime import time, datetime, timedelta
from django.core.signing import BadSignature, SignatureExpired
from .utils import SIGNER
import math

# define utiity function
def send_back_error_with_previous_data(request, error_message):
    context_variable = {}
    patient_data = {"username": request.POST.get("username")}
    prescribe_data = {
        "prescribe_time": request.POST.get("prescribe_time"),
        "drug_name" : request.POST.get("drug_name"),
        "total_tablets": request.POST.get("total_tablets"),
        "no_of_times_per_day": request.POST.get("no_of_times_per_day"),
        "no_of_tablets_per_use": request.POST.get("no_of_tablets_per_use"),
        "general_description": request.POST.get("general_description"),
    }
    patient_form = PatientForm(patient_data)
    prescribe_form = PrescribeForm(prescribe_data)
    context_variable["patient_form"] = patient_form
    context_variable["prescribe_form"] = prescribe_form 
    context_variable["any_error"] = error_message
    return context_variable

def send_back_error_with_previous_data_2(request, error_message):
    context_variable = {}
    patient_data = {"username": request.POST.get("username")}
    prescribe_data = {
        "drug_name" : request.POST.get("drug_name"),
        "no_of_times_per_day": request.POST.get("no_of_times_per_day"),
        "no_of_tablets_per_use": request.POST.get("no_of_tablets_per_use"),
    }
    patient_form = PatientForm(patient_data)
    prescribe_form = PrescribeForm(prescribe_data)
    context_variable["patient_form"] = patient_form
    context_variable["prescribe_form"] = prescribe_form 
    context_variable["any_error"] = error_message
    return context_variable


# Create your views here.
class PrescribeView(View):
    template_name = "prescription_ongo/prescribtion.html"
    def get(self, request, prescription_id):
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
            If both case come out False render the prescription form
            will add some context soon.
            """
            # use the prescription_id to get the prescription
            # and then get the username and drug_name
            user_prescription= Prescribe.objects.filter(
                id=prescription_id,
            ).first()

            if user_prescription:
                patient_data = {
                    "username": user_prescription.prescribed_user.username,
                }
                prescribe_data = {
                    "drug_name": user_prescription.drug_name,
                }
            else:
                patient_data = {}
                prescribe_data = {}

            patient_form, prescribe_form = PatientForm(patient_data), PrescribeForm(prescribe_data)
            context_variable = {}
            context_variable["patient"] = user_prescription.prescribed_user
            context_variable["patient_form"] = patient_form
            context_variable["prescribe_form"] = prescribe_form
            if request.session.get("success_message", None):
                context_variable["success_message"] = request.session["success_message"]
                del request.session["success_message"]
            return render(request, self.template_name, context_variable)
             
        login_url = reverse("prescription:custom_login")
        return redirect(login_url)

    def post(self, request, prescription_id):
        context_variable = None
        periods = ["am", "pm"]
        get_username_from_post = request.POST.get("username")
        check_username_exist = Patient.objects.filter(
            username=get_username_from_post,
        )
        if not check_username_exist.exists():
            context_variable = send_back_error_with_previous_data(request, "This patient username doesn't exist.")
            return render(request, self.template_name, context_variable)
        
        get_prescribe_time_from_post = request.POST.get("prescribe_time")
        if len(get_prescribe_time_from_post) > 4:
            context_variable = send_back_error_with_previous_data(request, "prescribe time should be in this form <time><am|pm> e.g 08am or 08pm or 8pm or 8am.")
            return render(request, self.template_name, context_variable)
        
        # check if the first or first two characters can be converted to int
        try:
            try_convert = int(get_prescribe_time_from_post[0:2]) if len(get_prescribe_time_from_post) == 4 else int(get_prescribe_time_from_post[0])
        except ValueError:
                context_variable = send_back_error_with_previous_data(request, f"prescribe time should be in this form <time><am|pm> e.g 08am or 08pm or 8pm or 8am, inputed {get_prescribe_time_from_post}.")
                return render(request, self.template_name, context_variable)
        
        # check if the last 2 characters is am or pm
        period_value = get_prescribe_time_from_post[-2: ]
        if period_value.lower() not in periods:
            context_variable = send_back_error_with_previous_data(request, f"prescribe time should be in this form <time><am|pm> e.g 08am or 08pm or 8pm or 8am, inputed {get_prescribe_time_from_post}.")
            return render(request, self.template_name, context_variable)
        
        #  check if the try convert is between a range
        if not 1 <= try_convert <= 12:
            context_variable = send_back_error_with_previous_data(request, f"prescribe time should be in this form <time><am|pm> and  between range 1 to 12  e.g 08am or 08pm or 8pm or 8am, inputed {get_prescribe_time_from_post}.")
            return render(request, self.template_name, context_variable)  
                
        # now save all the data for the patient prescription
        if period_value.lower() == "am":
            start = 0 if try_convert == 12 else try_convert
            hour = 12 + 12 - 1 if try_convert == 12 else try_convert - 1
        else:
            start = 0 + try_convert if try_convert == 12 else try_convert + 12
            hour = 0 + 12 - 1 if try_convert == 12 else try_convert + 12 - 1
            
        first_time = time(hour=start, minute=0) # time the user takes drug
        prescribe_time = time(hour=hour, minute=50) # time notifications are sent
        drug_name = request.POST.get("drug_name")
        total_tablets =  request.POST.get("total_tablets")
        no_of_times_per_day =  request.POST.get("no_of_times_per_day")
        no_of_tablets_per_use =  request.POST.get("no_of_tablets_per_use")
        general_description =  request.POST.get("general_description")


        # calculate the initial_proposed_date, recent_proposed_date, start_time
        start_time = datetime.now()

        #TODO check this calculation for zero division error
        try:
            total_days = math.ceil(int(total_tablets) / (int(no_of_times_per_day) * int(no_of_tablets_per_use)))
        except ZeroDivisionError:
            context_variable = send_back_error_with_previous_data(request, "Invalid entry no_of_times_per_day or no_of_tablets_per_use cannot be 0.")
            return render(request, self.template_name, context_variable)
                 
        initial_proposed_date = start_time + timedelta(total_days - 1)
        recent_proposed_date = initial_proposed_date

        # check if the drug exist if it does just update rather than create new one 
        check_prescription_exists = Prescribe.objects.filter(
            prescribed_user=check_username_exist.first(),
            drug_name=drug_name.lower()
        ).exists()

        if check_prescription_exists:
            Prescribe.objects.filter(
                prescribed_user=check_username_exist.first(),
                drug_name=drug_name.lower()
            ).update(
                first_time=first_time,
                prescribe_time = prescribe_time,
                start_time=start_time,
                initial_proposed_date=initial_proposed_date,
                recent_proposed_date=recent_proposed_date,
                total_tablets=total_tablets,
                total_tablets_dynamic=total_tablets,
                no_of_times_per_day=no_of_times_per_day,
                no_of_tablets_per_use=no_of_tablets_per_use,
                general_description=general_description,
                reverse_value=0               
            )
        else:
            # save prescription
            Prescribe.objects.create(
                prescribed_user=check_username_exist.first(),
                drug_name=drug_name.lower(),
                first_time=first_time,
                prescribe_time = prescribe_time,
                start_time=start_time,
                initial_proposed_date=initial_proposed_date,
                recent_proposed_date=recent_proposed_date,
                total_tablets=total_tablets,
                total_tablets_dynamic=total_tablets,
                no_of_times_per_day=no_of_times_per_day,
                no_of_tablets_per_use=no_of_tablets_per_use,
                general_description=general_description,
                reverse_value=0
            )
        
        # do a post redirect get request PRGR
        # but before it save a success message to the session
        request.session["success_message"] = "Drug prescription has been updated successfully."
        return redirect(request.path)


class DrugUsedView(View):
    template_name = "prescription_ongo/"
    def get(self, request, token):
        try:
            signed_value = SIGNER.unsign(token, max_age=timedelta(minutes=15))
            username, id = signed_value.split(":")
            # TODO decrease the ttd by the number of tablets per take
            # by using the username to get patient and with id to get drug
            get_patient = Patient.objects.filter(
                username=username,
            ).first()
            get_drug = Prescribe.objects.filter(
                prescribed_user=get_patient,
                id=int(id),
            ).first()

            # check if prescription or patient doesn.t exist
            if not get_patient or not get_drug:
                return render(request, self.template_name + 'prescribe_error.html')
            
            get_total_tablets_dynamic = get_drug.total_tablets_dynamic
            get_no_of_tablets_per_use = get_drug.no_of_tablets_per_use
            new_total_tablets_dynamic = get_total_tablets_dynamic - get_no_of_tablets_per_use

            get_drug.total_tablets_dynamic = new_total_tablets_dynamic
            get_drug.save()
            return render(request, self.template_name + 'drug_used.html')
        except (BadSignature, SignatureExpired):
            return render(request, self.template_name + 'link_expired.html')
             
class ChangePrescribeView(View):
    template_name = "prescription_ongo/change_prescription.html"
    def get(self, request, prescription_id):
        if request.user.is_authenticated:
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
            If both case come out False render the prescription form
            will add some context soon.
            """
            user_prescription= Prescribe.objects.filter(
                id=prescription_id,
            ).first()

            context_variable = {}
            
            if user_prescription:
                patient_data = {
                    "username": user_prescription.prescribed_user.username,
                }
                prescribe_data = {
                    "drug_name": user_prescription.drug_name,
                }
                context_variable["patient"] = user_prescription.prescribed_user
            else:
                patient_data = {}
                prescribe_data = {}
            
            patient_form, prescribe_form = PatientForm(patient_data), PrescribeForm(prescribe_data)
            context_variable["patient_form"] = patient_form
            context_variable["prescribe_form"] = prescribe_form
            if request.session.get("success_message", None):
                context_variable["success_message"] = request.session["success_message"]
                del request.session["success_message"]
            return render(request, self.template_name, context_variable)
        
        login_url = reverse("prescription:custom_login")
        return redirect(login_url)
    
    def post(self, request, prescription_id):
        get_username_from_post = request.POST.get("username")
        check_username_exist = Patient.objects.filter(
            username=get_username_from_post,
        )
        if not check_username_exist.exists():
            context_variable = send_back_error_with_previous_data_2(request, f"This patient with username {get_username_from_post} doesn't exist.")
            return render(request, self.template_name, context_variable)
        
        drug_name = request.POST.get("drug_name")
        prescription = Prescribe.objects.filter(
            drug_name=drug_name.lower(),
            prescribed_user=check_username_exist.first(),
        ).first()

        if not prescription:
            context_variable = send_back_error_with_previous_data_2(request, f"prescrition with drug name {drug_name} for username {get_username_from_post} is not found.")
            return render(request, self.template_name, context_variable)
        
        new_no_of_times_per_day = int(request.POST.get("no_of_times_per_day"))
        new_no_of_tablets_per_use = int(request.POST.get("no_of_tablets_per_use"))

        try:
            if new_no_of_tablets_per_use == 0 or new_no_of_times_per_day == 0:
                raise ZeroDivisionError
        except ZeroDivisionError:
            context_variable = send_back_error_with_previous_data_2(request, "Invalid entry no_of_times_per_day or no_of_tablets_per_use cannot be 0.")
            return render(request, self.template_name, context_variable)          

        #TODO check if new_no_of_times_per_day or new_no_of_tablets_per_use == 0
        # to prevent zero division error

        st = prescription.start_time
        ttf = prescription.total_tablets
        ttd = prescription.total_tablets_dynamic
        ipd = prescription.initial_proposed_date
        rpd = prescription.recent_proposed_date
        pnots = prescription.no_of_times_per_day
        ptpi = prescription.no_of_tablets_per_use
        nnots = new_no_of_times_per_day
        ntpi = new_no_of_tablets_per_use
        reverse_value = prescription.reverse_value


        # solve if they are equal and reverse == 0
        if ttf == ttd and reverse_value == 0:
            total_days = math.ceil((ttf / (nnots * ntpi)))
            ipd = st + timedelta(total_days - 1)
            # update the prescribe object
            prescription = Prescribe.objects.filter(
                drug_name=drug_name.lower()
            ).update(
                no_of_times_per_day=nnots,
                no_of_tablets_per_use=ntpi,
                initial_proposed_date=ipd,
                recent_proposed_date=ipd,
            )
        
        # solve if they are equal and reverse != 0
        elif ttf == ttd and reverse_value != 0:
            first = -1 * (reverse_value - ttd)
            second = math.ceil((ttd / (pnots * ptpi)))
            third = rpd.day - ipd.day - second
            x = first / third
            # now get the rpd, no_of_times_per_day, no_of_tablets_per_use
            first = math.floor((reverse_value - ttd) / x)
            second = math.ceil((ttd) / (nnots * ntpi))
            rpd = ipd + timedelta(second - first)
            prescription = Prescribe.objects.filter(
                drug_name=drug_name.lower()
            ).update(
                recent_proposed_date=rpd,
                no_of_times_per_day=nnots,
                no_of_tablets_per_use=ntpi,         
            )
        # solve if they are not equal 
        else:
            first = math.floor(((ttf - ttd) / (pnots * ptpi)))
            second = math.ceil((ttd / (nnots * ntpi)))
            rpd = ipd + timedelta(second - first)
            prescription = Prescribe.objects.filter(
                drug_name=drug_name.lower()
            ).update(
                total_tablets=ttd,
                recent_proposed_date=rpd,
                no_of_times_per_day=nnots,
                no_of_tablets_per_use=ntpi,
                reverse_value=ttf         
            )
        # do a post redirect get request PRGR
        # but before it save a success message to the session
        request.session["success_message"] = "Drug prescription has been updated successfully."
        return redirect(request.path)
    
class HospitalSecretSearch(View):
    template_name = "prescription_ongo/registerusers.html"
    def get(self, request):
        context_dict = {}
        context_dict["search_user"] = "search_user"
        
        # check if there are query parameters in the url, so we can handle the search also in get request
        if request.GET.get("insurance_name", None) and request.GET.get("insurance_number", None):
            get_insurance_name = request.GET.get("insurance_name", None)
            get_insurance_number = request.GET.get("insurance_number", None)

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

            context_dict["msg"] = "msg"

            if check_if_user_exist.exists():
                context_dict["success_msg"] = f"User with insurance_number {clean_insurance_number} exists."
            else:
               context_dict["error_msg"] = f"User doesn't exist, create a new user or retry again."
        
        insurance_form = SecretInsuranceRegisterForm()
        context_dict["insurance_form"] = insurance_form

        return render(request, self.template_name, context_dict)

    def post(self, request):
        context_dict = {}
        context_dict["search_user"] = "search_user"
        
        # handling form submission instead of query parameter
        if request.POST.get("insurance_name", None) and request.POST.get("insurance_number", None):
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

            context_dict["msg"] = "msg"

            if check_if_user_exist.exists():
                context_dict["success_msg"] = f"User with insurance_number {clean_insurance_number} exists."
            else:
               context_dict["error_msg"] = f"User doesn't exist, create a new user or retry again."

        return render(request, self.template_name, context_dict)
    

class HospitalSecretSignUp(View):
    template_name = "prescription_ongo/registerusers.html"
    def get(self, request):
        context_dict = {}
        context_dict["register_user"] = "register_user"
        
        # create user form and inurance form
        user_form = SecretPatientRegisterForm()
        insurance_form = SecretInsuranceRegisterForm()

        context_dict["user_form"] = user_form
        context_dict["insurance_form"] = insurance_form

        if request.session.get("sign_success_msg", None):
            context_dict["sign_msg"] = "sign_msg"
            context_dict["sign_success_msg"] = request.session.get("sign_success_msg")
            del request.session["sign_success_msg"]


        return render(request, self.template_name, context_dict)
    
    def post(self, request):
        context_dict = {}
        context_dict["register_user"] = "register_user"

        # get this specific data to check for errors i.e username and insurance id
        get_username = request.POST.get("username")
        get_insurance_id = request.POST.get("insurance_id")
        get_insurance_name = request.POST.get("insurance_name")
        get_email = request.POST.get("email")

        # remove all spaces in insurance name and insurance number
        clean_username = ""
        clean_insurance_id = ""
        clean_insurance_name = ""

        for h in get_insurance_name:
            if h == "\n" or h == "\t" or h == " ":
                continue
            clean_insurance_name += h

        for i in get_username:
            if i == "\n" or i == "\t" or i == " ":
                continue
            clean_username += i
        
        for j in get_insurance_id:
            if j == "\n" or j == "\t" or j == " ":
                continue
            clean_insurance_id += j

        user_insurance_id = clean_insurance_name.lower() + "-" + clean_insurance_id.lower()
        print(user_insurance_id)

        check_user_email = Patient.objects.filter(
            email=get_email,
        )
        
        check_user_username = Patient.objects.filter(
            username=clean_username,
        )
    
        check_user_insurance_id = Patient.objects.filter(
            insurance_id=user_insurance_id,
        )

        if check_user_username.exists():
            context_dict["sign_msg"] = "sign_msg"
            context_dict["sign_error_msg"] = f"User with username {clean_username} already exists."
            return render(request, self.template_name, context_dict)
        elif check_user_insurance_id.exists():
            context_dict["sign_msg"] = "sign_msg"
            context_dict["sign_error_msg"] = f"User with insurance_id {clean_insurance_id} already exists."
            return render(request, self.template_name, context_dict)
        elif check_user_email.exists():
            context_dict["sign_msg"] = "sign_msg"
            context_dict["sign_error_msg"] = f"User with email {get_email} already exists."
            return render(request, self.template_name, context_dict)

        else:
             # save the new user by gettting firstname, middlename, lastname, username, email, and insurance id
             user_first_name = request.POST.get("first_name")
             user_middle_name = request.POST.get("middle_name")
             user_last_name = request.POST.get("last_name")
             user_email = request.POST.get("email")
             
             # save the user
             Patient.objects.create_user(
                 first_name=user_first_name.capitalize(),
                 middle_name=user_middle_name.capitalize(),
                 last_name=user_last_name.capitalize(),
                 email=user_email,
                 username=clean_username,
                 insurance_id=user_insurance_id,
             )

             request.session["sign_success_msg"] = f"New user created"
             return redirect(request.path)


class NewPrescribeView(View):
    template_name = "prescription_ongo/prescribtion.html"
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

            """
            If both case come out False render the prescription form
            will add some context soon.
            """
            # use patient_id to get patient
            context_variable = {}
            patient = Patient.objects.filter(
                id=patient_id
            ).first()

            if patient:
                patient_data = {"username": patient.username}
            else:
                patient_data = {}
            
            context_variable["patient"] = patient
            patient_form, prescribe_form = PatientForm(patient_data), PrescribeForm()
            context_variable["patient_form"] = patient_form
            context_variable["prescribe_form"] = prescribe_form
            if request.session.get("success_message", None):
                context_variable["success_message"] = request.session["success_message"]
                del request.session["success_message"]
            print("trying to cretae a new medication")
            print(request.path)
            return render(request, self.template_name, context_variable)
             
        login_url = reverse("prescription:custom_login")
        return redirect(login_url)

    def post(self, request, patient_id):
        context_variable = None
        periods = ["am", "pm"]
        get_username_from_post = request.POST.get("username")
        check_username_exist = Patient.objects.filter(
            username=get_username_from_post,
        )
        if not check_username_exist.exists():
            context_variable = send_back_error_with_previous_data(request, "This patient username doesn't exist.")
            return render(request, self.template_name, context_variable)
        
        get_prescribe_time_from_post = request.POST.get("prescribe_time")
        if len(get_prescribe_time_from_post) > 4:
            context_variable = send_back_error_with_previous_data(request, "prescribe time should be in this form <time><am|pm> e.g 08am or 08pm or 8pm or 8am.")
            return render(request, self.template_name, context_variable)
        
        # check if the first or first two characters can be converted to int
        try:
            try_convert = int(get_prescribe_time_from_post[0:2]) if len(get_prescribe_time_from_post) == 4 else int(get_prescribe_time_from_post[0])
        except ValueError:
                context_variable = send_back_error_with_previous_data(request, f"prescribe time should be in this form <time><am|pm> e.g 08am or 08pm or 8pm or 8am, inputed {get_prescribe_time_from_post}.")
                return render(request, self.template_name, context_variable)
        
        # check if the last 2 characters is am or pm
        period_value = get_prescribe_time_from_post[-2: ]
        if period_value.lower() not in periods:
            context_variable = send_back_error_with_previous_data(request, f"prescribe time should be in this form <time><am|pm> e.g 08am or 08pm or 8pm or 8am, inputed {get_prescribe_time_from_post}.")
            return render(request, self.template_name, context_variable)
        
        #  check if the try convert is between a range
        if not 1 <= try_convert <= 12:
            context_variable = send_back_error_with_previous_data(request, f"prescribe time should be in this form <time><am|pm> and  between range 1 to 12  e.g 08am or 08pm or 8pm or 8am, inputed {get_prescribe_time_from_post}.")
            return render(request, self.template_name, context_variable)  
                
        # now save all the data for the patient prescription
        if period_value.lower() == "am":
            start = 0 if try_convert == 12 else try_convert
            hour = 12 + 12 - 1 if try_convert == 12 else try_convert - 1
        else:
            start = 0 + try_convert if try_convert == 12 else try_convert + 12
            hour = 0 + 12 - 1 if try_convert == 12 else try_convert + 12 - 1
            
        first_time = time(hour=start, minute=0) # time the user takes drug
        prescribe_time = time(hour=hour, minute=50) # time notifications are sent
        drug_name = request.POST.get("drug_name")
        total_tablets =  request.POST.get("total_tablets")
        no_of_times_per_day =  request.POST.get("no_of_times_per_day")
        no_of_tablets_per_use =  request.POST.get("no_of_tablets_per_use")
        general_description =  request.POST.get("general_description")


        # calculate the initial_proposed_date, recent_proposed_date, start_time
        start_time = datetime.now()

        #TODO check this calculation for zero division error
        try:
            total_days = math.ceil(int(total_tablets) / (int(no_of_times_per_day) * int(no_of_tablets_per_use)))
        except ZeroDivisionError:
            context_variable = send_back_error_with_previous_data(request, "Invalid entry no_of_times_per_day or no_of_tablets_per_use cannot be 0.")
            return render(request, self.template_name, context_variable)
                 
        initial_proposed_date = start_time + timedelta(total_days - 1)
        recent_proposed_date = initial_proposed_date

        # check if the drug exist if it does just update rather than create new one 
        check_prescription_exists = Prescribe.objects.filter(
            prescribed_user=check_username_exist.first(),
            drug_name=drug_name.lower()
        ).exists()

        if check_prescription_exists:
            Prescribe.objects.filter(
                prescribed_user=check_username_exist.first(),
                drug_name=drug_name.lower()
            ).update(
                first_time=first_time,
                prescribe_time = prescribe_time,
                start_time=start_time,
                initial_proposed_date=initial_proposed_date,
                recent_proposed_date=recent_proposed_date,
                total_tablets=total_tablets,
                total_tablets_dynamic=total_tablets,
                no_of_times_per_day=no_of_times_per_day,
                no_of_tablets_per_use=no_of_tablets_per_use,
                general_description=general_description,
                reverse_value=0               
            )
        else:
            # save prescription
            Prescribe.objects.create(
                prescribed_user=check_username_exist.first(),
                drug_name=drug_name.lower(),
                first_time=first_time,
                prescribe_time = prescribe_time,
                start_time=start_time,
                initial_proposed_date=initial_proposed_date,
                recent_proposed_date=recent_proposed_date,
                total_tablets=total_tablets,
                total_tablets_dynamic=total_tablets,
                no_of_times_per_day=no_of_times_per_day,
                no_of_tablets_per_use=no_of_tablets_per_use,
                general_description=general_description,
                reverse_value=0
            )
        
        # do a post redirect get request PRGR
        # but before it save a success message to the session
        request.session["success_message"] = "Drug prescription has been updated successfully."
        print("done !!!")
        return redirect(request.path)


