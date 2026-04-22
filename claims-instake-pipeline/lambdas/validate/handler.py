import json, logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log(level, event, **kwargs):
    logger.log(level, json.dumps({"event": event, **kwargs}))

def handler(event, context):

    required = ['claim_id', 'provider_id', 'patient_id', 'amount', 'service_date']

    for field in required:
        if not event.get(field):
            log(logging.ERROR, "validation_failed", error=f"Missing required field: {field}")
            raise ValueError(f"Missing required field: {field}")

    if event['amount'] <= 0:
        log(logging.ERROR, "validation_failed", error="Amount must be greater than 0")
        raise ValueError("Amount must be greater than 0")
    
    log(logging.INFO, "claim_validated", claim_id=event["claim_id"], provider_id=event["provider_id"])
    return event # pass the claim to the next step