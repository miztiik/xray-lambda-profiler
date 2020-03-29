#!/usr/bin/env python3

from aws_cdk import core

from app_stacks.get_wiki_url_stack import getWikiUrlStack
from app_stacks.vpc_stack import VpcStack
from app_stacks.wiki_api_stack import wikiApiStack
from load_generator_stacks.locust_load_generator import LocustLoadGeneratorStack
from xray_lambda_profiler.xray_lambda_profiler_stack import XrayLambdaProfilerStack

app = core.App()
# VPC Stack for hosting EC2 & Other resources
vpc_stack = VpcStack(app, "get-wiki-url-vpc-stack",
                     description="VPC Stack for hosting EC2 & Other resources"
                     )

# WIKI App: HTTP EndPoint on EC2 Stack
get_wiki_url_stack = getWikiUrlStack(
    app, "get-wiki-url-stack", vpc=vpc_stack.vpc,
    description="WIKI App: HTTP EndPoint on EC2 Stack"
)

# Deploy the API GW for WIKI App, with the HTTP Endpoint Integration
get_wiki_url_api_stack = wikiApiStack(app, "get-wiki-url-api-stack",
                                      wiki_api_endpoint=get_wiki_url_stack.web_app_server.instance_public_ip,
                                      description="Deploy the API GW for WIKI App, with the HTTP Endpoint Integration"
                                      )

# Deploy the AWS XRay Profiler, with the Lambda Integrated with APIGW
xray_profiler_stack = XrayLambdaProfilerStack(
    app, "xray-lambda-profiler",
    wiki_api_endpoint=get_wiki_url_api_stack.wiki_url_path_00.url,
    description="Deploy the AWS XRay Profiler, with the Lambda Integrated with APIGW"
)

# Deploy Load Testing Tool - Locust Stack
locust_stack = LocustLoadGeneratorStack(
    app, f"locust-load-generator-stack",
    vpc=vpc_stack.vpc,
    url=xray_profiler_stack.polyglot_svc_api_resource_01.url,
    LOAD_PARAMS={
        "NO_OF_CLIENTS": "10",
        "HATCH_RATE": "1",
        "RUN_TIME": "10",
        "NO_OF_TASKS": "2"
    },
    description="Deploy Load Testing Tool - Locust Stack"
)

# Stack Level Tagging
core.Tag.add(app, key="Owner",
             value=app.node.try_get_context('owner'))
core.Tag.add(app, key="OwnerProfile",
             value=app.node.try_get_context('github_profile'))
core.Tag.add(app, key="GithubRepo",
             value=app.node.try_get_context('github_repo_url'))
core.Tag.add(app, key="ToKnowMore",
             value=app.node.try_get_context('youtube_profile'))

app.synth()
