from flask import Blueprint, render_template, redirect, url_for, request
from bson.objectid import ObjectId
from datetime import datetime
from db_proware import db_orders

queuebp = Blueprint('queue', __name__)  # changed name from 'orders' → 'queue'

from flask import session, redirect, url_for

@queuebp.route('/queue', methods=['GET', 'POST'])
def queue_view():
    if request.method == 'POST':
        if 'start' in request.form:
            session['queue_started'] = True
            db_orders.update_many({}, {'$set': {'queue_status': "queue"}})
        elif 'stop' in request.form:
            session.pop('queue_started', None)
        return redirect(url_for('queue.queue_view'))

    queue_started = session.get('queue_started', False)

    queue_orders = []
    skip_orders = []

    if queue_started:
        queue_orders = list(db_orders.find({"queue_status": "queue"}).sort("_id", 1))
        skip_orders = list(db_orders.find({"queue_status": "skipped"}).sort("_id", 1))

    return render_template("queue.html",
                           queue_started=queue_started,
                           queue_orders=queue_orders,
                           skip_orders=skip_orders)



@queuebp.route('/queue_done', methods=['POST'])
def queue_done():
    ref_num = request.form.get('ref_num')
    if ref_num:
        db_orders.update_one(
            {"reference_number": ref_num},
            {"$set": {"queue_status": "done"}}
        )
    return redirect(url_for('queue.queue_view'))


@queuebp.route('/queue_skip', methods=['POST'])
def queue_skip():
    ref_num = request.form.get('ref_num')
    if ref_num:
        db_orders.update_one(
            {"reference_number": ref_num},
            {"$set": {"queue_status": "skipped"}}
        )
    return redirect(url_for('queue.queue_view'))
