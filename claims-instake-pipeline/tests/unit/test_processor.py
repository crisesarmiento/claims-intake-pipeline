import json
from lambdas.processor import handler as processor_handler
import pandas as pd


def test_processor_normalization():
    event = {
        "Records": [
            {"body": json.dumps({"claim_id": "c-001", "provider_id": "p-001", "amount": "150.0", "status": "pending", "service_date": "2026-04-21"})},
            {"body": json.dumps({"claim_id": "c-002", "provider_id": "p-001", "amount": "200.0", "status": "processed", "service_date": "2026-04-20"})},
        ]
    }

    result = processor_handler.handler(event, {})

    assert isinstance(result[0]['service_date'], pd.Timestamp)
    assert isinstance(result[0]['amount'], float)
    assert result[0]['status'] == result[0]['status'].upper()


def test_processor_empty_batch():
    event = {"Records": []}
    result = processor_handler.handler(event, {})
    assert result == []


def test_processor_aggregated_totals():
    event = {
        "Records": [
            {"body": json.dumps({"claim_id": "c-001", "provider_id": "p-001", "amount": "150.0", "status": "pending", "service_date": "2026-04-21"})},
            {"body": json.dumps({"claim_id": "c-002", "provider_id": "p-001", "amount": "200.0", "status": "processed", "service_date": "2026-04-20"})},
        ]
    }
    result = processor_handler.handler(event, {})
    assert result is not None
    totals = sum(r['amount'] for r in result if r['provider_id'] == 'p-001')
    assert totals == 350.0