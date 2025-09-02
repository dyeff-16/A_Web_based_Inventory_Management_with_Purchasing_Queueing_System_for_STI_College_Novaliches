from email.message import EmailMessage
import random
import re
import smtplib
import bcrypt
from flask import Flask, url_for, redirect, render_template, session, flash, request, Blueprint
from db_proware import *
from flask_bcrypt import Bcrypt
from flask import current_app
from datetime import datetime, timedelta

loginbp = Blueprint('login', __name__, url_prefix='/auth')

bcrypt = Bcrypt()

failed_otp_attempts = {}  # { 'IP': { 'count': int, 'last_attempt': datetime } }
failed_signup_attempts = {}  # { 'IP': { 'count': int, 'last_attempt': datetime } }
BLOCK_TIME = timedelta(minutes=10)
MAX_ATTEMPTS = 5

@loginbp.route("/login", methods=['POST', 'GET'])
def login_():   
    if 'user' in session:
        return redirect(url_for('home'))

    ip = request.remote_addr
    now = datetime.utcnow()

    # Block IP if too many failed attempts
    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                block_time_left = BLOCK_TIME - (now - attempt_info['last_attempt'])
                block_minutes = block_time_left.seconds // 60
                block_seconds = block_time_left.seconds % 60
                flash(f'Too many failed attempts. Your IP is blocked for {block_minutes} minutes and {block_seconds} seconds. Please try again later.')
                return render_template('login.html')
            else:
                # Reset block after BLOCK_TIME
                failed_otp_attempts.pop(ip)

    if request.method == 'POST': 
        email = request.form['email_']
        password = request.form['password_']        
        user = db_account.find_one({ "email" : email})

        if user:
            # if bcrypt.check_password_hash(user['password'], password):
            if password == user['password']:
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                session['login_pending'] = {
                        'fullname': user['fullname'],
                        'email': user['email'],
                        'student_id': user['std_id'],
                        'role': user['role'],
                        'otp': otp,
                        'otp_created_at': datetime.utcnow().isoformat(),
                        'otp_attempts': 0
                    }

                send_otp_email(email, otp)
                print("Login OTP sent")
                return redirect(url_for('login.otp_verification_login'))
            else:
                print("Incorrect password")
                flash('Incorrect email or password')
        else:
            print('Account not found')
            flash('Incorrect email or password')

    return render_template('login.html')

@loginbp.route('/otp_login', methods=['GET', 'POST'])
def otp_verification_login():
    if 'user' in session:
        return redirect(url_for('home'))

    login_pending = session.get('login_pending')
    if not login_pending:
        flash('Session expired. Please login again.')
        return redirect(url_for('login.login_'))

    ip = request.remote_addr
    now = datetime.utcnow()

    # Block IP if too many failed attempts
    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                flash('Too many failed attempts from your IP. Try again later.')
                return render_template('otp_login.html')  # Render the page instead of redirecting
            else:
                # Reset block after BLOCK_TIME
                failed_otp_attempts.pop(ip)

    if request.method == 'POST':
        user_otp = request.form['otp_verification']
        otp_time = datetime.fromisoformat(login_pending['otp_created_at'])

        if datetime.utcnow() - otp_time > timedelta(minutes=5):
            session.pop('login_pending')
            flash('OTP expired. Please login again.')
            return render_template('otp_login.html')  # Render the page instead of redirecting

        if login_pending['otp_attempts'] >= 5:
            session.pop('login_pending')
            flash('Too many attempts. Please login again.')
            return render_template('otp_login.html')  # Render the page instead of redirecting

        if user_otp == login_pending['otp']:
            session['user'] = {
                'fullname': login_pending['fullname'],
                'email': login_pending['email'],
                'student_id': login_pending['student_id'],
                'role': login_pending['role'],
            }
            session.pop('login_pending')

            # Reset IP failure count on success
            failed_otp_attempts.pop(ip, None)

            return redirect(url_for('home'))
        else:
            login_pending['otp_attempts'] += 1
            session['login_pending'] = login_pending
            flash('Invalid OTP. Try again.')

            # Track IP failed attempts
            failed_otp_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_otp_attempts[ip]['count'] += 1
            failed_otp_attempts[ip]['last_attempt'] = now

    return render_template('otp_login.html')

@loginbp.route('/logout', methods=['GET','POST'])
def logout():
    if 'user' in session:
        print("logout user")
        session.pop('user')
    return redirect(url_for('home'))

# @loginbp.route('/signup', methods=['POST', 'GET'])
# def signup():
#     if 'user' in session:
#         return redirect(url_for('home'))

#     ip = request.remote_addr
#     now = datetime.utcnow()

#     # Block IP if too many failed attempts
#     if ip in failed_signup_attempts:
#         attempt_info = failed_signup_attempts[ip]
#         if attempt_info['count'] >= MAX_ATTEMPTS:
#             if now - attempt_info['last_attempt'] < BLOCK_TIME:
#                 block_time_left = BLOCK_TIME - (now - attempt_info['last_attempt'])
#                 block_minutes = block_time_left.seconds // 60
#                 block_seconds = block_time_left.seconds % 60
#                 flash(f'Too many failed attempts. Your IP is blocked for {block_minutes} minutes and {block_seconds} seconds. Please try again later.')
#                 return render_template('signup.html')
#             else:
#                 # Reset block after BLOCK_TIME
#                 failed_signup_attempts.pop(ip)

#     if request.method == 'POST':
#         fullname = request.form['full_name']
#         email = request.form['email']
#         std_id = request.form['student_id']
#         password = request.form['password']
#         confirmpassword = request.form['confirm_password']
        
#         find_acc = db_account.find_one({'email': email, 'std_id': std_id})
        
#         allowed_domain = r'^[a-zA-Z0-9._%+-]+@novaliches\.sti\.edu\.ph$'
#         if not re.match(allowed_domain, email):
#             flash('Please use your @novaliches.sti.edu.ph student email.')
#             return render_template('signup.html')
        
#         if find_acc:
#             flash('Email already exists. Please use a different email or student ID.')
#             return render_template("signup.html")
        
#         if password != confirmpassword:
#             flash("Passwords do not match")
#             return render_template("signup.html")
        
#         otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])   
#         session['pending_user'] = {
#             'fullname': fullname,
#             'email': email,
#             'password': bcrypt.generate_password_hash(password).decode('utf-8'),
#             'std_id': std_id,
#             'role': 'user',
#             'otp': otp,
#             'otp_created_at': datetime.utcnow().isoformat(),
#             'otp_attempts': 0
#         }

#         send_otp_email(email, otp)
#         print("Signup OTP sent")
#         return redirect(url_for('login.otp_verification'))  # Redirect to OTP verification page

#     return render_template('signup.html')

@loginbp.route('/otp_verify', methods=['GET', 'POST'])
def otp_verification():
    if 'user' in session:
        return redirect(url_for('home'))

    signup_pending = session.get('pending_user')
    if not signup_pending:
        flash('Session expired. Please sign up again.')
        return redirect(url_for('login.signup'))

    ip = request.remote_addr
    now = datetime.utcnow()

    # Block IP if too many failed attempts
    if ip in failed_signup_attempts:
        attempt_info = failed_signup_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                flash('Too many failed attempts from your IP. Try again later.')
                return render_template('otp_verify.html')  # Render the page instead of redirecting
            else:
                # Reset block after BLOCK_TIME
                failed_signup_attempts.pop(ip)

    if request.method == 'POST':
        user_otp = request.form['otp_verification']
        otp_time = datetime.fromisoformat(signup_pending['otp_created_at'])

        if datetime.utcnow() - otp_time > timedelta(minutes=5):
            session.pop('pending_user')
            flash('OTP expired. Please sign up again.')
            return render_template('otp_verify.html')  # Render the page instead of redirecting

        if signup_pending['otp_attempts'] >= 5:
            session.pop('pending_user')
            flash('Too many attempts. Please sign up again.')
            return render_template('otp_verify.html')  # Render the page instead of redirecting

        if user_otp == signup_pending['otp']:
            # Save user to the database
            db_account.insert_one({
                'fullname': signup_pending['fullname'],
                'email': signup_pending['email'],
                'std_id': signup_pending['std_id'],
                'password': signup_pending['password'],
                'role': signup_pending['role']
            })

            session.pop('pending_user')

            # Reset IP failure count on success
            failed_signup_attempts.pop(ip, None)

            flash('Signup successful! Please login to continue.')
            return redirect(url_for('login.login_'))
        else:
            signup_pending['otp_attempts'] += 1
            session['pending_user'] = signup_pending
            flash('Invalid OTP. Try again.')

            # Track IP failed attempts
            failed_signup_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_signup_attempts[ip]['count'] += 1
            failed_signup_attempts[ip]['last_attempt'] = now

    return render_template('otp_verify.html')

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg['Subject'] = 'Proware OTP verification'
    msg['From'] = current_app.config['EMAIL_USER']
    msg['To'] = to_email
    msg.set_content(f"""Good day!

Thank you for using STI ProWare!

Warning: Do not give this to anyone. This code can be used to login to your account.

Your One-Time Password (OTP) is given below. It is valid for the next 5 minutes.

One-Time Password (OTP): {otp}

If you did not request this code, please disregard this message.

Warm regards,
ProWare
""")


    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(current_app.config['EMAIL_USER'], current_app.config['EMAIL_PASSWORD'])
        server.send_message(msg)

