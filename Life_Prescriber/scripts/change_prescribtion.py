from prescription_ongo.models import Prescribe, Patient
from datetime import datetime, time, timedelta
import math

def run(*args):
    drug_name = input("Enter drug name: ")
    username = input("Enter patient username: ")
    get_patient = Patient.objects.filter(
        username=username,
    ).first()
    new_no_of_times_per_day = int(input("Enter new number of time per day: "))
    new_no_of_tablets_per_use = int(input("Enter dose: "))

    prescription = Prescribe.objects.filter(
        drug_name=drug_name.lower(),
        prescribed_user=get_patient,
    ).first()

    if not prescription:
        print(f"prescrition with drug name {drug_name} is not found.")
        return
    
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






    # get_current_time = time(12, 55, 0)
    # all_prescription_objects = Prescribe.objects.filter(
    #     prescribe_time__lte=get_current_time, 
    # ) & Prescribe.objects.filter(
    #     first_time__gte=get_current_time,
    # ) & Prescribe.objects.filter(
    #     total_tablets__gte=0,
    # )
    # for prescription_object in all_prescription_objects:
    #     prescribe_time = prescription_object.prescribe_time
    #     first_time  = prescription_object.first_time
    #     # calculate the next time these prescribe time would be triggered
    #     hours_to_add = 24 // prescription_object.no_of_times_per_day
    #     current_datetime = datetime.now()
    #     prescribe_time = datetime.combine(current_datetime, prescribe_time)
    #     first_time = datetime.combine(current_datetime, first_time)
    #     prescribe_time = prescribe_time + timedelta(hours=hours_to_add)
    #     first_time = first_time + timedelta(hours=hours_to_add)
    #     print(prescribe_time.time(), first_time.time())
