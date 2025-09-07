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
  
  user = session['user']['email']
  print(user)
  history = list(db_history.find({'email': user}).sort([("order_date", -1), ("order_time", -1)])) 
  return render_template('history.html', history=history)
