import datetime
from flask import session
import pytz
from db_proware import *


def audit_log(action):
    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    print("PH Time Logged:", ph_time.strftime("%Y-%m-%d %H:%M:%S"))
    session_get = session.get("user")
    email = db_account.find_one({"email": session_get['email']})
   
    fullname = email['fullname']
    db_auditlog.insert_one({
        "fullname": fullname,
        "action": action,
        "timestamp": ph_time  
    })