import json
import os
import random
import uuid
from time import sleep

import requests
from aws_xray_sdk.core import patch_all, xray_recorder

import boto3

patch_all()
xray_recorder.configure(service="api_on_lambda", sampling=False)


@xray_recorder.capture('LATENCY_GENERATING_SVC')
def random_sleep(max_seconds=10):
    xray_recorder.put_annotation("RANDMOMLY_SLEEP_AT_WORK", "True")
    sleep((random.randint(0, max_seconds) / 10))


def _trigger_exception():
    r = False
    if os.getenv('TRIGGER_RANDOM_FAILURES', False):
        if not random.randint(1, 8) % 3:
            r = True
    return r


def _ddb_put_item(item):
    _ddb = boto3.resource('dynamodb')
    _ddb_table = _ddb.Table(os.environ.get('DDB_TABLE_NAME'))
    item['_id'] = str(uuid.uuid4())
    try:
        _ddb_table.put_item(Item=item)
    except Exception as e:
        xray_recorder.put_annotation("DDB_ERROR", "True")
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
        "body":  {"message": "Internal Mystical Error"}
    }
    try:
        print(
            f"Git_resp:{requests.get(BASE_URL, params=payload).status_code}")
    except Exception as er:
        print(f"{str(er)}")
    return resp


@xray_recorder.capture('_get_random_fox')
def _get_random_fox():
    BASE_URL = 'https://randomfox.ca/floof'
    payload = {}
    resp = {}
    try:
        requests.get(BASE_URL, params=payload)
    except requests.exceptions.RequestException as err:
        resp = {'error_message': str(err)}
    return resp


@xray_recorder.capture('_get_random_coder_quote')
def _get_random_coder_quote():
    BASE_URL = 'https://programming-quotes-api.herokuapp.com/quotes/random'
    payload = {}
    resp = {}
    try:
        resp = json.dumps(requests.get(BASE_URL, params=payload).json())
    except requests.exceptions.RequestException as e:
        resp = {'error_message': str(e)}
    return resp


@xray_recorder.capture('_get_wiki_url')
def _get_wiki_url(_url, q):
    BASE_URL = _url
    payload = {}
    resp = {"statusCode": 400}
    HOT_TOPICS = ['cholas', 'cheras', 'pandyas',
                  'pallavas', 'sangam_era', 'kural']
    if q:
        q = q.split('/')[-1]
    else:
        q = random.choice(HOT_TOPICS)

    try:
        random_sleep()
        if _trigger_exception():
            xray_recorder.put_annotation("SIMULATED_ERRORS", "True")
            xray_recorder.begin_subsegment("BRITTLE_LEGACY_APP")
            d = xray_recorder.current_subsegment()
            d.put_annotation("MANUALLY_TRIGGERRED_IN_SUBSEGMENT", "True")
            xray_recorder.end_subsegment()
            raise Exception("RANDOM_ERROR: Simulate Mystique Failure")
        r1 = requests.get(
            f'{BASE_URL}/{q}', params=payload)
        xray_recorder.put_metadata('RESPONSE', resp)
        resp["statusCode"] = r1.status_code
        z = r1.json()
        resp["body"] = json.dumps({"message": z["body"]["message"]})
        _ddb_put_item(resp)
    except Exception as e:
        resp["body"] = json.dumps({"message": str(e)})
    return resp


@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    resp = {}
    print(event)
    print(_get_random_coder_quote())
    _get_random_fox()
    r1 = _get_github_jobs()

    if os.getenv("WIKI_API_ENDPOINT"):
        q = event.get('path')
        r2 = _get_wiki_url(os.getenv("WIKI_API_ENDPOINT"), q)
        r2.pop("_id", None)
    if r2["statusCode"] == 400:
        resp = r1
    elif r1["statusCode"] == 501:
        resp = r2
    print(f"{resp}")
    return resp
