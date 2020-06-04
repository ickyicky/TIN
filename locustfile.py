import random
import json
from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(5, 9)

    @task
    def list_dir(self):
        self.client.get("/dir")

    @task
    def post_get_file(self):
        number = random.randint(0, 10)
        self.client.post(f"/file/example{number}.txt", b"asd" * 1024 * 1024)  # 1 MB
        self.client.get(f"/file/example{number}.txt")

    def on_start(self):
        response = self.client.post(
            "/authorize",
            json.dumps({"username": "superuser", "password": "AdMiNiStRaToR1@3"}),
            headers={"Content-Type": "application/json"},
        )
        self.client.headers["Authorization"] = response.headers["Authorization"]
