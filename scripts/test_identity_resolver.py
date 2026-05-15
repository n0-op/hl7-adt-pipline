from src.identity_resolver import get_or_create_patient_uuid, lookup_mrn

# First call — should create
uuid1 = get_or_create_patient_uuid("MRN123456")
print(f"First call: {uuid1}")

# Second call — should return the same UUID
uuid2 = get_or_create_patient_uuid("MRN123456")
print(f"Second call: {uuid2}")
print(f"Same UUID? {uuid1 == uuid2}")

# Reverse lookup
mrn = lookup_mrn(uuid1)
print(f"Reverse lookup: {mrn}")