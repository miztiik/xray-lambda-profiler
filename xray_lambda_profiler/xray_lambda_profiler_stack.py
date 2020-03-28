from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_cloudwatch as _cloudwatch
from aws_cdk import aws_cloudwatch_actions as _cw_actions
from aws_cdk import aws_dynamodb as _dynamodb
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as _sns
from aws_cdk import aws_sns_subscriptions as _subs
from aws_cdk import core


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = 'MystiqueAutomation'
    ENVIRONMENT = 'production'
    REPO_NAME = 'xray-lambda-profiler'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    VERSION = '2020_03_28'
    POLYGLOT_SUPPORT_EMAIL = 'mystique@example.com'


class XrayLambdaProfilerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, wiki_api_endpoint, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # DynamodDB Table(TODO:Create re-usable data model):
        queries_table = _dynamodb.Table(self, "queriesDataTable",
                                        partition_key=_dynamodb.Attribute(
                                            name="_id", type=_dynamodb.AttributeType.STRING)
                                        )

        # Create AWS XRay Layer
        aws_xray_layer = _lambda.LayerVersion(self, 'awsXrayLayer',
                                              code=_lambda.Code.from_asset(
                                                  'lambda_src/layer_code/aws_xray_python_37.zip'),
                                              compatible_runtimes=[
                                                  _lambda.Runtime.PYTHON_3_7,
                                                  _lambda.Runtime.PYTHON_3_8
                                              ],
                                              license=f'Mystique LambdaLayer of AWS XRay, Refer to AWS for license.',
                                              description='Layer to trace AWS Lamba Calls'
                                              )

        # Create Requests Layer
        requests_layer = _lambda.LayerVersion(self, 'requestsLayer',
                                              code=_lambda.Code.from_asset(
                                                    'lambda_src/layer_code/requests_python_37.zip'),
                                              compatible_runtimes=[
                                                  _lambda.Runtime.PYTHON_3_7,
                                                  _lambda.Runtime.PYTHON_3_8
                                              ],
                                              description='Python requests Layer to make HTTP calls'
                                              )

        # Defines an AWS Lambda resource
        with open("lambda_src/polyglot_strangler_fig_svc.py", encoding="utf8") as fp:
            polyglot_svc_fn_handler_code = fp.read()

        polyglot_svc_fn = _lambda.Function(
            self,
            id='polyglotStranglerFigService',
            function_name="polyglot_svc_fn",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(
                polyglot_svc_fn_handler_code),
            handler='index.lambda_handler',
            timeout=core.Duration.seconds(59),
            environment={
                'LD_LIBRARY_PATH': '/opt/python',
                'WIKI_API_ENDPOINT': wiki_api_endpoint,
                'DDB_TABLE_NAME': queries_table.table_name,
                'TRIGGER_RANDOM_FAILURES': 'True'
            },
            layers=[aws_xray_layer, requests_layer],
            tracing=_lambda.Tracing.ACTIVE
        )
        # Grant Lambda permissions to write to Dynamodb
        queries_table.grant_read_write_data(polyglot_svc_fn)

        ##### PUBLISH TO API GW ######

        # Enable AWS XRay Tracing at API GW
        polyglot_svc_api_stage_options = _apigw.StageOptions(
            stage_name="myst",
            data_trace_enabled=True,
            tracing_enabled=True
        )

        # Create API Gateway
        api_01 = _apigw.RestApi(self, 'polglotApiEndpoint',
                                rest_api_name='mystique-xray-tracer-api',
                                deploy_options=polyglot_svc_api_stage_options)

        v1 = api_01.root.add_resource("polyglot_svc")

        # Add resource for HTTP Endpoint: API Hosted on EC2
        polyglot_svc_api_resource_00 = v1.add_resource('wiki')
        self.polyglot_svc_api_resource_01 = polyglot_svc_api_resource_00.add_resource(
            '{query}')

        polyglot_svc_api_lambda_integration = _apigw.LambdaIntegration(
            handler=polyglot_svc_fn,
            proxy=True,
            integration_responses=[{"statusCode": "200"}],
            request_parameters={
                "integration.request.path.query": "method.request.path.query"}
        )

        self.polyglot_svc_api_resource_01.add_method(
            http_method="GET",
            integration=polyglot_svc_api_lambda_integration,
            method_responses=[{"statusCode": "200"}],
            request_parameters={
                'method.request.header.Content-Type': False,
                'method.request.path.query': True
            }
        )

        ##### MONITORING ######

        # Now let us create alarms for our Lambda Function
        # alarm is raised there are more than 5(threshold) of the measured metrics in two(datapoint) of the last three seconds(evaluation):
        # Period=60Seconds, Eval=3, Threshold=5
        # metric_errors(): How many invocations of this Lambda fail.
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_lambda/Function.html
        polyglot_svc_fn_error_alarm = polyglot_svc_fn.metric_errors().create_alarm(self, "polglotSvcAlarm",
                                                                                   alarm_name="polyglot_svc_fn_error_alarm",
                                                                                   threshold=10,
                                                                                   evaluation_periods=5,
                                                                                   period=core.Duration.minutes(
                                                                                       1),
                                                                                   treat_missing_data=_cloudwatch.TreatMissingData.IGNORE
                                                                                   )
        # SNS For Alerts for Polyglot Service
        polyglot_svc_support_topic = _sns.Topic(self, "polyglotSvcTopic",
                                                display_name="PolyglotSvc",
                                                topic_name="polyglotSvcSupportTopic"
                                                )

        # Subscribe Polyglot Service Team Email to topic
        polyglot_svc_support_topic.add_subscription(
            _subs.EmailSubscription(global_args.POLYGLOT_SUPPORT_EMAIL))

        # Add the topic to the Alarm
        polyglot_svc_fn_error_alarm.add_alarm_action(
            _cw_actions.SnsAction(polyglot_svc_support_topic))

        # Create CloudWatch Dashboard for Polyglot Service Team
        polyglot_svc_dashboard = _cloudwatch.Dashboard(self,
                                                       id="polyglotSvcDashboard",
                                                       dashboard_name="Polyglot-Svc"
                                                       )
        """
        polyglot_svc_dashboard = _cloudwatch.dashboard.add_widgets(
            GraphWidget(
                title="Executions vs error rate",
                left=[execution_count_metric],
                right=[error_count_metric.with(
                    statistic="average",
                    label="Error rate",
                    color=Color.GREEN
                )]
            ))
        """

        polyglot_svc_dashboard.add_widgets(
            _cloudwatch.AlarmWidget(
                title="Lambda-Errors",
                alarm=polyglot_svc_fn_error_alarm
            )
        )

        ###########################################
        ################# OUTPUTS #################
        ###########################################

        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self,
                                  'PolyglotServiceApiUrl',
                                  value=f'{self.polyglot_svc_api_resource_01.url}',
                                  description=f'Call the polyglot API'
                                  )
