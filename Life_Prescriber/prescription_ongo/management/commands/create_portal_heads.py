import os
from django.core.management.base import BaseCommand
from prescription_ongo.models import ClinicUser


class Command(BaseCommand):
    help = "Create the initial head user for each portal if they do not already exist."

    def handle(self, *args, **options):
        self._create(
            username=os.getenv("HOSPITAL_HEAD_USERNAME", "hospital_head"),
            email=os.getenv("HOSPITAL_HEAD_EMAIL", "hospital@lifeprescriber.com"),
            first_name=os.getenv("HOSPITAL_HEAD_FIRST_NAME", "Hospital"),
            last_name=os.getenv("HOSPITAL_HEAD_LAST_NAME", "Head"),
            designation=os.getenv("HOSPITAL_HEAD_DESIGNATION", "Doctor"),
            institution=os.getenv("HOSPITAL_HEAD_INSTITUTION", "General Hospital"),
            portal_type="hospital",
            password=os.getenv("HOSPITAL_HEAD_PASSWORD", ""),
        )
        self._create(
            username=os.getenv("PHARMACY_HEAD_USERNAME", "pharmacy_head"),
            email=os.getenv("PHARMACY_HEAD_EMAIL", "pharmacy@lifeprescriber.com"),
            first_name=os.getenv("PHARMACY_HEAD_FIRST_NAME", "Pharmacy"),
            last_name=os.getenv("PHARMACY_HEAD_LAST_NAME", "Head"),
            designation=os.getenv("PHARMACY_HEAD_DESIGNATION", "Pharmacist"),
            institution=os.getenv("PHARMACY_HEAD_INSTITUTION", "Central Pharmacy"),
            portal_type="pharmacy",
            password=os.getenv("PHARMACY_HEAD_PASSWORD", ""),
        )
        # Public demo accounts — fixed credentials shown in portfolio
        self._create(
            username="hospital_head",
            email="hospital@lifeprescriber.com",
            first_name="Demo",
            last_name="Hospital",
            designation="Doctor",
            institution="General Hospital",
            portal_type="hospital",
            password="sitdownhere",
        )
        self._create(
            username="pharmacy_head",
            email="pharmacy@lifeprescriber.com",
            first_name="Demo",
            last_name="Pharmacy",
            designation="Pharmacist",
            institution="Central Pharmacy",
            portal_type="pharmacy",
            password="sitdownhere",
        )

    def _create(self, username, email, first_name, last_name,
                designation, institution, portal_type, password):
        if ClinicUser.objects.filter(username=username).exists():
            self.stdout.write(f"[skip] {portal_type} head '{username}' already exists.")
            return
        if not password:
            self.stderr.write(
                f"[error] No password set for {portal_type} head. "
                f"Set the env var {'HOSPITAL' if portal_type == 'hospital' else 'PHARMACY'}_HEAD_PASSWORD."
            )
            return
        ClinicUser.objects.create_user(
            username=username,
            email=email,
            first_name=first_name.capitalize(),
            last_name=last_name.capitalize(),
            designation=designation.capitalize(),
            medical_institution=institution,
            portal_type=portal_type,
            role="head",
            password=password,
        )
        self.stdout.write(f"[created] {portal_type} head '{username}' at {institution}.")
