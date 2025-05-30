import datetime
import pytz
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


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


def add_get_variables_to_url(base_url: str, params: dict) -> str:
    """
    Adds GET variables (query parameters) to a given URL string.

    Args:
        base_url: The original URL string.
        params: A dictionary where keys are parameter names and values are
                parameter values.

    Returns:
        The URL string with the added GET variables, correctly URL-encoded.
    """
    # filter params
    params = {k: v for k, v in params.items() if v}

    # 1. Parse the original URL into its components
    #    (scheme, netloc, path, params, query, fragment)
    parsed_url = urlparse(base_url)

    # 2. Parse existing query parameters (if any)
    existing_params = parse_qs(parsed_url.query)

    # 3. Merge new parameters with existing ones
    #    Note: parse_qs returns lists for values, so we need to flatten
    #    or ensure new params overwrite existing ones if keys are the same.
    #    For simplicity, we'll overwrite existing keys with new ones.
    merged_params = {}
    for key, value_list in existing_params.items():
        # parse_qs always returns a list, take the first item if exists
        merged_params[key] = value_list[0] if value_list else ''

    # Add/overwrite with new parameters
    merged_params.update(params)

    # 4. Encode the merged parameters into a URL-friendly query string
    #    quote_via=quote_plus handles spaces as '+' which is common for query strings
    #    (as opposed to '%20' for regular path segments)
    # quote_via=None uses default urlencode, which uses %xx for spaces
    encoded_query = urlencode(merged_params)

    # If you specifically want '+' for spaces, use:
    # encoded_query = urlencode(merged_params, quote_via=urllib.parse.quote_plus)

    # 5. Reconstruct the URL with the new query string
    #    urlunparse takes a tuple: (scheme, netloc, path, params, query, fragment)
    new_url = urlunparse(parsed_url._replace(query=encoded_query))
    new_url = f"{new_url}"
    return new_url


if __name__ == '__main__':
    # Example 1: Basic URL with no existing GET variables
    base_url_1 = "https://example.com/page"
    params_1 = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": "30"
    }
    new_url_1 = add_get_variables_to_url(base_url_1, params_1)
    print(f"Original URL 1: {base_url_1}")
    print(f"New URL 1: {new_url_1}\n")

    # Example 2: URL with existing GET variables
    base_url_2 = "https://api.calendly.com/event_types?user=user_uuid_123"
    params_2 = {
        "name": "Jane O'Connell",
        "email": "jane.o'connell@test.co.uk",
        "referrer": "My Website (Version 2.1)"
    }
    new_url_2 = add_get_variables_to_url(base_url_2, params_2)
    print(f"Original URL 2: {base_url_2}")
    print(f"New URL 2: {new_url_2}\n")

    # Example 3: URL with fragment and a special character in name
    base_url_3 = "http://localhost:8000/booking#section-details"
    params_3 = {
        "name": "Alice & Bob",
        "meeting_type": "Discovery Call"
    }
    new_url_3 = add_get_variables_to_url(base_url_3, params_3)
    print(f"Original URL 3: {base_url_3}")
    print(f"New URL 3: {new_url_3}\n")

    # Example 4: Overwriting an existing parameter
    base_url_4 = "https://example.com/search?query=python&page=1"
    params_4 = {
        "page": "2",
        "sort": "date_desc"
    }
    new_url_4 = add_get_variables_to_url(base_url_4, params_4)
    print(f"Original URL 4: {base_url_4}")
    print(f"New URL 4: {new_url_4}\n")

    # Example 5: Empty params dictionary
    base_url_5 = "https://example.com/no_change"
    params_5 = {}
    new_url_5 = add_get_variables_to_url(base_url_5, params_5)
    print(f"Original URL 5: {base_url_5}")
    print(f"New URL 5: {new_url_5}\n")
