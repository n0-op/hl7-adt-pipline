from hl7apy.parser import parse_message
from hl7apy.consts import VALIDATION_LEVEL

def parse_adt_message(raw_message: str) -> dict:
    msg = parse_message(raw_message.strip(), 
                    validation_level=VALIDATION_LEVEL.QUIET)

    pid = msg.pid
    pv1 = msg.pv1
    msh = msg.msh
    evn = msg.evn

    return {
        "message_id": msh.msh_10.value,
        "event_type": msh.msh_9.value,
        "event_timestamp": evn.evn_2.value,
        "patient": {
            "mrn": pid.pid_3.cx_1.value,
            "last_name": pid.pid_5.pid_5_1.value,
            "first_name": pid.pid_5.pid_5_2.value,
            "middle_initial": pid.pid_5.pid_5_3.value,
            "date_of_birth": pid.pid_7.value,
            "sex": pid.pid_8.value,
            "address": pid.pid_11.value,
            "phone": pid.pid_13.value,
        },
        "visit": {
            "patient_class": pv1.pv1_2.value,
            "location": pv1.pv1_3.value,
            "attending_physician": pv1.pv1_7.value,
            "service": pv1.pv1_10.value,
            "admit_type": pv1.pv1_4.value,
        }
    }