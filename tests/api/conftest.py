import pytest
import requests
import uuid
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_BASE_URL = "http://localhost:8000/api/v1"

@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/")

@pytest.fixture(scope="session")
def run_id():
    return str(uuid.uuid4())[:8]

@pytest.fixture(scope="function")
def case_id():
    return str(uuid.uuid4())[:6]


class APIClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries, pool_connections=20, pool_maxsize=20)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def root_url(self) -> str:
        if self._base_url.endswith("/api/v1"):
            return self._base_url[: -len("/api/v1")]
        return self._base_url

    def request(self, method: str, path: str, **kwargs):
        url = f"{self._base_url}{path if path.startswith('/') else '/' + path}"
        timeout = kwargs.pop("timeout", 10)
        return self._session.request(method, url, timeout=timeout, **kwargs)

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self.request("PUT", path, **kwargs)


@pytest.fixture(scope="session")
def api_client(base_url):
    return APIClient(base_url)


@pytest.fixture(scope="session", autouse=True)
def wait_for_api(api_client):
    deadline = time.time() + 45
    last_error = None
    while time.time() < deadline:
        try:
            res = api_client._session.get(f"{api_client.root_url}/docs", timeout=3)
            if res.status_code in (200, 401, 403):
                return
            last_error = f"status={res.status_code} body={res.text[:200]}"
        except Exception as e:
            last_error = str(e)
        time.sleep(1)
    raise RuntimeError(f"API not ready: {last_error}")


@pytest.fixture(scope="session")
def auth_token(api_client, run_id):
    username = f"testuser_{run_id}"
    email = f"{username}@example.com"
    password = "SecurePassword123!"

    user_data = {
        "email": email,
        "username": username,
        "phone": f"13800{run_id[:6]}",
        "address": "123 Test St",
        "password": password,
        "first_name": "Test",
        "last_name": "User",
        "type": "customer"
    }
    api_client.post("/auth/register", json=user_data)

    login_data = {"username": username, "password": password}
    response = api_client.post("/auth/token", data=login_data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
