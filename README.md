# claims-intake-pipeline

Serverless healthcare data ingestion and processing pipeline built with Python, AWS CDK v2, and LocalStack.

## Architecture

```
POST /claims  (API Gateway)
      │
      ▼
 Lambda: ingest        ← validates input, puts message to SQS
      │
      ▼
 SQS Queue             ← decouples ingest from processing; DLQ on 3 failures
      │
      ▼
 Lambda: processor     ← Pandas normalization + batch aggregation
      │
      ▼
 Step Functions        ← orchestrates: Validate → Enrich → Store
      │
      ▼
 DynamoDB              ← stores processed claims
      │
      ▼
 CloudWatch            ← structured JSON logs + custom metrics dashboard
```

## Stack

- Python 3.12
- AWS CDK v2 (IaC)
- LocalStack (local AWS emulation)
- Pandas via Lambda container image
- pytest + moto (unit), LocalStack (integration)
- GitHub Actions CI

## Setup

```bash
# Install dependencies
make install

# Start LocalStack
localstack start

# Deploy stack to LocalStack
make deploy

# Run unit tests
make test-unit

# Run integration tests (requires LocalStack running)
make test-integration
```

## Usage

```bash
# Submit a claim
curl -X POST https://<api-id>.execute-api.localhost.localstack.cloud:4566/prod/claims \
  -H 'Content-Type: application/json' \
  -d '{
    "claim_id": "CLM-001",
    "provider_id": "P-123",
    "patient_id": "PAT-456",
    "amount": 150.00,
    "service_date": "2026-04-18"
  }'

# Invoke Lambda directly via LocalStack
make invoke-ingest

# Scan DynamoDB table
make scan-dynamo
```

## Design Decisions

### Container image over Lambda layer for Pandas
Pandas + NumPy + dependencies exceed the 250MB unzipped Lambda layer limit. Container images support up to 10GB. Cold start impact is mitigated with provisioned concurrency on latency-sensitive paths.

### Express Step Functions over Standard
Express workflows (up to 5 min, at-least-once, high throughput) fit data pipeline workloads. Standard workflows (up to 1 year, exactly-once, full audit trail) are the right choice for human-approval flows, financial transactions, or anything requiring strict deduplication guarantees.

### Two GSIs on ClaimsTable
- `StatusIndex` (PK: `status`, SK: `created_at`) — pipeline monitoring, e.g. query all `FAILED` claims in a time range
- `ProviderIndex` (PK: `provider_id`, SK: `created_at`) — business queries, e.g. all claims submitted by a given provider

### SQS over Kafka (MSK) at this scale
SQS is the right fit here: simple task queue, message consumed and deleted, built-in DLQ, no operational overhead. Kafka (AWS MSK) becomes the better choice when you need: (1) multiple independent consumers reading the same event stream, (2) event replay for audit or reprocessing, or (3) throughput in the millions of messages per second range. A migration path would be: replace SQS with an MSK topic, update the processor Lambda to use a Kafka consumer group, and keep the Step Functions orchestration unchanged downstream.

### Idempotency via DynamoDB partition key
`claim_id` is the DynamoDB partition key. Duplicate SQS delivery (at-least-once) results in a safe `put_item` overwrite — no duplicate records, no extra deduplication logic needed.

### SQS visibility timeout matches Lambda timeout
Both set to 300s. If the processor Lambda times out mid-execution, SQS will not re-deliver the message until the visibility window expires — preventing a second Lambda from processing the same batch concurrently.
