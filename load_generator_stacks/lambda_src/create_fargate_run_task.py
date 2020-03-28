# -*- coding: utf-8 -*-
"""
.. module: get_video_metadata.py
    :Actions: Get
    :copyright: (c) 2020 Mystique.,
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

import json
import logging
import os

import boto3
import botocore
from botocore.exceptions import ClientError

__author__ = 'Mystique'
__email__ = 'miztiik@github'
__version__ = '0.0.1'
__status__ = 'production'


class global_args:
    """
    Global statics
    """
    OWNER = 'Mystique'
    ENVIRONMENT = 'production'
    MODULE_NAME = 'trigger_fargate_run_task'
    LOG_LEVEL = logging.INFO


def set_logging(lv=global_args.LOG_LEVEL):
    '''
    Helper to enable logging
    '''
    logging.basicConfig(level=lv)
    LOGGER = logging.getLogger()
    LOGGER.setLevel(lv)
    return LOGGER


def lambda_handler(event, context):
    # Initialize Logger
    global LOGGER
    LOGGER = set_logging(logging.INFO)
    resp = {'status': False, }

    client = boto3.client('ecs')

    r1 = client.run_task(
        cluster=os.getenv("CLUSTER_NAME"),
        launchType="FARGATE",
        taskDefinition=os.getenv("TASK_DEFINITION"),
        count=int(os.getenv("NO_OF_TASKS")),
        platformVersion='LATEST',
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": json.loads(os.getenv("SUBNETS")),
                "assignPublicIp": "ENABLED"
            }
        },
        startedBy=f"{global_args.OWNER}-Automation"
    )
    LOGGER.info(r1)

    return str(r1)


if __name__ == '__main__':
    lambda_handler({}, {})
