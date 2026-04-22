import os, boto3

def handler(event, context):
    table = boto3.resource("dynamodb").Table(os.environ['TABLE_NAME'])
    table.put_item(Item=event)
    return event