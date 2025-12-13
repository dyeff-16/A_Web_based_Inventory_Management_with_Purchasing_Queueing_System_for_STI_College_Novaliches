from flask import Blueprint, redirect, render_template, session, url_for
from db_proware import db_orders

queuebp = Blueprint('queue', __name__, url_prefix='/queue')

@queuebp.route("/queue_user", methods=["GET"])
def queue_user():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    status_doc = db_orders.find_one() or {"queue_started": False}
    queue_started = status_doc.get("queue_started", False)

    if queue_started:
        user_session = session['user']
        email_session = user_session['email']

        now_serving_order = db_orders.find_one({'status': 'Paid',"queue_status": "queue"}, sort=[("_id", 1)])
        now_serving = now_serving_order["reference_number"] if now_serving_order else None

        queue_orders = list(db_orders.find({'status': 'Paid',"queue_status": "queue"}).sort("_id", 1))
        skip_orders = list(db_orders.find({'status': 'Paid',"queue_status": "skipped"}).sort("_id", 1))

        user_ref_num = session.get("ref_num")

        return render_template("queue.html",
                               now_serving=now_serving,
                               queue_orders=queue_orders,
                               skip_orders=skip_orders,
                               user_ref_num=user_ref_num,
                               email=email_session)
    else:
        return render_template("queue.html")