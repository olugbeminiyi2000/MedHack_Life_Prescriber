from django.core.signing import TimestampSigner
from django.urls import reverse
SIGNER_2 = TimestampSigner()

def generate_secret_url(link_name):
    # create timer token
    timer_token = SIGNER_2.sign(link_name)
    return timer_token