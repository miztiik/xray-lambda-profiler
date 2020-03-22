from aws_cdk import core
from aws_cdk import aws_apigateway as _apigw


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = 'MystiqueAutomation'
    ENVIRONMENT = 'production'
    REPO_NAME = 'xray-lambda-profiler'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    VERSION = '2020_03_22'


class wikiApiStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, wiki_api_endpoint, ** kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create API Gateway
        api_01 = _apigw.RestApi(self, 'apiEndpoint',
                                rest_api_name='mystique-wiki-api')
        v1 = api_01.root.add_resource("v1")

        # Add resource for HTTP Endpoint: API Hosted on EC2
        self.wiki_url_path_00 = v1.add_resource('wiki_url')
        wiki_url_path_01 = self.wiki_url_path_00.add_resource('{needle}')

        list_objects_responses = [_apigw.IntegrationResponse(status_code="200",
                                                             response_parameters={
                                                                 'method.response.header.Timestamp': 'integration.response.header.Date',
                                                                 'method.response.header.Content-Length': 'integration.response.header.Content-Length',
                                                                 'method.response.header.Content-Type': 'integration.response.header.Content-Type'
                                                             }
                                                             )
                                  ]

        wiki_url_integration_options = _apigw.IntegrationOptions(
            integration_responses=list_objects_responses,
            request_parameters={
                "integration.request.path.needle": "method.request.path.needle"}
        )

        wiki_url_integration = _apigw.HttpIntegration(
            url=f'http://{wiki_api_endpoint}/api/{{needle}}',
            http_method='GET',
            options=wiki_url_integration_options,
            proxy=False,
        )
        wiki_url_method = wiki_url_path_01.add_method(
            "GET", wiki_url_integration,
            request_parameters={
                'method.request.header.Content-Type': False,
                'method.request.path.needle': True
            },
            method_responses=[_apigw.MethodResponse(status_code="200",
                                                    response_parameters={
                                                        'method.response.header.Timestamp': False,
                                                        'method.response.header.Content-Length': False,
                                                        'method.response.header.Content-Type': False
                                                    },
                                                    response_models={
                                                        'application/json': _apigw.EmptyModel()
                                                    }
                                                    )
                              ]
        )

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

        output_2 = core.CfnOutput(self,
                                  "GetWiki",
                                  value=f'{self.wiki_url_path_00.url}',
                                  description=f'Get Wiki Url for given topic'
                                  )
