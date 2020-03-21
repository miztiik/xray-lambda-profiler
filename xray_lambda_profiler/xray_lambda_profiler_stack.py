from aws_cdk import core
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_apigateway as _apigw


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = ''
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'


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
                'WIKI_API_ENDPOINT': wiki_api_endpoint
            },
            layers=[aws_xray_layer, requests_layer],
            tracing=_lambda.Tracing.ACTIVE
        )

        # Create API Gateway
        hot_jobs_api = _apigw.LambdaRestApi(
            self,
            'hotJobsApi',
            default_cors_preflight_options={
                "allow_origins": _apigw.Cors.ALL_ORIGINS,
                # "allow_methods": _apigw.Cors.ALL_METHODS
            },
            handler=get_python_jobs_fn,
            proxy=False
        )

        get_hot_jobs = hot_jobs_api.root.add_resource("hot_jobs")
        get_hot_jobs.add_method("GET")
