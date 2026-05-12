import json
from parser import parse_adt_message

with open("data/samples/adt_a01.hl7", "r") as f:
    raw = f.read()

# HL7 uses \r as segment terminator, not \n
raw = raw.replace("\n", "\r").replace("\r\r", "\r")

result = parse_adt_message(raw)
print(json.dumps(result, indent=2))