#!/usr/bin/env python3

from aws_cdk import core

from xray_lambda_profiler.xray_lambda_profiler_stack import XrayLambdaProfilerStack
from app_stacks.vpc_stack import VpcStack
from app_stacks.get_wiki_url_stack import getWikiUrlStack

app = core.App()
# VPC Stack for hosting EC2 & Other resources
vpc_stack = VpcStack(app, "get_wiki_url_stack_vpc_stack")

# HTTP EndPoint on EC2 Stack
get_wiki_url_stack = getWikiUrlStack(
    app, "get_wiki_url_stack", vpc=vpc_stack.vpc)

xray_profiler_stack = XrayLambdaProfilerStack(
    app, "xray-lambda-profiler", wiki_api_endpoint=get_wiki_url_stack.web_app_server.public_ip)


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
