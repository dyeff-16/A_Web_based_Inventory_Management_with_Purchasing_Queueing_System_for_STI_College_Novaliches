import base64
from flask import Blueprint, Flask, url_for, redirect, render_template, session, flash, request
from db_proware import *


notifbp= Blueprint('notif', __name__, url_prefix='/notification')

@notifbp.route('/notificaiton')
def notification():
  if 'user' not in session:
        return redirect(url_for('login.login_'))
  
  user = session['user']['email']
  print(user)
  notif = list(db_notification.find({'email': user}).sort([("order_date", -1), ("order_time", -1)])) 
  return render_template('notification.html', notification=notif)

@notifbp.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    user_email = session['user']['email']
    selected_status = request.args.get('status', 'placed_order')  # default = show all

    # Build query
    query = {"email": user_email}
    if selected_status == 'placed_order': 
        query["status"] = "placed_order"
        history_data = list(db_orders.find(query).sort([("order_date", -1), ("order_time", -1)]))
    elif selected_status == 'paid':
        query["status"] = "paid"
        history_data = list(db_orders.find(query).sort([("order_date", -1), ("order_time", -1)]))
    elif selected_status == 'claim':
        query["status"] = "claim"
        history_data = list(db_orders.find(query).sort([("order_date", -1), ("order_time", -1)]))
    elif selected_status == "history":
        history_data = list(db_history.find(query).sort([("order_date", -1), ("order_time", -1)]))


    return render_template(
        "history.html",
        history=history_data,
        selected_status=selected_status
    )
@notifbp.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    ref_number = request.form.get('ref_number')
    file = request.files.get('img_receipt')

    if file and ref_number:
        # Convert file to base64
        receipt_b64 = base64.b64encode(file.read()).decode('utf-8')

        db_orders.update_one(
            {"reference_number": ref_number, "email": session['user']['email']},
            {"$set": {"receipt": receipt_b64}}
        )
        flash("Receipt uploaded successfully!", "success")

    return redirect(url_for('notif.history', status='placed_order'))
