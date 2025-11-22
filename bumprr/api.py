import requests

# Local imports
from config import get_config

def fetch_data(service, path, *, method="GET", params=None, body=None, headers=None):
    
    config = get_config()

    default_headers = {
        "User-Agent": "BumprrClient/1.0",
        "Accept": "application/json",
        "X-Api-Key": config[service].get("api_key", ""),
    }

    baseUrl = config[service]["base_url"]

    full_url = f"{baseUrl.rstrip('/')}/{path.lstrip('/')}"

    response = requests.get(full_url, params=params, json=body, headers=headers, method=method)
    response.raise_for_status()
    return response.json()