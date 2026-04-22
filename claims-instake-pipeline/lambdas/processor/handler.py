import json
import pandas as pd

def handler(event, context):
    
    if event['Records']:
        records = []
        for record in event['Records']:
            body = json.loads(record['body'])
            records.append(body)


        df = pd.DataFrame(records) # all records in a one dataframe

        df["service_date"] = pd.to_datetime(df["service_date"])
        df["amount"] = df["amount"].astype(float)
        df["status"] = df["status"].str.upper()
        
        totals = df.groupby('provider_id')['amount'].sum()


        print("Totals by provider:", totals.to_dict()) # log totals
        return df.to_dict(orient='records') # return normalized records
    else:
        return []