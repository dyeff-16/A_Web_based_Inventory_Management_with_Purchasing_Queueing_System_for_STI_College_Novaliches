from flask import Blueprint, render_template, redirect, url_for, request
from datetime import datetime
from db_proware import db_orders

queueadminbp = Blueprint('queue_admin', __name__)  

from flask import session, redirect, url_for

@queueadminbp.route('/queue', methods=['GET', 'POST'])
def queue_view():
    if request.method == 'POST':
        if 'start' in request.form:
            db_orders.update_one({}, {"$set": {"queue_started": True}}, upsert=True)
            db_orders.update_many({'status': 'Paid',}, {'$set': {'queue_status': "queue"}})
        elif 'stop' in request.form:
            db_orders.update_one({}, {"$set": {"queue_started": False}}, upsert=True)
        return redirect(url_for('queue_admin.queue_view'))

    status_doc = db_orders.find_one() or {"queue_started": False}
    queue_started = status_doc.get("queue_started", False)

    queue_orders = []
    skip_orders = []

    if queue_started:
        queue_orders = list(db_orders.find({'status': 'Paid',"queue_status": "queue"}).sort("_id", 1))
        skip_orders = list(db_orders.find({'status': 'Paid',"queue_status": "skipped"}).sort("_id", 1))

    return render_template("admin/queue.html",
                           queue_started=queue_started,
                           queue_orders=queue_orders,
                           skip_orders=skip_orders)



@queueadminbp.route('/queue_done', methods=['POST'])
def queue_done():
    ref_num = request.form.get('ref_num')
    if ref_num:
        db_orders.update_one(
            {"reference_number": ref_num},
            {"$set": {"queue_status": "done", 'status': 'Claimed'}}
        )
    return redirect(url_for('queue_admin.queue_view'))


@queueadminbp.route('/queue_skip', methods=['POST'])
def queue_skip():
    ref_num = request.form.get('ref_num')
    if ref_num:
        db_orders.update_one(
            {"reference_number": ref_num},
            {"$set": {"queue_status": "skipped"}}
        )
    return redirect(url_for('queue_admin.queue_view'))
