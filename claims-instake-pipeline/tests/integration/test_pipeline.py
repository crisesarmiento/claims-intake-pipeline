import boto3
import requests
import time

API_URL = "https://mywajjmlwb.execute-api.localhost.localstack.cloud:4566/prod/claims"

def get_client(service):
    return boto3.client(service, endpoint_url="http://localhost:4566", region_name="us-east-1", aws_access_key_id="test", aws_secret_access_key="test")

VALID_CLAIMS = {
    "claim_id": "c-integration-001",
    "provider_id": "p-001",
    "patient_id": "pat-001",
    "amount": 150.0,
    "service_date": "2026-04-21"
}

def test_post_valid_claim_returns_202():
    response = requests.post(API_URL, json=VALID_CLAIMS)
    assert response.status_code == 202
    assert response.json().get('claim_id') == "c-integration-001"

def test_claim_stored_in_dynamodb():
    response = requests.post(API_URL, json=VALID_CLAIMS)
    time.sleep(3)
    dynamodb = get_client("dynamodb")
    item = dynamodb.get_item(TableName="ClaimsTable", Key={"claim_id": {"S": "c-integration-001"}})
    assert item.get('Item') != {} # empty dict means no item found


def test_invalid_claim_returns_422_dlq_empty():
    invalid_claim = {**VALID_CLAIMS, "amount": -1}
    response = requests.post(API_URL, json=invalid_claim)
    assert response.status_code == 422

    sqs = get_client("sqs")
    dlq_url = sqs.get_queue_url(QueueName="ClaimsDeadLetterQueue")["QueueUrl"]
    atts = sqs.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=["ApproximateNumberOfMessages"])

    assert atts.get('Attributes').get('ApproximateNumberOfMessages') == '0'