import json
from src.parser import parse_adt_message
from src.validator import validate_parsed_message
from src.uploader import upload_to_s3

with open("data/samples/adt_a01.hl7", "r") as f:
    raw = f.read()

# HL7 uses \r as segment terminator, not \n
raw = raw.replace("\n", "\r").replace("\r\r", "\r")

result = parse_adt_message(raw)
print(json.dumps(result, indent=2))

validation = validate_parsed_message(result)
print(json.dumps(validation, indent=2))

if validation["valid"]:
    upload_result = upload_to_s3(result)
    print(f"s3_key: {upload_result['s3_key']}")
    print(f"patient_uuid: {upload_result['patient_uuid']}")
else:
    print("Validation failed, skipping upload. Errors:")
    for error in validation["errors"]:
        print(f"  - {error}")