import datetime
import json
import os
import requests
from dotenv import load_dotenv

from utils.deep_get import deep_get
from ai.llm_gemini import LLmGemini
from utils.misc import add_get_variables_to_url


class MyCalendly:
    def __init__(self, calendly_pat: str = ""):
        self.pat = calendly_pat or os.getenv("CALENDLY_PAT", "")
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        }
        self.user = {}
        self.events = {}
        self.slots = []

        self.event_uri = ""
        self.event_scheduling_url = ""
        self.available_dates = []

        self.initialize()

    @classmethod
    def humanize_dates(cls, dates: list[datetime.date]) -> list[tuple[datetime.date, str]]:
        """
        Converts a list of date objects into a list of (date, humanized_string) tuples.

        - If the date is today, the string is "Today".
        - If the date is tomorrow, the string is "Tomorrow".
        - For other dates in the next 6 days (after tomorrow), the string is "Next [Day Name]".
        - For all other dates, the original date is returned as a string (e.g., "YYYY-MM-DD").
        """
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        spanish_day_names = {
            0: "Lunes",  # Monday (Python's weekday 0)
            1: "Martes",  # Tuesday (Python's weekday 1)
            2: "Miércoles",  # Wednesday (Python's weekday 2)
            3: "Jueves",  # Thursday (Python's weekday 3)
            4: "Viernes",  # Friday (Python's weekday 4)
            5: "Sábado",  # Saturday (Python's weekday 5)
            6: "Domingo"  # Sunday (Python's weekday 6)
        }
        spanish_month_names = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre"
        }

        humanized_list = []
        for d in dates:
            if d == today:
                humanized_list.append((d, "Hoy"))
            elif d == tomorrow:
                humanized_list.append((d, "Mañana"))
            elif today < d <= today + datetime.timedelta(days=7):  # Check for next 6 days (after tomorrow)
                # %A gives the full weekday name (e.g., "Monday")
                weekday_index = d.weekday()
                spanish_day_name = spanish_day_names[weekday_index]
                humanized_list.append((d, f"{spanish_day_name}"))
            else:
                # For dates beyond the "next 7 days" window, or in the past
                day_number = d.day
                month_name_spanish = spanish_month_names[d.month]
                humanized_list.append((d, f"{day_number} de {month_name_spanish}"))
        return humanized_list

    def initialize(self):
        self.api_get_current_user_uri()
        self.events = self.api_get_event_types()
        self.event_uri = deep_get(self.events, 0, "uri", default="")
        self.event_scheduling_url = deep_get(self.events, 0, "scheduling_url", default="NO URL")

        t0 = datetime.datetime.now(datetime.timezone.utc)
        t1 = t0 + datetime.timedelta(hours=4)
        t2 = t0 + datetime.timedelta(days=6)
        self.slots = self.api_get_available_slots(t1, t2)
        self.available_dates = self.humanize_dates([
            datetime.datetime.strptime(string_date, "%Y-%m-%d").date()
            for string_date in
            sorted(list(set([xi["start_time"][:10] for xi in self.slots if xi["status"] == "available"])))
        ])

    def user_uri(self):
        return self.user.get("resource", {}).get("uri", "")

    def event_types(self):
        return self.events

    def api_get_current_user_uri(self):
        """Obtiene el URI del usuario actual."""
        response = requests.get(f"{self.base_url}/users/me", headers=self.headers)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP
        self.user = response.json()
        return self.user_uri()

    def api_get_event_types(self):
        """Obtiene los tipos de evento activos del usuario."""
        params = {"user": self.user_uri(), "active": "true"}
        response = requests.get(f"{self.base_url}/event_types", headers=self.headers, params=params)
        response.raise_for_status()
        self.events = response.json()
        self.events = [
            x for x in self.events.get("collection", [])
            if x.get("active", False)
        ]

        return self.event_types()

    def api_get_available_slots(self, start_date_utc, end_date_utc):
        """
        Obtiene los horarios disponibles para un tipo de evento en un rango de fechas.
        Las fechas deben estar en formato ISO 8601 UTC (ej: "2023-10-27T00:00:00Z")
        """
        et = self.event_types()
        event_type_uri = et[0]["uri"]
        params = {
            "event_type": event_type_uri,
            "start_time": start_date_utc.isoformat().replace("+00:00", "Z"),
            "end_time": end_date_utc.isoformat().replace("+00:00", "Z")
        }
        # print(f"Debug: Requesting availability with params: {params}") # Para depuración
        response = requests.get(f"{self.base_url}/event_type_available_times", headers=self.headers, params=params)
        response.raise_for_status()

        # Filtrar solo los slots que son 'available'
        self.slots = [
            slot for slot in response.json()["collection"]
            if slot.get("status") == "available" and "start_time" in slot
        ]
        return self.slots

    def get_available_dates(self):
        return [dt_human for dt,dt_human in self.available_dates]

    def get_available_times_for_date(self, date_str: str):
        prompt = f"""Dada la fecha DATE='{date_str}' y los siguientes slots SLOTS={self.slots} regresame solamente los horarios disponibles de la fecha DATE que coincidan con el arreglo de SLOTS y regresame la lista de los horarios ordenados en formato JSON con valores tales como '1:30PM' o 11:00AM. Al final solamente retorna la lista sin texto adicional"""
        llm = LLmGemini(api_key=os.environ["GEMINI_APIKEY"])
        ans, _ = llm.get_answer_and_json_response(prompt)
        ans = ans.replace("`", "").replace("json", "")
        json_ans = json.loads(ans)
        return json_ans

    def get_schedule_event_url(self, date_and_time: str, name: str = "", email: str = ""):
        prompt = f"""Dada la fecha y hora en DATETIME='{date_and_time}' y los siguientes slots SLOTS={self.slots} regresame el slot dentro de SLOTS que represente la fecha y hora en DATETIME. Al final solamente retorna el elemento en formato JSON sin texto adicional, en caso de no coincidir, retorna un JSON vacio"""
        llm = LLmGemini(api_key=os.environ["GEMINI_APIKEY"])
        ans, _ = llm.get_answer_and_json_response(prompt)
        ans = ans.replace("`", "").replace("json", "")
        json_ans = json.loads(ans)
        if not json_ans:
            return ""

        url = deep_get(json_ans, "scheduling_url", default="")
        url = add_get_variables_to_url(url, {"name": name, "email": email})
        return url


if __name__ == '__main__':
    load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
    cal = MyCalendly()
    print("Available dates:",cal.get_available_dates())
    print("Available times:",cal.get_available_times_for_date("Mañana"))
    print(cal.get_schedule_event_url("Próximo viernes a las 2:30PM", name="Pedro Mayorga", email="ppmayorga80@gmail.com"))
    cal = MyCalendly()
