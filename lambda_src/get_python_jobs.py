# -*- coding: utf-8 -*-
import json
import logging
import os
import random
import uuid
from time import sleep

import requests
from aws_xray_sdk.core import xray_recorder

import boto3

xray_recorder.configure(service='api_on_lambda', sampling=False)


class global_args:
    """
    Global statics
    """
    OWNER = 'Mystique'
    ENVIRONMENT = 'production'
    MODULE_NAME = 'get_python_jobs.py'
    LOG_LEVEL = logging.INFO


def set_logging(lv=global_args.LOG_LEVEL):
    '''
    Helper to enable logging
    '''
    logging.basicConfig(level=lv)
    LOGGER = logging.getLogger()
    LOGGER.setLevel(lv)
    return LOGGER


def random_sleep(max_seconds=10):
    sleep((random.randint(0, max_seconds) / 10))


def _trigger_excetpion():
    if not random.randint(1, 9) % 3:
        return True
    else:
        return False


def _ddb_put_item(item):
    _ddb = boto3.resource('dynamodb')
    _ddb_table = _ddb.Table(os.environ.get('DDB_TABLE_NAME'))
    item['_id'] = str(uuid.uuid4())
    LOGGER.info(f"DDB_ITEM:{item}")
    response = _ddb_table.put_item(
        Item=item
    )


@xray_recorder.capture('_get_github_jobs')
def _get_github_jobs(skill='python', location='london'):
    BASE_URL = 'https://jobs.github.com/positions.json'
    HOT_SKILLS = ['python', 'angular', 'microservices',
                  'aws', 'ios', 'containers', 'c']
    payload = {
        'skill': random.choice(HOT_SKILLS),
        'location': location
    }
    resp = {}
    try:
        resp = requests.get(BASE_URL, params=payload)
        resp = json.loads(resp.text)
        if _trigger_excetpion():
            raise requests.exceptions.RequestException(
                f"Random Exception Triggered To Simulate Failures, Mystique")
    except requests.exceptions.RequestException as err:
        LOGGER.error(f"ERROR:{str(err)}")
        resp['error_message'] = str(err)

    return resp


@xray_recorder.capture('_get_random_fox')
def _get_random_fox():
    BASE_URL = 'https://randomfox.ca/floof'
    payload = {}
    resp = {}
    try:
        xray_recorder.begin_subsegment('random_sleep')
        random_sleep()
        xray_recorder.end_subsegment()

        resp = requests.get(BASE_URL, params=payload)
        resp = json.loads(resp.text)
    except requests.exceptions.RequestException as err:
        resp['error_message'] = str(err)
    return resp


@xray_recorder.capture('_get_random_coder_quote')
def _get_random_coder_quote():
    BASE_URL = 'https://programming-quotes-api.herokuapp.com/quotes/random'
    payload = {}
    resp = {}
    try:
        xray_recorder.begin_subsegment('random_quotes_trace')
        resp = requests.get(BASE_URL, params=payload)
        resp = json.loads(resp.text)
        xray_recorder.end_subsegment()
    except requests.exceptions.RequestException as err:
        resp['error_message'] = str(err)
    return resp


@xray_recorder.capture('_get_wiki_url')
def _get_wiki_url(endpoint_url):
    BASE_URL = endpoint_url
    payload = {}
    resp = {}
    HOT_TOPICS = ['cholas', 'cheras', 'pandyas',
                  'pallavas', 'sangam_era', 'kural']

    try:
        xray_recorder.put_annotation('PROCESS', '_get_wiki_url')
        resp = requests.get(
            f'{BASE_URL}/{random.choice(HOT_TOPICS)}', params=payload)
        resp = json.loads(resp.text)
        xray_recorder.put_metadata('RESPONSE', resp)
    except requests.exceptions.RequestException as err:
        resp['error_message'] = str(err)
    return resp


@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    global LOGGER
    LOGGER = set_logging(logging.INFO)
    resp = {'status': False, 'jobs_data': ''}

    _get_random_coder_quote()
    _get_random_fox()
    if os.getenv('WIKI_API_ENDPOINT'):
        res = _get_wiki_url(os.getenv('WIKI_API_ENDPOINT'))
        _ddb_put_item(res)
    resp = _get_github_jobs()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": resp
        })
    }
