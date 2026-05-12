EXPECTED_EVENT_TYPES = {"A01", "A08", "A40"}

def validate_parsed_message(msg: dict) -> dict:
    errors = []

    mrn = msg.get("patient", {}).get("mrn", "")
    if not mrn:
        errors.append("mrn is missing or empty")

    event_timestamp = msg.get("event_timestamp", "")
    if not event_timestamp:
        errors.append("event_timestamp is missing or empty")

    event_type = msg.get("event_type", "")
    if not any(t in event_type for t in EXPECTED_EVENT_TYPES):
        errors.append(f"event_type '{event_type}' is not one of the expected ADT types: A01, A08, A40")

    return {"valid": len(errors) == 0, "errors": errors}
