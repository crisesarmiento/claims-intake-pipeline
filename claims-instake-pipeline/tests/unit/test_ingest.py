import json
from unittest.mock import patch
from lambdas.ingest import handler as ingest_handler

@patch("lambdas.ingest.handler.boto3")
def test_ingest_handler(mock_boto3):
    mock_boto3.client.return_value.send_message.return_value = {}
    mock_boto3.client.return_value.put_metric_data.return_value = {}

    event = {
        "body": json.dumps({
            "claim_id": "c-001",
            "provider_id": "p-001",
            "patient_id": "pat-001",
            "amount": 150.0,
            "service_date": "2026-04-21"
        })
    }

    result = ingest_handler.handler(event, {})

    # Both SQS and Cloudwatch should be called
    assert result is not None
    assert result['statusCode'] == 202
    assert result['body'] == json.dumps({'claim_id': 'c-001'})
    mock_boto3.client.return_value.send_message.assert_called_once()
    mock_boto3.client.return_value.put_metric_data.assert_called_once()

@patch("lambdas.ingest.handler.boto3")
def test_missing_claim_id(mock_boto3):
    mock_boto3.client.return_value.send_message.return_value = {}
    mock_boto3.client.return_value.put_metric_data.return_value = {}
    mock_boto3.client.return_value.send_message.assert_not_called()
    mock_boto3.client.return_value.put_metric_data.assert_not_called()
    event = {
        "body": json.dumps({
            "provider_id": "p-001",
            "patient_id": "pat-001",
            "amount": 150.0,
            "service_date": "2026-04-21"
        })
    }   
    result = ingest_handler.handler(event, {})
    assert result is not None
    assert result['statusCode'] == 422
    assert result['body'] == json.dumps({'error': 'Unprocessable Entity', 'details': 'Missing required fields'})
    mock_boto3.client.return_value.send_message.assert_not_called()
    mock_boto3.client.return_value.put_metric_data.assert_not_called()

@patch("lambdas.ingest.handler.boto3")
def test_amount_is_minus_ten(mock_boto3):
    mock_boto3.client.return_value.send_message.return_value = {}
    mock_boto3.client.return_value.put_metric_data.return_value = {}

    event = {
        "body": json.dumps({
            "claim_id": "c-001",
            "provider_id": "p-001",
            "patient_id": "pat-001",
            "amount": -10.0,
            "service_date": "2026-04-21"
        })
        }
    result = ingest_handler.handler(event, {})
    assert result is not None
    assert result['statusCode'] == 422
    assert result['body'] == json.dumps({'error': 'Unprocessable Entity', 'details': 'Amount must be greater than 0'})
    mock_boto3.client.return_value.send_message.assert_not_called()
    mock_boto3.client.return_value.put_metric_data.assert_not_called()