import json
import logging
import os
import random
import uuid
from time import sleep

import requests
from aws_xray_sdk.core import patch_all, xray_recorder

import boto3

patch_all()
xray_recorder.configure(service="api_on_lambda", sampling=False)


class global_args:
    LOG_LEVEL = logging.INFO


def set_logging(lv=global_args.LOG_LEVEL):
    '''
    Helper to enable logging
    '''
    logging.basicConfig(level=lv)
    LOGGER = logging.getLogger()
    LOGGER.setLevel(lv)
    return LOGGER


@xray_recorder.capture('SLEEPING_AT_WORK')
def random_sleep(max_seconds=10):
    sleep((random.randint(0, max_seconds) / 10))


def _trigger_exception():
    r = False
    if os.getenv('TRIGGER_RANDOM_FAILURES', False):
        if not random.randint(1, 8) % 2:
            r = True
    return r


def _ddb_put_item(item):
    _ddb = boto3.resource('dynamodb')
    _ddb_table = _ddb.Table(os.environ.get('DDB_TABLE_NAME'))
    item['_id'] = str(uuid.uuid4())
    try:
        _ddb_table.put_item(Item=item)
    except Exception as err:
        xray_recorder.put_annotation("DDB_ERRORS", "True")
        raise


@xray_recorder.capture('_get_github_jobs')
def _get_github_jobs(skill='python', location='london'):
    BASE_URL = 'https://jobs.github.com/positions.json'
    HOT_SKILLS = ['python', 'microservices', 'ios', 'aws', 'containers']
    payload = {
        'skill': random.choice(HOT_SKILLS),
        'location': location
    }
    resp = {
        "statusCode": 501,
        "body":  json.dumps({"message": "Internal Mystical Error"})
    }
    try:
        r1 = requests.get(BASE_URL, params=payload)
        resp["statusCode"] = r1.status_code
        resp["body"] = json.dumps({"message": r1.json()})
    except Exception as err:
        LOGGER.info(f"ERROR:{str(err)}")
        pass
    return resp


@xray_recorder.capture('_get_random_fox')
def _get_random_fox():
    BASE_URL = 'https://randomfox.ca/floof'
    payload = {}
    resp = {}
    try:
        r1 = requests.get(BASE_URL, params=payload)
        resp = r1.json()
    except requests.exceptions.RequestException as err:
        resp = {'error_message': str(err)}
    return resp


@xray_recorder.capture('_get_random_coder_quote')
def _get_random_coder_quote():
    BASE_URL = 'https://programming-quotes-api.herokuapp.com/quotes/random'
    payload = {}
    resp = {}
    try:
        r1 = requests.get(BASE_URL, params=payload)
        resp = r1.json()
    except requests.exceptions.RequestException as err:
        resp = {'error_message': str(err)}
    return resp


@xray_recorder.capture('_get_wiki_url')
def _get_wiki_url(endpoint_url):
    BASE_URL = endpoint_url
    payload = {}
    resp = {"statusCode": 400}
    HOT_TOPICS = ['cholas', 'cheras', 'pandyas',
                  'pallavas', 'sangam_era', 'kural']
    try:
        random_sleep()
        if _trigger_exception():
            xray_recorder.put_annotation("SIMULATED_ERRORS", "True")
            xray_recorder.begin_subsegment("BRITTLE_LEGACY_APP")
            d = xray_recorder.current_subsegment()
            d.put_annotation("SIMULATED_ERRORS_IN_SUBSEGMENT", "True")
            xray_recorder.end_subsegment()
            raise Exception("RANDOM_ERROR: Simulate Mystique Failure")
        r1 = requests.get(
            f'{BASE_URL}/{random.choice(HOT_TOPICS)}', params=payload)
        resp["statusCode"] = r1.status_code
        resp["body"] = json.dumps({"message": r1.json()})
        _ddb_put_item(resp)
        xray_recorder.put_metadata('RESPONSE', resp)
    except Exception as err:
        resp["body"] = json.dumps({"message": str(err)})
    return resp


@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    global LOGGER
    LOGGER = set_logging(logging.INFO)
    resp = {}
    LOGGER.info(_get_random_coder_quote())
    _get_random_fox()

    if os.getenv("WIKI_API_ENDPOINT"):
        r0 = _get_wiki_url(os.getenv("WIKI_API_ENDPOINT"))

    if r0["statusCode"] == 400:
        resp = r0
        LOGGER.info(f"ERROR:{str(resp)}")
    else:
        resp = _get_github_jobs()
    return resp
