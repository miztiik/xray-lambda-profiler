from aws_cdk import aws_cloudformation as cfn
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import core


class trigger_run_task(core.Construct):
    def __init__(self, scope: core.Construct, id: str, config_params, ** kwargs) -> None:
        super().__init__(scope, id)

        # Read LambdaFunction Code
        try:
            with open("load_generator_stacks/custom_resources/trigger_run_task/lambda_src/trigger_run_task_lambda_function.py", encoding="utf-8") as fp:
                code_body = fp.read()
        except OSError:
            print('Unable to read UserData script')

        # Create IAM Permission Statements that are required by the Lambda

        trigger_run_task_fn = _lambda.SingletonFunction(
            self, "Singleton",
            uuid="mystique2010-4ee1-11e8-9c2d-fa7ae01bbebc",
            code=_lambda.InlineCode(code_body),
            handler="index.lambda_handler",
            timeout=core.Duration.seconds(300),
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "RUN_TASK_FN_ARN": config_params.get("RUN_TASK_FN_ARN")
            },
            # security_group=config_params.get('RUN_TASK_FN_ARN'),

        )
        roleStmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=["*"],
            actions=["lambda:InvokeFunction"]
        )
        roleStmt1.sid = "AllowLambdaToInvokeLambda"
        trigger_run_task_fn.add_to_role_policy(roleStmt1)

        resource = cfn.CustomResource(
            self, "Resource",
            provider=cfn.CustomResourceProvider.lambda_(
                trigger_run_task_fn
            ),
            properties=kwargs,
        )

        self.response = resource.get_att("Response").to_string()
