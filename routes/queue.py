from flask import Blueprint, redirect, render_template, session, url_for
from db_proware import db_orders

queuebp = Blueprint('queue', __name__, url_prefix='/queue')

@queuebp.route("/queue_user", methods=["GET"])
def queue_user():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    if 'queue' in session:
        user_session = session['user']
        email_session = user_session['email']
        # Find the first order in the queue (now serving)
        now_serving_order = db_orders.find_one({"queue_status": "queue"}, sort=[("_id", 1)])
        now_serving = now_serving_order["reference_number"] if now_serving_order else None

        # All queue orders sorted by oldest first
        queue_orders = list(db_orders.find({"queue_status": "queue"}).sort("_id", 1))

        # All skipped orders sorted by oldest first
        skip_orders = list(db_orders.find({"queue_status": "skipped"}).sort("_id", 1))

        # Current user’s reference number (if logged in or tracked in session)
        user_ref_num = session.get("ref_num")

        return render_template("queue.html",now_serving=now_serving,queue_orders=queue_orders,skip_orders=skip_orders,user_ref_num=user_ref_num,email=email_session)
    else:
        return render_template("queue.html")
