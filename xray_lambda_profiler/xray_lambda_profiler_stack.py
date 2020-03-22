from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_apigateway as _apigw


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
        with open("lambda_src/get_python_jobs.py", encoding="utf8") as fp:
            get_python_jobs_fn_handler_code = fp.read()

        get_python_jobs_fn = _lambda.Function(
            self,
            id='getPythonJobsFn',
            function_name="get_python_jobs_fn",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(get_python_jobs_fn_handler_code),
            handler='index.lambda_handler',
            timeout=core.Duration.seconds(300),
            environment={
                'LD_LIBRARY_PATH': '/opt/python',
                'WIKI_API_ENDPOINT': f'http://{wiki_api_endpoint}/api'
            },
            layers=[aws_xray_layer, requests_layer],
            tracing=_lambda.Tracing.ACTIVE
        )

        # Create API Gateway
        api_01 = _apigw.RestApi(self, "apiEndpoint")
        v1 = api_01.root.add_resource("v1")

        # Add resource for jobs API
        hot_jobs = v1.add_resource('hot_jobs')
        hot_jobs_integration = _apigw.LambdaIntegration(get_python_jobs_fn)
        hot_jobs_method = hot_jobs.add_method(
            "GET", hot_jobs_integration)

        # Add resource for HTTP Endpoint: API Hosted on EC2
        wiki_url = v1.add_resource('wiki_url')
        wiki_url_integration = _apigw.HttpIntegration(
            url=f'http://{wiki_api_endpoint}/api/{{needle}}', http_method='GET', proxy=False)
        wiki_url_method = wiki_url.add_method(
            "GET", wiki_url_integration)

        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self,
                                  "APIGatewayUrl",
                                  value=f'{api_01.url}',
                                  description=f"This url to query for hottest python jobs"
                                  )
