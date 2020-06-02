import pytest
import requests
import json
import os


class Client:
    def __init__(self, api_url):
        self.session = requests.Session()
        self.api_url = api_url

    def post(self, path, data=b"", headers={}):
        return self.session.post(
            os.path.join(self.api_url, path),
            data,
            headers=dict(self.session.headers, **headers),
            verify=False,
        )

    def patch(self, path, data=b"", headers={}):
        return self.session.patch(
            os.path.join(self.api_url, path),
            data,
            headers=dict(self.session.headers, **headers),
            verify=False,
        )

    def put(self, path, data=b"", headers={}):
        return self.session.put(
            os.path.join(self.api_url, path),
            data,
            headers=dict(self.session.headers, **headers),
            verify=False,
        )

    def delete(self, path, headers={}):
        return self.session.delete(
            os.path.join(self.api_url, path),
            headers=dict(self.session.headers, **headers),
            verify=False,
        )

    def get(self, path, headers={}):
        return self.session.get(
            os.path.join(self.api_url, path),
            headers=dict(self.session.headers, **headers),
            verify=False,
        )


class APIClient(Client):
    AUTHORIZATION_PATH = "authorize"
    JSON_HEADER = {"Content-Type": "application/json"}
    USERNAME = "superuser"
    PASSWORD = "AdMiNiStRaToR1@3"

    def set_token(self, token):
        self.session.headers["Authorization"] = token

    def authorize(self, username=None, password=None):
        payload = {
            "username": username or self.USERNAME,
            "password": password or self.PASSWORD,
        }

        response = self.post(
            self.AUTHORIZATION_PATH, json.dumps(payload), headers=self.JSON_HEADER
        )
        assert response.status_code == 200
        self.set_token(response.headers["Authorization"])
        return response


@pytest.fixture
def client():
    api_url = "https://0.0.0.0:12345"
    return APIClient(api_url)


@pytest.fixture
def config():
    with open("/app/conf/config.json") as f:
        return json.loads(f.read())
