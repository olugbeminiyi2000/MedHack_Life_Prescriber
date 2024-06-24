from django.core.signing import TimestampSigner
from django.urls import reverse

SIGNER = TimestampSigner()

def generate_prescription_url(prescription_object):
    SITE_URL = "http://127.0.0.1:8000"
    token = SIGNER.sign(prescription_object.prescribed_user.username + ':' + str(prescription_object.id))
    url = reverse("prescription:drug_used", args=[token])
    return SITE_URL + url