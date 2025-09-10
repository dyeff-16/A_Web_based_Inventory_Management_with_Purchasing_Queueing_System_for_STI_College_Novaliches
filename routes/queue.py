from flask import Blueprint, render_template, session
from db_proware import db_orders

queuebp = Blueprint('queue', __name__, url_prefix='/queue')

@queuebp.route("/", methods=["GET"])
def queue_view():
    # Find the first order in the queue (now serving)
    now_serving_order = db_orders.find_one({"queue_status": "queue"}, sort=[("_id", 1)])
    now_serving = now_serving_order["reference_number"] if now_serving_order else None

    # All queue orders sorted by oldest first
    queue_orders = list(db_orders.find({"queue_status": "queue"}).sort("_id", 1))

    # All skipped orders sorted by oldest first
    skip_orders = list(db_orders.find({"queue_status": "skipped"}).sort("_id", 1))

    # Current user’s reference number (if logged in or tracked in session)
    user_ref_num = session.get("ref_num")

    return render_template(
        "queue.html",
        now_serving=now_serving,
        queue_orders=queue_orders,
        skip_orders=skip_orders,
        user_ref_num=user_ref_num
    )
