import random
import os
import sys


from locust import HttpUser, TaskSet, task, between


def topics_generic(l):
    HOT_TOPICS = ["trace", "storage", "lambda",
                  "database", "compute", "network"]
    url_suffix = f"/{random.choice(HOT_TOPICS)}"
    response = l.client.get(url_suffix, name="polyglot_svc")
    print(f'{{"resp_status_code":{response.status_code}}}')
    print(f"Locust instance {os.path.basename(__file__)}")


def topic_aws(l):
    # headers={'X-Requested-With': 'XMLHttpRequest'})
    url_suffix = f"/aws"
    response = l.client.get(
        url_suffix, name="polyglot_svc_observability")
    print(f'{{"resp_status_code":{response.status_code}}}')
    print(f"Running 'polyglot_svc'")


class UserTasks(TaskSet):
    # one can specify tasks like this
    tasks = [topics_generic, topic_aws]


class WebsiteUser(HttpUser):
    wait_time = between(1, 2)
    tasks = [UserTasks]
