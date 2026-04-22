import json, logging
import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log(level, event, **kwargs):
    logger.log(level, json.dumps({"event": event, **kwargs}))

def handler(event, context):
    event["processed_at"] = datetime.datetime.now().isoformat()
    event["status"] = "PROCESSED"
    log(logging.INFO, "claim_enriched", claim_id=event["claim_id"], provider_id=event["provider_id"])
    return event