import base64
from datetime import datetime
from flask import Blueprint, jsonify, url_for, redirect, render_template, session, flash, request
import pytz
from db_proware import *


notifbp = Blueprint('notif', __name__, url_prefix='/notification')

@notifbp.route('/notificaiton')
def notification():
  if 'user' not in session:
        return redirect(url_for('login.login_'))
  
  user = session['user']['email']
  print(user)
  notif = list(db_notification.find({'email': user}).sort([("order_date", -1), ("order_time", -1)]))
  db_notification.update_many(
          {'email': user, 'unread': True},
          {'$set': {'unread': False}}
      )
  return render_template('notification.html', notification=notif)

@notifbp.route('/getNotif', methods=['GET','POST'])
def getNotif():
    
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    user = session['user']['email']
    notif = db_notification.find({'email': user})
    notify = False

    for notification in notif:
        if notification.get('unread'):
              notify = True
              break
    
    return jsonify({'notif': notify})
