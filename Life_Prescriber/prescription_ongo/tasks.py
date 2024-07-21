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
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Medication Reminder</title>
                </head>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #345C72; color: white; text-align: center; padding: 20px; font-size: 24px;">
                        Hi <span style="color: #0c81bb;">{prescription_object.prescribed_user.first_name}</span>, this is a reminder from <span style="color: #0c81bb;">Life Prescriber™</span> to take your medication at {prescription_object.first_time}.
                    </div>
                    <div style="background-color: #3690d97a; border: 1px solid #0c81bb; border-radius: 20px; padding: 10px; margin-top: 20px;">
                        <h2 style="margin: 0; text-decoration: underline;">Prescription Details</h2>
                        <p><strong>Total tablets:</strong> {prescription_object.total_tablets}</p>
                        <p><strong>Number of dose(s) per day:</strong> {prescription_object.no_of_times_per_day}</p>
                        <p style="margin-bottom: 0;"><strong>Number of tablets per dose:</strong> {prescription_object.no_of_tablets_per_use}</p>
                    </div>
                    <div style="background-color: #3690d97a; border: 1px solid #0c81bb; border-radius: 20px; padding: 10px; margin-top: 20px;">
                        <h2 style="font-weight: bold; text-decoration: underline; margin: 0;">General description</h2>
                        <p style="margin: 0; padding-top: 5px;">{prescription_object.general_description}</p>
                    </div>
                    <div style="padding-top: 25px; text-align: center;">
                        Click <a href="{TIMER_URL}" target="_blank" style="color: #0c81bb; text-decoration: none;">here</a> if the prescribed dose has been completed.
                    </div>
                    <div style="display: flex; align-items: center; padding-top: 25px; text-align: center;">
                        <div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; width: 75px; height: 75px;">
                            <img src="static/images/logo_placeholder.png" alt="logo" style="height: 100%; width: 100%;">
                        </div>
                        <div style="display: flex; flex-direction: column; line-height: 5px; text-align: center;">
                            <h2 style="font-size: 30px; margin: 0;"><span style="color: #0c81bb;">Life Prescriber™</span></h2>
                            <p style="color: #0c81bb; margin: 0;">...your medication on the go!</p>
                        </div>
                    </div>
                    <div style="text-align: center; font-size: 12px; color: #882b2b; margin-top: -10px;">
                        © 2024 Life Prescriber™. All rights reserved.
                    </div>
                </body>
                </html>
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