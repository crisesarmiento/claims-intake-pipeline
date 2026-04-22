def handler(event, context):

    required = ['claim_id', 'provider_id', 'patient_id', 'amount', 'service_date']

    for field in required:
        if not event.get(field):
            raise ValueError(f"Missing required field: {field}")

    if event['amount'] <= 0:
        raise ValueError(f"Amount must be greater than 0")
        
    return event # pass the claim to the next step