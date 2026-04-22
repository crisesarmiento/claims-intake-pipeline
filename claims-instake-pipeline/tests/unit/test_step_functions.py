from unittest.mock import patch, MagicMock
from lambdas.store import handler as store_handler
from lambdas.validate import handler as validate_handler
from lambdas.enrich import handler as enrich_handler
import pytest
import os

os.environ['TABLE_NAME'] = 'ClaimsTable'

@patch("lambdas.store.handler.boto3")
def test_store(mock_boto3):
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table
    event = {
        "claim_id": "c-001",
        "provider_id": "p-001",
        "amount": 150.0,
        "status": "pending",
        "service_date": "2026-04-21"
    }
    result = store_handler.handler(event, {})
    assert result is not None
    assert result == event
    mock_table.put_item.assert_called_once_with(Item=event)

def test_validate():
    event = {
        "claim_id": "c-001",
        "provider_id": "p-001",
        "patient_id": "pat-001",
        "amount": 150.0,
        "status": "pending",
        "service_date": "2026-04-21"
    }
    result = validate_handler.handler(event, {})
    assert result is not None
    assert result == event

def test_validate_missing_fields():
    event = {
        "claim_id": "c-001",
        "provider_id": "p-001",
        "amount": 150.0,
        "service_date": "2026-04-21"
    }
    with pytest.raises(ValueError):
        validate_handler.handler(event, {})

def test_enrich():
    event = {
        "claim_id": "c-001",
        "provider_id": "p-001",
        "amount": 150.0,
        "status": "pending",
        "service_date": "2026-04-21"
    }
    result = enrich_handler.handler(event, {})
    assert result is not None
    assert 'processed_at' in result
    assert result['status'] == "PROCESSED"