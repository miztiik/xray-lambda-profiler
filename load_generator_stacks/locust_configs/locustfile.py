import random
import os
import sys

from locust import HttpUser, task, TaskSet, between


class xrayAppTasks(TaskSet):
    @task(1)
    def index(self):
        HOT_TOPICS = ["trace", "storage", "lambda",
                      "database", "compute", "network"]
        url_suffix = f"/{random.choice(HOT_TOPICS)}"
        response = self.client.get(url_suffix, name="polyglot_svc")
        print(f'{{"resp_status_code":{response.status_code}}}')
        print(f"Locust instance {os.path.basename(__file__)}")

    @task(2)
    def polyglot_svc(self):
        # headers={'X-Requested-With': 'XMLHttpRequest'})
        url_suffix = f"/aws"
        response = self.client.get(
            url_suffix, name="polyglot_svc_observability")
        print(f'{{"resp_status_code":{response.status_code}}}')
        print(f"Running 'polyglot_svc'")


class WebsiteUser(HttpUser):
    tasks = [xrayAppTasks]
    wait_time = between(1, 2)
