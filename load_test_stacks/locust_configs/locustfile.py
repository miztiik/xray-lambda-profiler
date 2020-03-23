import random
import sys

from locust import HttpLocust, TaskSet, between, task


def get_hot_jobs(locust):
    url_suffix = f"/"
    # Statistics for these requests will be grouped under: hot_jobs
    locust.client.get(url_suffix, name="hot_jobs")


class MyTaskSet(TaskSet):
    tasks = {get_hot_jobs: 2}


class MyLocust(HttpLocust):
    task_set = MyTaskSet
    wait_time = between(1, 2)
