from datetime import datetime
from zoneinfo import ZoneInfo


def now():

    # Zona horaria de Ciudad de México
    cdmx_tz = ZoneInfo("America/Mexico_City")

    # Fecha y hora actual en esa zona
    now_cdmx = datetime.now(cdmx_tz)

    # Formato deseado
    fmt = now_cdmx.strftime("%Y-%m-%d %H:%M:%S")

    return str(fmt)
