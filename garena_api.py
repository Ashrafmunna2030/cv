import requests
import json
import uuid
import time
from typing import Optional, Dict, Any

class GarenaShopAPI:
    """
    Client for Garena Shop endpoints (unofficial).
    """
    BASE_URL = "https://shop.garena.my"

    # Default headers from the provided HTTP requests
    DEFAULT_HEADERS = {
        "Host": "shop.garena.my",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Android"',
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Android WebView";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
        "sec-ch-ua-mobile": "?1",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "mark.via.gp",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://shop.garena.my/?app=100067&channel=202953",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    def __init__(self, cookies: Dict[str, str]):
        """
        :param cookies: Dictionary of cookies (e.g., source, region, mspid2, datadome, _ga, __csrf__, etc.)
        """
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.session.cookies.update(cookies)

    def track_event(self, event: str, session_id: str, payload: Dict[str, Any]) -> requests.Response:
        """
        POST /api/tracker/track – send a tracking event.
        """
        url = f"{self.BASE_URL}/api/tracker/track"
        data = {
            "client_id": 10000,
            "data": [
                {
                    "event": event,
                    "id": str(uuid.uuid4()),
                    "ts": int(time.time()),
                    "payload": payload
                }
            ]
        }
        headers = {"Accept": "*/*", "Content-Type": "application/json"}
        return self.session.post(url, json=data, headers=headers)

    def check_session(self) -> requests.Response:
        """
        GET /api/auth/check_session – verify current session status.
        """
        url = f"{self.BASE_URL}/api/auth/check_session"
        headers = {"Accept": "application/json, text/plain, */*"}
        return self.session.get(url, headers=headers)

    def player_id_login(self, app_id: int, login_id: str) -> requests.Response:
        """
        POST /api/auth/player_id_login – authenticate using a player ID (UID).
        Returns user info including nickname if login is successful.
        """
        url = f"{self.BASE_URL}/api/auth/player_id_login"
        payload = {"app_id": app_id, "login_id": login_id}
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/plain, */*"}
        return self.session.post(url, json=payload, headers=headers)

    def init_pay(self,
                 app_id: int,
                 packed_role_id: int,
                 channel_id: int,
                 service: str = "mb",
                 channel_data: Optional[Dict] = None,
                 revamp_experiment: Optional[Dict] = None,
                 region: str = "MY",
                 language: str = "en") -> requests.Response:
        """
        POST /api/shop/pay/init – initialize a payment.

        :param app_id: Application ID (e.g., 100067 for Free Fire)
        :param packed_role_id: Role ID (0 if not applicable)
        :param channel_id: Payment channel ID (e.g., 221179)
        :param service: Service name (default "mb")
        :param channel_data: Dict with "need_return" and "payment_channel" (default {"need_return": True, "payment_channel": None})
        :param revamp_experiment: Experiment data; if None, built from cookies/mspid2
        :param region: Region code (default "MY")
        :param language: Language code (default "en")
        :return: Response object (expected JSON: {"display_id": "...", "init": {"url": "..."}, "result": "success"})
        """
        url = f"{self.BASE_URL}/api/shop/pay/init"
        params = {"region": region, "language": language}

        if channel_data is None:
            channel_data = {"need_return": True, "payment_channel": None}

        if revamp_experiment is None:
            # Use mspid2 cookie as session_id if present, otherwise generate a UUID
            session_id = self.session.cookies.get("mspid2", str(uuid.uuid4()))
            revamp_experiment = {
                "session_id": session_id,
                "group": "treatment2",
                "service_version": "mshop_frontend_20260421",
                "source": "mb",
                "domain": "shop.garena.my"
            }

        payload = {
            "app_id": app_id,
            "packed_role_id": packed_role_id,
            "channel_id": channel_id,
            "service": service,
            "channel_data": channel_data,
            "revamp_experiment": revamp_experiment
        }

        # CSRF token is expected to be present in cookies (key "__csrf__")
        csrf_token = self.session.cookies.get("__csrf__")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
        }
        if csrf_token:
            headers["x-csrf-token"] = csrf_token

        return self.session.post(url, params=params, json=payload, headers=headers)
