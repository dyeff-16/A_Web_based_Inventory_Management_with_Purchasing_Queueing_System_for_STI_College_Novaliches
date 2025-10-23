from datetime import datetime
from flask import session
import pytz
from db_proware import *

def audit_log(action):
    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    doc = {
        "action": action,
        "timestamp_str": ph_time.strftime('%Y-%m-%d %H:%M:%S')
    }

    user = session.get("user")
    if user:
        acct = db_account.find_one({"email": user.get('email')}, {"fullname": 1, "email": 1})
        if acct:
            doc["fullname"] = acct.get("fullname")
            doc["email"] = acct.get("email")

    db_auditlog.insert_one(doc)