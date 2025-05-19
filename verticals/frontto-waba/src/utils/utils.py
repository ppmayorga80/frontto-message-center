import datetime
import pytz


def fix_phone(to):
    # for now only fix mexico phone numbers
    if to.startswith("52"):
        if len(to) == 13 and to[2] == "1":
            to = to[:2] + to[-10:]
    return to


def cur_dt(tz="America/Mexico_City"):
    # Define the time zone for Mexico City
    mytz = pytz.timezone(tz)
    # Get the current date and time in that time zone
    current_datetime = datetime.datetime.now(mytz)

    return current_datetime


def format_utc_to_local(utc_dt_str, local_tz_name="America/Mexico_City"):
    """Convierte una cadena de fecha UTC a una fecha y hora local legible."""
    if not isinstance(utc_dt_str, str):
        utc_dt_str = f"{utc_dt_str}"

    try:
        utc_dt = datetime.datetime.fromisoformat(utc_dt_str.replace("Z", "+00:00"))
        local_tz = pytz.timezone(local_tz_name)
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime("%Y-%m-%d %I:%M %p %Z")  # Formato más amigable
    except Exception as e:
        print(f"Error formateando fecha {utc_dt_str}: {e}")
        return utc_dt_str  # Devuelve original si hay error


if __name__ == '__main__':
    x = cur_dt()
    # x = datetime.datetime.now(datetime.timezone.utc)

    fx = format_utc_to_local(x)

    print(type(x))
    print(x)
    print(type(fx))
    print(fx)
