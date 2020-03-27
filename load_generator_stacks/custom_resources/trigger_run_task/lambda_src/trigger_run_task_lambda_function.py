# -*- coding: utf-8 -*-

import json
from datetime import datetime
import logging as LOGGGER
import os


import boto3
import cfnresponse


def lambda_handler(event, context):
    LOGGGER.getLogger().setLevel(LOGGGER.INFO)

    # This needs to change if there are to be multiple resources in the same stack
    physical_id = 'TriggerFargateRunTaskToGenerateLocustLoad'

    try:
        LOGGGER.info(f'Input event: {event}')

        # Check if this is a Create and we're failing Creates
        if event['RequestType'] == 'Create' and event['ResourceProperties'].get('FailCreate', False) or event['RequestType'] == 'Delete':
            LOGGGER.info('Create failure requested by SINGLEtonneeeeee')
            raise RuntimeError('Create failure requested')

        # Do the thing
        message = event['ResourceProperties']['Message']

        # MINE
        client = boto3.client('lambda')
        data = {}
        response = client.invoke(FunctionName=os.getenv("RUN_TASK_FN_ARN"),
                                 InvocationType='Event',
                                 Payload=json.dumps(data))

        try:
            triggerResponse = response.get('StatusCode')
            LOGGGER.info(f"Response from Boto: {response}")
            LOGGGER.info(f"Payload from Boto: {response['Payload'].read()}")
            LOGGGER.info(
                f"Payload from Boto: {response['Payload'].read().decode()}")
        except Exception as err:
            LOGGGER.exception(e)

        # MINE

        attributes = {
            'Response': f"Message recieved from function. StatusCode: {triggerResponse}"
        }

        cfnresponse.send(event, context, cfnresponse.SUCCESS,
                         attributes, physical_id)
    except Exception as e:
        LOGGGER.exception(e)
        # cfnresponse's error message is always "see CloudWatch"
        cfnresponse.send(event, context, cfnresponse.FAILED, {}, physical_id)
