import os
from dotenv import load_dotenv
from django.conf import settings
from django.core.signing import TimestampSigner
from django.urls import reverse
from .models import OneTimeLink

load_dotenv()
SIGNER = TimestampSigner()

def generate_prescription_url(prescription_object):
    if settings.DEBUG:
        SITE_URL = os.getenv("LOCAL_HOST")
    else:
        SITE_URL = os.getenv("WEB_HOST")
    # create timer token
    timer_token = SIGNER.sign(prescription_object.prescribed_user.username + ':' + str(prescription_object.id))
    # create clicked token
    one_time_link = OneTimeLink.objects.create()
    clicked_token = one_time_link.token
    url = reverse("prescription:drug_used", args=[timer_token, clicked_token])
    return SITE_URL + url