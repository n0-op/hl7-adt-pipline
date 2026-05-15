import os
import uuid
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def _get_connection():
    try:
        return psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
    except KeyError as e:
        raise RuntimeError(f"Missing required environment variable: {e}") from e
    except psycopg2.OperationalError as e:
        raise RuntimeError(f"Failed to connect to the database: {e}") from e


def get_or_create_patient_uuid(mrn: str) -> str:
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT patient_uuid FROM patient_identity WHERE mrn = %s",
                (mrn,),
            )
            row = cur.fetchone()
            if row:
                return str(row[0])

            new_uuid = uuid.uuid4()
            cur.execute(
                    """
                    INSERT INTO patient_identity (mrn, patient_uuid)
                    VALUES (%s, %s)
                    ON CONFLICT (mrn) DO NOTHING
                    RETURNING patient_uuid
                    """,
                    (mrn, str(new_uuid))
            )
        conn.commit()
    return str(new_uuid)


def lookup_mrn(patient_uuid: str) -> str | None:
    with _get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT mrn FROM patient_identity WHERE patient_uuid = %s",
                (patient_uuid,),
            )
            row = cur.fetchone()
    return row[0] if row else None
