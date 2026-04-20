#!/usr/bin/env python3
import os
import aws_cdk as cdk
from claims_instake_pipeline.claims_instake_pipeline_stack import ClaimsInstakePipelineStack

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
CDK_DEFAULT_ACCOUNT = os.getenv("CDK_DEFAULT_ACCOUNT", "000000000000")

app = cdk.App()
ClaimsInstakePipelineStack(app, "ClaimsInstakePipelineStack", env=cdk.Environment(
    account=CDK_DEFAULT_ACCOUNT,
    region=AWS_REGION
))

app.synth()
