# -*- coding: utf-8 -*-
"""
.. module: get_python_jobs.py
    :Actions: Get 
    :copyright: (c) 2020 Mystique.,
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

# from aws_xray_sdk.core import patch_all
from aws_xray_sdk.core import xray_recorder
import time
import requests
# import boto3
import os
import json
import logging

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
    MODULE_NAME = 'get_video_metadata.py'
    LOG_LEVEL = logging.INFO


def set_logging(lv=global_args.LOG_LEVEL):
    '''
    Helper to enable logging
    '''
    logging.basicConfig(level=lv)
    LOGGER = logging.getLogger()
    LOGGER.setLevel(lv)
    return LOGGER


@xray_recorder.capture('_get_github_jobs')
def _get_github_jobs(skill='python', location='london'):
    '''
    Get Jobs listed in Github
    '''
    BASE_URL = 'https://jobs.github.com/positions.json'
    payload = {
        'skill': skill,
        'location': location
    }
    resp = {}
    try:
        resp = requests.get(BASE_URL, params=payload)
        resp = json.loads(resp.text)
    except requests.exceptions.RequestException as err:
        LOGGER.error(f"ERROR:{str(e)}")
        resp['error_message'] = str(e)

    return resp


@xray_recorder.capture('_get_random_fox')
def _get_random_fox():
    '''
    Get list of random foxes
    '''
    BASE_URL = 'https://randomfox.ca/floof'
    payload = {}
    resp = {}
    try:
        resp = requests.get(BASE_URL, params=payload)
        resp = json.loads(resp.text)
    except requests.exceptions.RequestException as err:
        LOGGER.error(f"ERROR:{str(e)}")
        resp['error_message'] = str(e)
    return resp


@xray_recorder.capture('_get_random_coder_quote')
def _get_random_coder_quote():
    '''
    Get list of random foxes
    '''
    BASE_URL = 'https://programming-quotes-api.herokuapp.com/quotes/random'
    payload = {}
    resp = {}
    try:
        resp = requests.get(BASE_URL, params=payload)
        resp = json.loads(resp.text)
    except requests.exceptions.RequestException as err:
        LOGGER.error(f"ERROR:{str(e)}")
        resp['error_message'] = str(e)
    return resp


@xray_recorder.capture('_get_wiki_url')
def _get_wiki_url(endpoint_url):
    BASE_URL = f'{endpoint_url}/api/mystique'
    payload = {}
    resp = {}
    try:
        resp = requests.get(BASE_URL, params=payload)
        resp = json.loads(resp.text)
    except requests.exceptions.RequestException as err:
        LOGGER.error(f"ERROR:{str(e)}")
        resp['error_message'] = str(e)
    return resp


@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    # Initialize Logger
    global LOGGER
    LOGGER = set_logging(logging.INFO)
    resp = {'status': False, 'jobs_data': ''}

    _get_random_coder_quote
    _get_random_fox()
    if os.getenv('WIKI_API_ENDPOINT'):
        _get_wiki_url(os.getenv('WIKI_API_ENDPOINT'))
    resp = _get_github_jobs()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": resp
        })
    }


if __name__ == '__main__':
    lambda_handler({}, {})
