import random
import sys

from locust import HttpLocust, TaskSet, between, task


def get_random_page(locust):
    ROOT_URL = "https://aws.amazon.com/blogs/compute/tag/s3/"
    domain = random.choice(["compute", "database", "security"])
    tag_name = random.choice(["s3", "iam"])
    url_suffix = f"/{domain}/tag/{tag_name}"
    locust.client.get(url_suffix)


def get_security_opensource(locust):
    locust.client.get(
        "https://aws.amazon.com/blogs/opensource/category/serverless")
    locust.client.get(
        "https://aws.amazon.com/blogs/containers/the-role-of-aws-fargate-in-the-container-world")
    locust.client.get(
        "https://aws.amazon.com/blogs/containers/category/compute/amazon-kubernetes-service")


def get_year_page(locust):
    ROOT_URL = "https://aws.amazon.com/about-aws/whats-new"
    # Generate a list with 'start', 'end' & increment
    aws_years = list(range(2004, 2021, 1))
    year_id = random.choice(aws_years)  # Choose a random number from list
    url_suffix = f"/{year_id}"
    locust.client.get(url_suffix)


class MyTaskSet(TaskSet):
    tasks = {get_random_page: 2, get_security_opensource: 1}


class MyLocust(HttpLocust):
    task_set = MyTaskSet
    wait_time = between(1, 2)
