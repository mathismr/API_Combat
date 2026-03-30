from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from http.client import HTTPResponse
from typing import Dict
import json
import socket

from fastapi import HTTPException

from app.core.config import settings

MONSTERS_API_URL = (
    f"{settings.MONSTERS_API_BASE_URL}:{settings.MONSTERS_API_PORT}/api/monsters"
)


def fetch_api(endpoint: str, uuid: str) -> Dict | HTTPException:
    match endpoint:
        case "monster":
            url = f"{MONSTERS_API_URL}/get/{uuid}"
        case "skill":
            url = f"{MONSTERS_API_URL}/skills/get/{uuid}"
        case "turn":
            url = f"http://localhost:8000/api/turns/get/{uuid}"
        case _:
            return {"error": "Invalid endpoint"}

    try:
        response = urlopen(url, timeout=5)
        response_json = json.loads(response.read().decode("utf-8"))
        return response_json
    except HTTPError as e:
        try:
            response_dict = json.loads(e.read().decode("utf-8"))
        except Exception:
            response_dict = {"status": getattr(e, "code", 500), "detail": str(e)}
        raise HTTPException(
            status_code=response_dict.get("status", 500), detail=response_dict
        )
    except (URLError, ConnectionRefusedError, socket.timeout, OSError) as e:
        detail = (
            f"Cannot reach Monsters API at {url}. "
            "Check MONSTERS_API_FULL_URL or run the monsters service. "
            f"Original error: {e}"
        )
        raise HTTPException(status_code=502, detail=detail)
