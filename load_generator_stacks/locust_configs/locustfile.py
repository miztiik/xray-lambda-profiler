import random
import os
import sys

from locust import HttpUser, TaskSet, between, task

class xrayAppTasks(TaskSet):
    @task(1)
    def index(self):
        HOT_TOPICS = ["trace", "storage", "lambda",
                      "database", "compute", "network"]
        url_suffix = f"/{random.choice(HOT_TOPICS)}"
        self.client.get(url_suffix, name="polyglot_svc")
        print(f"Locust instance {os.path.basename(__file__)}")

    @task(2)
    def polyglot_svc(self):
        # headers={'X-Requested-With': 'XMLHttpRequest'})
        url_suffix = f"/aws"
        self.client.get(url_suffix, name="polyglot_svc_observability")
        print(f"Running 'polyglot_svc'")


class WebsiteUser(HttpUser):
    task_set = xrayAppTasks
    wait_time = between(1, 2)
