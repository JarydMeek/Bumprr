import requests

# Local imports
from config import get_config

def fetch_data(service, path, *, method="GET", params=None, body=None, headers=None, full_path_override=None):
    
    config = get_config()

    default_headers = {
        "User-Agent": "BumprrClient/1.0",
        "Accept": "application/json",
        "X-Api-Key": config[service].get("api_key", ""),
    }

    fullHeaders = {**default_headers, **(headers or {})}

    baseUrl = config[service]["base_url"]

    full_url = f"{baseUrl.rstrip('/')}/api/{config[service].get('version', 'v3')}/{path.lstrip('/')}"

    if full_path_override:
        full_url = f"{baseUrl.rstrip('/')}/{full_path_override.lstrip('/')}"

    response = requests.request(method, full_url, params=params, json=body, headers=fullHeaders)
    response.raise_for_status()

    try:
        return response.json()
    except: 
        return response.text