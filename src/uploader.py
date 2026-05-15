import json
from datetime import datetime

import boto3

from src.identity_resolver import get_or_create_patient_uuid

BUCKET_NAME = "hl7-pipeline-output-danmarquez"


def upload_to_s3(msg: dict) -> dict:
    event_timestamp = msg.get("event_timestamp", "")
    try:
        dt = datetime.strptime(event_timestamp[:14], "%Y%m%d%H%M%S")
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Malformed event_timestamp {event_timestamp!r}: expected YYYYMMDDHHMMSS"
        ) from e

    mrn = msg["patient"]["mrn"]
    patient_uuid = get_or_create_patient_uuid(mrn)

    s3_key = (
        f"parsed/{dt.year:04d}/{dt.month:02d}/{dt.day:02d}/"
        f"{patient_uuid}_{event_timestamp}.json"
    )

    boto3.client("s3").put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=json.dumps(msg).encode("utf-8"),
        ContentType="application/json",
        ServerSideEncryption="aws:kms",
    )

    return {"s3_key": s3_key, "patient_uuid": patient_uuid}
