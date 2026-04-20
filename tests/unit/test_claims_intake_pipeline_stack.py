import aws_cdk as core
import aws_cdk.assertions as assertions

from claims_intake_pipeline.claims_intake_pipeline_stack import ClaimsIntakePipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in claims_intake_pipeline/claims_intake_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ClaimsIntakePipelineStack(app, "claims-intake-pipeline")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
