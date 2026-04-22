import os, boto3
import json, logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log(level, event, **kwargs):
    logger.log(level, json.dumps({"event": event, **kwargs}))

def handler(event, context):
    try:
        table = boto3.resource("dynamodb").Table(os.environ['TABLE_NAME'])
        table.put_item(Item=event)

        boto3.client('cloudwatch').put_metric_data(
            Namespace="ClaimsIntakePipeline",
            MetricData=[{
                "MetricName": "ClaimsProcessed",
                "Value": 1, 
                "Unit": "Count"
            }]
        )

        log(logging.INFO, "claim_stored", claim_id=event["claim_id"], provider_id=event["provider_id"])
        return event
    except Exception as e:
        log(logging.ERROR, "claim_stored_failed", error=str(e))
        raise e