import random
import os
import sys

from locust import HttpLocust, TaskSet, between, task


class xrayAppTasks(TaskSet):
    @task(1)
    def index(self):
        self.client.get("/")
        print(f"Locust instance {os.path.basename(__file__)}")
        pass

    @task(2)
    def polyglot_svc(self):
        # Add containers
        # headers={'X-Requested-With': 'XMLHttpRequest'})
        url_suffix = f"/"
        # Statistics for these requests will be grouped under: hot_jobs
        self.client.get(url_suffix, name="polyglot_svc")
        print(f"Running 'polyglot_svc'")


class WebsiteUser(HttpLocust):
    task_set = xrayAppTasks
    wait_time = between(1, 2)
