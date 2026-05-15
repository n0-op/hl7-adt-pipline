# hl7-adt-pipeline

An HL7 v2 ADT message pipeline that parses inbound messages, validates them, resolves patient identities, and stores results in HIPAA-aligned AWS infrastructure.

I built it to get hands-on with the operational side of healthcare data integration: ingestion, identity resolution, encrypted storage, audit logging. It is not production-ready and it does not handle real PHI, but the architecture mirrors what a production system would look like.

## What it does

Reads an HL7 v2 ADT A01 (admit) message, extracts patient and visit data, runs validation, looks up or creates a patient UUID, and writes the parsed JSON to S3 keyed by that UUID. The patient identity mapping lives in PostgreSQL on RDS.

End-to-end output for the sample message:

```
parsed message → validation passes → MRN123456 resolves to eba33260-4885-4dae-b6cc-a023333857f4
→ written to s3://hl7-pipeline-output-danmarquez/parsed/2024/03/15/eba33260-4885-4dae-b6cc-a023333857f4_20240315082300.json
```

## Architecture

```
HL7 v2 ADT message (file)
    │
    ▼
src/parser.py     ── hl7apy → structured Python dict
    │
    ▼
src/validator.py  ── checks MRN, timestamp, event type
    │
    ▼
src/identity_resolver.py  ── MRN ↔ UUID via PostgreSQL
    │
    ▼
src/uploader.py   ── JSON to S3 with KMS encryption
```

Two storage destinations. PostgreSQL on RDS holds the patient identity mapping. It is a hot path that needs fast, consistent key lookups by MRN or UUID, and the schema also includes a `patient_records` table with a JSONB column ready for Phase 2. S3 holds the full parsed message body. It is bulk data that benefits from cheap, immutable, encrypted object storage, partitioned by date and keyed by patient UUID.

Splitting them this way is a deliberate architectural choice. The alternative would be cramming everything into PostgreSQL, which works fine until the volume of stored messages grows and the operational store gets bogged down with what is essentially cold storage.

## HIPAA-aligned configuration

No real PHI passes through this project, but the AWS configuration follows the same rules that would apply if it did:

- S3 bucket has SSE-KMS encryption on by default
- Bucket policy denies any request without HTTPS, and denies any upload that does not explicitly request KMS encryption
- CloudTrail logs every data event on the bucket, scoped to just this bucket so the logs are not buried in noise from the rest of the account
- IAM policy on the writer is least-privilege, with bucket-level and object-level actions on separate resources
- RDS has encryption at rest enabled, lives in a security group locked to a single IP, and is not publicly addressable beyond that
- Credentials come from a gitignored `.env` file; SQL is parameterized everywhere

A production version of this would swap `.env` for AWS Secrets Manager, run RDS in Multi-AZ, and put everything in a proper VPC. Those choices were skipped to keep monthly costs at zero and stay focused on the integration logic.

## Stack

- Python 3.10+
- `hl7apy` for HL7 v2 parsing
- `boto3` for AWS
- `psycopg2-binary` for PostgreSQL
- `python-dotenv` for local config
- AWS services: S3, IAM, KMS, CloudTrail, RDS PostgreSQL 18

## Repo layout

```
hl7-adt-pipeline/
├── data/samples/adt_a01.hl7     # test message
├── scripts/
│   ├── apply_schema.py           # creates the PostgreSQL tables
│   └── verify_schema.py          # confirms tables exist
├── src/
│   ├── parser.py                 # hl7apy wrapper
│   ├── validator.py              # field and event-type checks
│   ├── identity_resolver.py      # MRN ↔ UUID
│   ├── uploader.py               # S3 write with KMS
│   └── main.py                   # end-to-end runner
├── pyproject.toml
└── .env.example                  # template; real .env is gitignored
```

## Running it

```bash
git clone https://github.com/n0-op/hl7-adt-pipeline.git
cd hl7-adt-pipeline
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .

cp .env.example .env
# edit .env with your RDS endpoint and credentials
aws configure

python scripts/apply_schema.py
python src/main.py
```

## Roadmap

This is Phase 1 of a four-phase build. Each phase fills in another layer of what a production integration platform actually has to handle.

**Phase 1 — Ingest and store** (done)

Parse a single ADT message, validate it, resolve patient identity, write to S3 and PostgreSQL.

**Phase 2 — Validate, route, observe**

Expand the validator into a real framework with severity levels and a dead-letter pattern. Wire `patient_records` into the upload path so the parsed body also lands in PostgreSQL as JSONB. Add structured logging with correlation IDs that follow a message through every stage. This is the phase where the pipeline stops looking like a script and starts looking like a service.

**Phase 3 — Event-driven ingestion**

Replace the manual `main.py` run with an S3-triggered Lambda. Add CloudWatch dashboards for ingestion volume, parse success rate, validation pass rate, and end-to-end latency. This is where the project starts to feel like a real ingestion system instead of a demo.

**Phase 4 — FHIR and analytics**

Add a conversion layer that turns the parsed HL7 output into a FHIR R4 Patient resource. Add Athena over the S3 output for ad-hoc SQL analytics on the JSON files directly. This phase bridges to how real platforms like Zus Health expose data to downstream consumers.

## Known gaps

Things I would do differently in production. Listed here so they do not look like oversights:

- The identity resolver has a race condition. Two concurrent inserts for the same MRN would both find nothing, both attempt the insert, and the second would fail on the unique constraint. The fix is `INSERT ... ON CONFLICT (mrn) DO NOTHING RETURNING patient_uuid`. I left it as-is for clarity in the demo, but it is a real bug.
- `.env` is fine for local development. In production this moves to AWS Secrets Manager with rotation.
- Single-AZ RDS means no automatic failover. Multi-AZ would double the cost for no benefit on a portfolio project.
- No tests yet. A real version would have unit tests for the parser and validator, plus integration tests that round-trip a synthetic message through the full pipeline.
- MRN as the only identity attribute is a simplification. Real identity resolution does fuzzy matching across name, date of birth, and other demographic fields, and has to deal with merge events when two records turn out to be the same patient.
- No retry or dead-letter handling. A real pipeline routes failed messages somewhere for triage. This one just raises and stops.

