from urllib.request import urlopen, HTTPError
from http.client import HTTPResponse
from typing import Dict
import json

from app.core.config import settings

MONSTERS_API_URL = f"{settings.MONSTERS_API_BASE_URL}:{settings.MONSTERS_API_PORT}/api/monsters"

def monster_api_rq(endpoint: str, uuid: str) -> Dict:
    match endpoint:
        case "monster":
            url = f"{MONSTERS_API_URL}/get/{uuid}"
        case "skill":
            url = f"{MONSTERS_API_URL}/skills/get/{uuid}"
        case _:
            return {"error": "Invalid endpoint"}

    try:
        response: HTTPResponse = urlopen(url)
        response_json = json.loads(response.read().decode("utf-8"))
        return response_json
    except HTTPError as e:
        return json.loads(e.read().decode("utf-8"))
