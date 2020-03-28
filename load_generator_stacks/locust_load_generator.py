import json

from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_ecs as _ecs
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import core

from load_generator_stacks.custom_resources.trigger_run_task.trigger_run_task_stack import trigger_run_task


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = 'MystiqueAutomation'
    ENVIRONMENT = 'production'
    REPO_NAME = 'xray-lambda-profiler'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    VERSION = '2020_03_23'


class LocustLoadGeneratorStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: _ec2.IVpc, url: str, LOAD_PARAMS: dict, ** kwargs) -> None:
        """
        Defines an instance of the traffic generator.
        :param scope: construct scope
        :param id:    construct id
        :param vpc:   the VPC in which to host the traffic generator cluster
        :param url:   the URL to hit
        :param LOAD_PARAMS:   LOCUST load testing parameters
        """
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here):
        locust_cluster = _ecs.Cluster(self,
                                      "locustCluster",
                                      vpc=vpc)

        """
        Load Testing Service in Fargate Cluster
        """

        locust_task_def = _ecs.FargateTaskDefinition(self,
                                                     "locustAppTaskDef",
                                                     )

        locust_container = locust_task_def.add_container("locustAppContainer",
                                                         environment={
                                                             "github_profile": "https://github.com/miztiik",
                                                             "LOCUSTFILE_PATH": "/locustfile.py",
                                                             "TARGET_URL": url,
                                                             "LOCUST_OPTS": f"--clients={LOAD_PARAMS['NO_OF_CLIENTS']} --hatch-rate={LOAD_PARAMS['HATCH_RATE']} --run-time={LOAD_PARAMS['RUN_TIME']} --no-web --print-stats",
                                                             # --clients The number of concurrent Locust users.
                                                             # --hatch-rate The rate per second in which clients are spawned.
                                                             # --run-time The number of seconds to run locust. ( Ensure enough time to hatch all users )
                                                             "ADDTIONAL_CUSTOM_OPTIONS": "--reset-stats --print-stats"
                                                         },
                                                         image=_ecs.ContainerImage.from_registry(
                                                             "mystique/xray-lambda-profiler:latest"),
                                                         logging=_ecs.LogDrivers.aws_logs(
                                                             stream_prefix="Mystique")
                                                         )

        locust_container.add_port_mappings(
            _ecs.PortMapping(container_port=80, protocol=_ecs.Protocol.TCP)
        )
        locust_container.add_port_mappings(
            _ecs.PortMapping(container_port=443, protocol=_ecs.Protocol.TCP)
        )

        # Defines an AWS Lambda resource
        with open("load_generator_stacks/lambda_src/create_fargate_run_task.py", encoding="utf8") as fp:
            create_fargate_run_task_fn_handler_code = fp.read()

        pub_subnet_ids = []
        for subnet in vpc.public_subnets:
            pub_subnet_ids.append(subnet.subnet_id)

        create_fargate_run_task_fn = _lambda.Function(
            self,
            id='triggerFargateRunTask',
            function_name="create_fargate_run_task_fn",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(
                create_fargate_run_task_fn_handler_code),
            handler='index.lambda_handler',
            timeout=core.Duration.seconds(200),
            environment={
                "CLUSTER_NAME": locust_cluster.cluster_name,
                "TASK_DEFINITION": locust_task_def.task_definition_arn,
                "SUBNETS": json.dumps(pub_subnet_ids),
                "CONTAINER_NAME": locust_container.container_name,
                "NO_OF_TASKS": LOAD_PARAMS["NO_OF_TASKS"]
            },
            reserved_concurrent_executions=1,
        )

        roleStmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[locust_task_def.task_definition_arn],
            actions=["ecs:RunTask"]
        )
        roleStmt1.sid = "AllowLambdaToCreateFargateRunTask"
        create_fargate_run_task_fn.add_to_role_policy(roleStmt1)

        # task_role = locust_task_def.execution_role.role_arn

        roleStmt2 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=[locust_task_def.execution_role.role_arn,
                       locust_task_def.task_role.role_arn],
            actions=["iam:PassRole"]
        )
        roleStmt2.sid = "AllowLambdaToPassRoleToRunTask"
        create_fargate_run_task_fn.add_to_role_policy(roleStmt2)

        # Create a trigger for our 'create_fargate_run_task' lambda Function
        gen_load = trigger_run_task(
            self, "triggerLoadGeneratorTask",
            config_params={
                "RUN_TASK_FN_ARN": create_fargate_run_task_fn.function_arn
            },
            message=[
                {
                    "RUN_TASK_FN_ARN": create_fargate_run_task_fn.function_arn
                }
            ]
        )

        """
        locust_service = _ecs.FargateService(self, 'locustAppService',
                                             cluster=locust_cluster,
                                             task_definition=locust_task_def,
                                             desired_count=2,
                                             assign_public_ip=True,
                                             service_name=f"{global_args.OWNER}-LocustLoadGenerator"
                                             )
        """
        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self,
                                  "LocustClusterName",
                                  value=f"{locust_cluster.cluster_name}",
                                  export_name="locustClusterName",
                                  description="The fargate cluster to generate load on APIs using Locust"
                                  )
