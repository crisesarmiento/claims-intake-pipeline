#!/usr/bin/env python3
import os
import aws_cdk as cdk
from claims_instake_pipeline.claims_instake_pipeline_stack import ClaimsInstakePipelineStack


app = cdk.App()
ClaimsInstakePipelineStack(app, "ClaimsInstakePipelineStack")

app.synth()
