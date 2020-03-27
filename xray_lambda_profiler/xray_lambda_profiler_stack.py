from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_dynamodb as _dynamodb


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = 'MystiqueAutomation'
    ENVIRONMENT = 'production'
    REPO_NAME = 'xray-lambda-profiler'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    VERSION = '2020_03_21'


class XrayLambdaProfilerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, wiki_api_endpoint, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # DynamodDB Table
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
        with open("lambda_src/polyglot_strangler_fig_service.py", encoding="utf8") as fp:
            polyglot_strangler_fig_service_fn_handler_code = fp.read()

        polyglot_strangler_fig_service_fn = _lambda.Function(
            self,
            id='polyglotStranglerFigService',
            function_name="polyglot_strangler_fig_service_fn",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(
                polyglot_strangler_fig_service_fn_handler_code),
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
        queries_table.grant_read_write_data(polyglot_strangler_fig_service_fn)

        # Enable AWS XRay Tracing at API GW
        polyglot_svc_api_stage_options = _apigw.StageOptions(
            stage_name="myst",
            data_trace_enabled=True,
            tracing_enabled=True
        )

        # Create API Gateway
        polyglot_svc_api = _apigw.LambdaRestApi(
            self,
            'polyglotStranglerFigServiceApi',
            default_cors_preflight_options={
                "allow_origins": _apigw.Cors.ALL_ORIGINS
            },
            handler=polyglot_strangler_fig_service_fn,
            proxy=False,
            rest_api_name='mystique-xray-api',
            deploy_options=polyglot_svc_api_stage_options
        )

        self.polyglot_svc_api_resource = polyglot_svc_api.root.add_resource(
            "polyglot_svc")
        self.polyglot_svc_api_resource.add_method("GET")

        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self,
                                  'PolyglotServiceApi',
                                  value=f'{self.polyglot_svc_api_resource.url}',
                                  description=f'Call the polyglot API'
                                  )
