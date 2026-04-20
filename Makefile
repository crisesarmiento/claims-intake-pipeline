# Define variables
AWS_PROFILE := default
REGION := us-east-1

.PHONY: install bootstrap deploy synth clean

# Install dependencies
install:
	npm install

# Bootstrap the environment (Required once per account/region)
bootstrap:
	npx cdk bootstrap aws://$(shell aws sts get-caller-identity --query Account --output text --profile $(AWS_PROFILE))/$(REGION) --profile $(AWS_PROFILE)

# Synthesize the CloudFormation template
synth:
	npx cdk synth --profile $(AWS_PROFILE)

# Deploy the stack
deploy:
	npx cdk deploy --require-approval never --profile $(AWS_PROFILE)

# Clean up build artifacts
clean:
	rm -rf cdk.out
