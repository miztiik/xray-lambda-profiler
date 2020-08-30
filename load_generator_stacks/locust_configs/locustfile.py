import random
import os
import sys

from locust import HttpUser, task, between


class xrayAppTasks(HttpUser):
    @task(2)
    def topics_generic(self):
        HOT_TOPICS = ["trace", "storage", "lambda",
                      "database", "compute", "network"]
        url_suffix = f"/{random.choice(HOT_TOPICS)}"
        response = self.client.get(url_suffix, name="polyglot_svc_generic")
        print(f'{{"resp_status_code":{response.status_code}}}')
        print(f"Locust instance {os.path.basename(__file__)}")

    @task(1)
    def topic_aws(self):
        # headers={'X-Requested-With': 'XMLHttpRequest'})
        url_suffix = f"/aws"
        response = self.client.get(
            url_suffix, name="polyglot_svc_observability_aws")
        print(f'{{"resp_status_code":{response.status_code}}}')
        print(f"Running 'polyglot_svc'")
