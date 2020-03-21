from aws_cdk import aws_ec2 as _ec2
from aws_cdk import aws_iam as _iam
from aws_cdk import core


class global_args:
    '''
    Helper to define global statics
    '''
    OWNER = 'MystiqueAutomation'
    ENVIRONMENT = 'production'
    REPO_NAME = 'xray-lambda-profiler'
    SOURCE_INFO = f'https://github.com/miztiik/{REPO_NAME}'
    VERSION = '2020_03_21'


class getWikiUrlStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Read BootStrap Script
        try:
            with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
                user_data = file.read()
        except OSError:
            print('Unable to read UserData script')

        # Get the latest AMI from AWS SSM
        linux_ami = _ec2.AmazonLinuxImage(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2)

        # Read BootStrap Script
        try:
            with open("bootstrap_scripts/install_httpd.sh", mode="r") as file:
                user_data = file.read()
        except OSError:
            print('Unable to read UserData script')

        # Get the latest ami
        amzn_linux_ami = _ec2.MachineImage.latest_amazon_linux(
            generation=_ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
        )
        # ec2 Instance Role
        _instance_role = _iam.Role(self, "webAppClientRole",
                                   assumed_by=_iam.ServicePrincipal(
                                       'ec2.amazonaws.com'),
                                   managed_policies=[
                                       _iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'AmazonSSMManagedInstanceCore'
                                       ),
                                       _iam.ManagedPolicy.from_aws_managed_policy_name(
                                           'AWSXRayDaemonWriteAccess'
                                       )
                                   ])
        # web_app_server Instance
        self.web_app_server = _ec2.Instance(self,
                                            "webAppServer",
                                            instance_type=_ec2.InstanceType(
                                                instance_type_identifier="t2.micro"),
                                            instance_name="web_app_server",
                                            machine_image=amzn_linux_ami,
                                            vpc=vpc,
                                            vpc_subnets=_ec2.SubnetSelection(
                                                subnet_type=_ec2.SubnetType.PUBLIC
                                            ),
                                            role=_instance_role,
                                            user_data=_ec2.UserData.custom(
                                                user_data)
                                            )

        # Allow Web Traffic to WebServer
        self.web_app_server.connections.allow_from_any_ipv4(
            _ec2.Port.tcp(80), description="Allow Web Traffic"
        )

        self.web_app_server.connections.allow_from_any_ipv4(
            _ec2.Port.tcp(443), description="Allow Secured Web Traffic"
        )

        output_0 = core.CfnOutput(self,
                                  "AutomationFrom",
                                  value=f"{global_args.SOURCE_INFO}",
                                  description="To know more about this automation stack, check out our github page."
                                  )

        output_1 = core.CfnOutput(self,
                                  "ApplicationServer",
                                  value=f'http://{self.web_app_server.instance_public_ip}/api/mystique',
                                  description=f"This instance serves the wiki url for a given search keyword"
                                  )
