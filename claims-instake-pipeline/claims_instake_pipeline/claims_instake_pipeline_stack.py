from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
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

        
        claims_table = dynamodb.Table(self, "ClaimsInstakePipelineTable", partition_key=dynamodb.Attribute(name="claim_id", type=dynamodb.AttributeType.STRING), removal_policy=RemovalPolicy.DESTROY)

        claims_table.add_global_secondary_index(index_name="status_index", partition_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING), sort_key=dynamodb.Attribute(name="created_at", type=dynamodb.AttributeType.NUMBER))
        claims_table.add_global_secondary_index(index_name="provider_id_index", partition_key=dynamodb.Attribute(name="provider_id", type=dynamodb.AttributeType.STRING), sort_key=dynamodb.Attribute(name="created_at", type=dynamodb.AttributeType.NUMBER))