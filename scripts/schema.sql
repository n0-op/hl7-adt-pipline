CREATE TABLE patient_identity (
    mrn VARCHAR(64) PRIMARY KEY,
    patient_uuid UUID NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patient_identity_uuid ON patient_identity(patient_uuid);

CREATE TABLE patient_records (
    patient_uuid UUID PRIMARY KEY REFERENCES patient_identity(patient_uuid),
    record_body JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_patient_records_body_gin ON patient_records USING GIN(record_body);