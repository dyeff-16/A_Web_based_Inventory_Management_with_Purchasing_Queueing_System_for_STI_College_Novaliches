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
    selected_status = request.args.get('status', 'history')  # default to 'history'

    # Map status names from the frontend to database values
    status_map = {
        'placed order': 'placed order',
        'paid': 'Paid',
        'completed': 'Completed',
        'history': None  
    }

    # Build query
    query = {'email': user_email}
    if status_map[selected_status]:
        query['status'] = status_map[selected_status]

    history_data = list(
        db_history.find(query).sort([("order_date", -1), ("order_time", -1)])
    )

    return render_template(
        'history.html',
        history=history_data,
        selected_status=selected_status
    )

