from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    RemovalPolicy,
)
from constructs import Construct

class ClaimsInstakePipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, encrypt_bucket: bool = False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if encrypt_bucket:
            s3.Bucket(self, "ClaimsInstakePipelineBucket", encryption=s3.BucketEncryption.KMS_MANAGED,removal_policy=RemovalPolicy.DESTROY)
        else:
            s3.Bucket(self, "ClaimsInstakePipelineBucket", removal_policy=RemovalPolicy.DESTROY)
