from celery import shared_task
# from django.core.mail import send_mass_mail
from .models import Prescribe
from datetime import datetime, timedelta
from django.core import mail
from .utils import generate_prescription_url

"""
putting a bin=True inside the @shared_task
takes note of the first running of your
celery process.

if running celery or celery beats and you want arguements
to be used in the function you must put self as the first arguement,
followed by your other arguements.
for celery where ever you would call that shared task function with the delay
method you must pass the arguements.
but for celery beats you define the arguements when configuring the
app.conf.beat_schedule = {
    'task-name': {
        'task': 'prescription_ongo.tasks.send_async_email',
        'schedule': timedelta(seconds=20),
        'args': (tuples of x number of arguments defined in the shared task)
    },
}

if no arguments is used for neither you would
remove the self, and all arguements and finally
it is better not to bind=True in shared_task decorator.

To use celery
1. first install redis from github
2. the download the msi
3. then put this software path in your environment path variable
4. the remaining steps is to install django celery, and celery beats
5. follow the whole instruction and make sure you do this

# this default_queue is very needed don't change!!!
# and also --pool=solo is compulsory when running celery worker
app.conf.task_default_queue = 'default' 

"""
@shared_task()
def send_async_email():
    # TODO here is the lace that the time calculation would be done and all other stuff.
    list_of_mail = []
    # tuple_of_mail = None

    # TODO imstead of fixed time object do datetime.now().time()
    get_current_time = datetime.now().time()

    # Get all prescription that match that time has not more than one tablet
    all_prescription_objects = Prescribe.objects.filter(
        prescribe_time__lte=get_current_time, 
    ) & Prescribe.objects.filter(
        first_time__gte=get_current_time,
    ) & Prescribe.objects.filter(
        total_tablets__gte=0,
    )
    
    # Create an email connection
    connection = mail.get_connection()

    # Manually open the connection
    connection.open()

    # iterate through each one of these prescription to use it columns
    # to create email, then send those email in mass
    for prescription_object in all_prescription_objects:
        # create timer link
        TIMER_URL = generate_prescription_url(prescription_object)
        # Construct the HTML content for the email
        html_content = f"""
            <div style="display: flex; justify-content: center; align-items: center;">
                <div
                    style="display: flex; flex-direction: column; justify-content: center; align-items: flex-start; margin-top: 45px;">
                    <div>
                        <p>Hi <span style="color: #0c81bb;">{prescription_object.prescribed_user.first_name}</span>, this is a reminder from <span
                                style="color: #0c81bb;">Life Prescriber™</span> to take <br>your medication at
                            {prescription_object.first_time}.</p>
                    </div>
                    <div
                        style="background-color: #3690d97a; border: 1px solid #0c81bb; border-radius: 20px; padding: 10px; width: 450px;">
                        <h2 style="margin: 0px; text-decoration: underline;">Presciption Details</h2>
                        <div>
                            <p><span style="font-weight: bold; color: #0c81bb;">Total tablets:</span>
                                {prescription_object.total_tablets}</p>
                            <p><span style="font-weight: bold; color: #0c81bb;">Number of dose(s) per day:</span>
                                {prescription_object.no_of_times_per_day}</p>
                            <p style="margin-bottom: 0px;"><span style="font-weight: bold; color: #0c81bb;">Number of tablets per
                                    dose:</span>
                                {prescription_object.no_of_tablets_per_use}</p>
                        </div>
                    </div>
                    <div
                        style="display: flex; flex-direction: column; align-items: flex-start; background-color: #3690d97a; border: 1px solid #0c81bb; border-radius: 20px; padding: 10px; width: 450px; margin-top: 20px;">
                        <h2 style="font-weight: bold; text-decoration: underline; margin: 0px;">General description</h2>
                        <div style="margin-top: 10px;">
                            <p style="margin: 0px; padding-top: 5px;">{prescription_object.general_description}</p>
                        </div>
                    </div>
                    <div style="display: flex; flex-direction: row; align-items: center; align-self: center; padding-top: 25px;">
                        <p>Click <a href="{TIMER_URL}" target="_blank">here</a> if prescribed dose has been completed.</p>
                    </div>
                    <div id="hero"
                        style="display: flex; flex-direction: row; align-items: center; padding-top: 25px; align-self: center;">
                        <div id="logo-div"
                            style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; width: 75px; height: 75px;">
                            <img src="./static/images/logo_placeholder.png" alt="logo" id="logo" style="height: 100%; width: 100%;">
                        </div>
                        <div class="form-elements"
                            style="display: flex; flex-direction: column; line-height: 5px; text-align: center;">
                            <h2 style="font-size: 30px; margin: 0px;"><span style="color: #0c81bb;">Life Prescriber™</span></h2>
                            <p style="text-align: end;"><span style="color: #0c81bb;">...your medication on the go!</span></p>
                        </div>
                    </div>
                    <div
                        style="display: flex; justify-content: center; align-self: center; text-align: center;  margin-top: -10px;">
                        <p style="font-size: 12px; color: #882b2b;  margin: 0px;">&copy; 2024 Life Prescriber™. All rights reserved.
                        </p>
                    </div>
                </div>
        """

        # Create an EmailMessage with the HTML content
        email = mail.EmailMessage(
            subject="Prescription Reminder",
            body=html_content,
            from_email="obolo.emmanuel31052000@gmail.com",
            to=[prescription_object.prescribed_user.email],
            connection=connection,  # Use the existing connection
        )

        # Set the content subtype to HTML
        email.content_subtype = "html"

        # Append the email to the list
        list_of_mail.append(email)

    # Send all emails in a single call
    connection.send_messages(list_of_mail)

    # Close the connection
    connection.close()


    # for prescription_object in all_prescription_objects:
    #     print(prescription_object.prescribed_user.email)
    #     create_mail = (
    #         "Prescription Reminder",
    #         f"This is a reminder from the hospital for you to take your medication at {prescription_object.first_time}.\nThis are more details concerning you medication.\nTotal Tablets: {prescription_object.total_tablets}.\nNumber of times per day: {prescription_object.no_of_times_per_day}.\nNumber of tablets to take: {prescription_object.no_of_tablets_per_use}\nGeneral Description: {prescription_object.general_description}.",
    #         "obolo.emmanuel31052000@gmail.com",
    #         [f"{prescription_object.prescribed_user.email}"]
    #     )
    #     list_of_mail.append(create_mail)
    # tuple_of_mail = tuple(list_of_mail)
    # send_mass_mail(tuple_of_mail, fail_silently=False)

    # TODO update all prescribe time, start time , and total number of tablets using the
    # no_of_tablets_per_use for total number of tablets
    # no_of_times_per_day for prescribe time and start time.- checked
    for prescription_object in all_prescription_objects:
        prescribe_time = prescription_object.prescribe_time
        first_time  = prescription_object.first_time
        # calculate the next time these prescribe time would be triggered
        hours_to_add = 24 // prescription_object.no_of_times_per_day
        current_datetime = datetime.now()
        prescribe_time = datetime.combine(current_datetime, prescribe_time)
        first_time = datetime.combine(current_datetime, first_time)
        prescribe_time = prescribe_time + timedelta(hours=hours_to_add)
        first_time = first_time + timedelta(hours=hours_to_add)
        Prescribe.objects.filter(
            id=prescription_object.id
        ).update(
            prescribe_time=prescribe_time,
            first_time=first_time,
        )