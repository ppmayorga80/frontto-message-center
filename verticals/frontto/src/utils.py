from datetime import datetime
import pytz

def fix_phone(to):
    # for now only fix mexico phone numbers
    if to.startswith("52"):
        if len(to)==13 and to[2]=="1":
            to = to[:2]+to[-10:]
    return to



def curdt(tz="America/Mexico_City"):
    # Define the time zone for Mexico City
    mytz = pytz.timezone(tz)

    # Get the current date and time in that time zone
    current_datetime = datetime.now(mytz)

    return current_datetime

