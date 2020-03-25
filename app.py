#!/usr/bin/env python3

from aws_cdk import core

from xray_lambda_profiler.wiki_api_stack import wikiApiStack
from xray_lambda_profiler.xray_lambda_profiler_stack import XrayLambdaProfilerStack
from app_stacks.vpc_stack import VpcStack
from app_stacks.get_wiki_url_stack import getWikiUrlStack

from load_generator_stacks.locust_load_generator import LocustLoadGeneratorStack

app = core.App()
# VPC Stack for hosting EC2 & Other resources
vpc_stack = VpcStack(app, "get-wiki-url-stack-vpc-stack")

# HTTP EndPoint on EC2 Stack
get_wiki_url_stack = getWikiUrlStack(
    app, "get-wiki-url-stack", vpc=vpc_stack.vpc)

# Deploy the API GW, with the HTTP Endpoint Integration
api_gw_for_xray_profiler_stack = wikiApiStack(app, "api-gw-for-xray-profiler",
                                              wiki_api_endpoint=get_wiki_url_stack.web_app_server.instance_public_ip
                                              )

# Deploy the AWS XRay Profiler, with the Lambda Integrated with APIGW
xray_profiler_stack = XrayLambdaProfilerStack(
    app, "xray-lambda-profiler",
    wiki_api_endpoint=api_gw_for_xray_profiler_stack.wiki_url_path_00.url
)

# Deploy Load Testing Tool - Locust Stack
locust_stack = LocustLoadGeneratorStack(
    app, f"locust-load-generator-stack",
    vpc=vpc_stack.vpc,
    url=xray_profiler_stack.hot_jobs_api_resource.url,
    LOAD_PARAMS={
        "NO_OF_CLIENTS": "200",
        "HATCH_RATE": "10",
        "RUN_TIME": "100",
    }
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
