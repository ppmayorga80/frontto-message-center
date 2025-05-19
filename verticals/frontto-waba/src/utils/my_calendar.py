import datetime
import json
import os
import requests
from dotenv import load_dotenv


class MyCalendar:
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

    def user_uri(self):
        return self.user.get("resource", {}).get("uri", "")

    def event_types(self):
        return self.events

    def test(self):
        self.api_get_current_user_uri()
        x = self.api_get_event_types()
        print(json.dumps(x, indent=4))

        t0 = datetime.datetime.now(datetime.timezone.utc)
        t1 = t0 + datetime.timedelta(hours=4)
        t2 = t0 + datetime.timedelta(days=6)
        x = self.api_get_available_slots(t1, t2)
        print(json.dumps(x, indent=4))

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

    def api_schedule_event(self, name: str, email: str):
        pass


if __name__ == '__main__':
    load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
    cal = MyCalendar()
    cal.test()
