from aws_cdk import (
    Stack,
    aws_sqs as sqs,
    Duration,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from constructs import Construct

class ClaimsInstakePipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, encrypt_bucket: bool = False, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if encrypt_bucket:
            s3.Bucket(self, "ClaimsInstakePipelineBucket", encryption=s3.BucketEncryption.KMS_MANAGED,removal_policy=RemovalPolicy.DESTROY)
            
        else:
            s3.Bucket(self, "ClaimsInstakePipelineBucket", removal_policy=RemovalPolicy.DESTROY)

        
        claims_table = dynamodb.Table(self,"ClaimsTable", table_name="ClaimsTable", partition_key=dynamodb.Attribute(name="claim_id", type=dynamodb.AttributeType.STRING), billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST, removal_policy=RemovalPolicy.DESTROY)

        claims_table.add_global_secondary_index(index_name="StatusIndex", partition_key=dynamodb.Attribute(name="status", type=dynamodb.AttributeType.STRING), sort_key=dynamodb.Attribute(name="created_at", type=dynamodb.AttributeType.NUMBER))
        claims_table.add_global_secondary_index(index_name="ProviderIndex", partition_key=dynamodb.Attribute(name="provider_id", type=dynamodb.AttributeType.STRING), sort_key=dynamodb.Attribute(name="created_at", type=dynamodb.AttributeType.NUMBER))
        
        # 1. DLQ (Dead Letter Queue)
        dlq = sqs.Queue(self, "ClaimsDeadLetterQueue", queue_name="ClaimsDeadLetterQueue", removal_policy=RemovalPolicy.DESTROY)

        # 2. Claims Queue (Queue for claims)
        claims_queue = sqs.Queue(self,"ClaimsQueue", queue_name="ClaimsQueue", visibility_timeout=Duration.seconds(300), dead_letter_queue=sqs.DeadLetterQueue(queue=dlq, max_receive_count=3),
            removal_policy=RemovalPolicy.DESTROY)

        # 3. Ingest Lambda (Lambda for ingesting claims)
        ingest_fn = lambda_.Function(self, "IngestFunction", function_name="claims-intake-pipeline-ingest-function", runtime=lambda_.Runtime.PYTHON_3_12, handler="handler.handler", code=lambda_.Code.from_asset("lambdas/ingest"), environment={
            "CLAIMS_QUEUE_URL": claims_queue.queue_url
        })

        processor_fn = lambda_.Function(self, "ProcessorFunction", function_name="claims-intake-pipeline-processor-function", runtime=lambda_.Runtime.PYTHON_3_12, handler="handler.handler", code=lambda_.Code.from_asset("lambdas/processor"))

        processor_fn.add_event_source(SqsEventSource(claims_queue, batch_size=10))

        validate_fn = lambda_.Function(self, "ValidationFunction", runtime=lambda_.Runtime.PYTHON_3_12, function_name="claims-intake-pipeline-validation-function", handler="handler.handler", code=lambda_.Code.from_asset("lambdas/validate"))

        enrich_fn = lambda_.Function(self, "EnrichFunction", runtime=lambda_.Runtime.PYTHON_3_12, function_name="claims-intake-pipeline-enrich-function", handler="handler.handler", code=lambda_.Code.from_asset("lambdas/enrich"))

        store_fn = lambda_.Function(self, "StoreFunction", runtime=lambda_.Runtime.PYTHON_3_12, function_name="claims-intake-pipeline-store-function", handler="handler.handler", code=lambda_.Code.from_asset("lambdas/store"), environment={
            "TABLE_NAME": claims_table.table_name
        })

        validate_task = tasks.LambdaInvoke(self, "ValidateClaim", lambda_function=validate_fn, payload_response_only=True)
        enrich_task = tasks.LambdaInvoke(self, "EnrichClaim", lambda_function=enrich_fn, payload_response_only=True)
        store_task = tasks.LambdaInvoke(self, "StoreClaim", lambda_function=store_fn, payload_response_only=True)


        validate_task.add_retry(
            errors=["Lambda.ServiceException"],
            max_attempts=3,
            backoff_rate=2,
            interval=Duration.seconds(2)
        )
        

        fail_state = sfn.Pass(self, "FailState", parameters={"status": "FAILED"})
        validate_task.add_catch(fail_state, result_path="$.error")

        chain = sfn.Chain.start(validate_task).next(enrich_task).next(store_task)
        state_machine = sfn.StateMachine(self, "ClaimsStateMachine", state_machine_name="ClaimsStateMachine", definition=chain, state_machine_type=sfn.StateMachineType.EXPRESS)

        # 4. API Gateway (API for claims)
        api = apigateway.RestApi(self, "ClaimsApi")
        claims_resource = api.root.add_resource("claims")
        claims_resource.add_method("POST", apigateway.LambdaIntegration(ingest_fn))
        