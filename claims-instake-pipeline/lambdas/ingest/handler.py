import json, logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log(level, event, **kwargs):
    logger.log(level, json.dumps({"event": event, **kwargs}))

def handler(event, context):


    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        log(logging.ERROR, "validation_failed", error=str(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Bad Request', 'details': 'Invalid JSON body'})
        }

    # 1. Validate required fields first
    if not body.get('claim_id') or not body.get('provider_id') or not body.get('patient_id') or not body.get('amount') or not body.get('service_date'):
        log(logging.ERROR, "validation_failed", error="Missing required fields")
        return {
            'statusCode': 422,
            'body': json.dumps({'error': 'Unprocessable Entity', 'details': 'Missing required fields'})
        }

    # 2. Then validate amount value (safe now — we know it exists)
    if body['amount'] <= 0:
        log(logging.ERROR, "validation_failed", error="Amount must be greater than 0")
        return {
            'statusCode': 422,
            'body': json.dumps({'error': 'Unprocessable Entity', 'details': 'Amount must be greater than 0'})
        }
    

    # 3. Send to SQS (we'll fill this next)
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=os.getenv('CLAIMS_QUEUE_URL'),
        MessageBody=json.dumps(body)
    )

    # 4 Cloudwatch log the claim
    boto3.client('cloudwatch').put_metric_data(
        Namespace="ClaimsIntakePipeline",
        MetricData=[{
            "MetricName": "ClaimsIngested",
            "Value": 1, 
            "Unit": "Count"
        }]
    )

    # 5. Return 202
    log(logging.INFO, "claim_ingested", claim_id=body["claim_id"], provider_id=body["provider_id"])
    return {
        'statusCode': 202,
        'body': json.dumps({'claim_id': body['claim_id']})
    }