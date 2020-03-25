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
    def get_hot_jobs(self):
        # Add containers
        # headers={'X-Requested-With': 'XMLHttpRequest'})
        url_suffix = f"/"
        # Statistics for these requests will be grouped under: hot_jobs
        self.client.get(url_suffix, name="hot_jobs")
        print(f"Running 'get_hot_jobs'")


class WebsiteUser(HttpLocust):
    task_set = xrayAppTasks
    wait_time = between(1, 2)
