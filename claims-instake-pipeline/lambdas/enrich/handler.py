import datetime

def handler(event, context):
    event["processed_at"] = datetime.datetime.now().isoformat()
    event["status"] = "PROCESSED"
    return event