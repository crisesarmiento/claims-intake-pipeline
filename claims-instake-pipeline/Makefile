.PHONY: deploy test invoke

deploy:
	cdklocal deploy --require-approval never
test:
	python -m pytest tests/ -v
invoke:
	awslocal lambda invoke --function-name claims-intake-pipeline-ingest-function output.json
	