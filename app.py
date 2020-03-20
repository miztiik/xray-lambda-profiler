#!/usr/bin/env python3

from aws_cdk import core

from xray_lambda_profiler.xray_lambda_profiler_stack import XrayLambdaProfilerStack


app = core.App()
XrayLambdaProfilerStack(app, "xray-lambda-profiler")

app.synth()
