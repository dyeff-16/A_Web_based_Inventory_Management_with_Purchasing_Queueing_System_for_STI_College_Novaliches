from email.message import EmailMessage
import random
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


def check_role(required_role):
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    if session['user']['roles'] == required_role:
        return True 
    return False

@loginbp.route("/login", methods=['POST', 'GET'])
def login_():   
    if 'user' in session:
        return redirect(url_for('home'))

    termsadcondition = db_info.find_one({"info": "terms and condition"})
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
        email = request.form['email']
        password = request.form['password']        
        user = db_account.find_one({ "email" : email})
        if user:
            # if bcrypt.check_password_hash(user['password'], password):
            if password == user['password']:
                if user.get('force_change_password', False):
                    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

                    session['pending_change_password'] = {
                        'email': email,   
                        'otp': otp,
                        'otp_created_at': datetime.utcnow().isoformat(),
                        'otp_attempts': 0
                    }
                    send_otp_email(user['email'], otp)
                    return redirect(url_for('login.otp_force_change_password'))
                
                otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                session['login_pending'] = {
                        'fullname': user['fullname'],
                        'email': user['email'],
                        'student_id': user['student_id'],
                        'roles': user['roles'],
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

    return render_template('login.html', tc=termsadcondition)

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
                'roles': login_pending['roles'],
            }
            session.pop('login_pending')

            # Reset IP failure count on success
            failed_otp_attempts.pop(ip, None)
            check_roles_user = check_role("student")
            check_roles_admin = check_role("admin")
            check_roles_system_admin = check_role("system_admin")
            
            if check_roles_user:
                return redirect(url_for('home'))
            elif check_roles_admin:
                return redirect(url_for('admin'))
            elif check_roles_system_admin:
                return redirect(url_for('system_admin'))

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
    return redirect(url_for('dashboard'))

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

@loginbp.route("/enter_info", methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        info_value = request.form.get('info_')

        acc = db_account.find_one({'email': info_value})
        if acc:            
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            session['otp_pending'] = {'email': info_value, 'otp': otp}
            send_otp_email(info_value, otp)
            flash("OTP has been sent to your email.")
            return redirect(url_for('login.otp_VerifyPassword'))
        else:
            return render_template("info.html")

    return render_template("info.html")

@loginbp.route('/otp_verify_password', methods=['GET', 'POST'])
def otp_VerifyPassword():
    if 'otp_pending' not in session:
        flash("Session expired. Please start again.")
        return redirect(url_for('login.info'))

    ip = request.remote_addr
    now = datetime.utcnow()

    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                block_time_left = BLOCK_TIME - (now - attempt_info['last_attempt'])
                block_minutes = block_time_left.seconds // 60
                block_seconds = block_time_left.seconds % 60
                flash(f'Too many failed attempts. Your IP is blocked for {block_minutes} minutes and {block_seconds} seconds. Please try again later.')
                return render_template("otp_ResetPassword.html")
            else:
                failed_otp_attempts.pop(ip)

    if request.method == 'POST':
        user_otp = request.form.get('otp_verification')
        otp_data = session['otp_pending']

        if user_otp == otp_data['otp']:
            session['usr_resetpassword'] = {'email': otp_data['email']}
            session.pop('otp_pending', None)
            failed_otp_attempts.pop(ip, None)  
            flash("OTP verified successfully. Please reset your password.")
            return redirect(url_for('login.reset_password'))
        else:
            flash("Invalid OTP. Please try again.")
            failed_otp_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_otp_attempts[ip]['count'] += 1
            failed_otp_attempts[ip]['last_attempt'] = now

    return render_template("otp_ResetPassword.html")

@loginbp.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if 'usr_resetpassword' not in session:
        flash("Unauthorized access.")
        return redirect(url_for('login.info'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("reset_password.html")

        email = session['usr_resetpassword']['email']
        db_account.update_one({"email": email}, {"$set": {"password": confirm_password}})

        session.pop('usr_resetpassword', None)
        flash("Password reset successful. Please log in.")
        return redirect(url_for('login.login_'))

    return render_template("reset_password.html")

@loginbp.route('/otp_force_change_password', methods=['POST','GET'])
def otp_force_change_password():
    if 'pending_change_password' not in session:
        flash("Session expired. Please start again.")
        return redirect(url_for('login.info'))
    
    ip = request.remote_addr
    now = datetime.utcnow()

    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                block_time_left = BLOCK_TIME - (now - attempt_info['last_attempt'])
                block_minutes = block_time_left.seconds // 60
                block_seconds = block_time_left.seconds % 60
                flash(f'Too many failed attempts. Your IP is blocked for {block_minutes} minutes and {block_seconds} seconds. Please try again later.')
                return render_template("otp_f_change_pass.html")
            else:
                failed_otp_attempts.pop(ip)

    if request.method == 'POST':
        user_otp = request.form.get('otp_verification')
        otp_data = session['pending_change_password']

        if user_otp == otp_data['otp']:
            session['pending_change_password'] = {'email': otp_data['email']}
            failed_otp_attempts.pop(ip, None)  
            flash("OTP verified successfully. Please reset your password.")
            return redirect(url_for('login.force_change_password'))
        else:
            flash("Invalid OTP. Please try again.")
            failed_otp_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_otp_attempts[ip]['count'] += 1
            failed_otp_attempts[ip]['last_attempt'] = now
    return render_template("otp_f_change_pass.html")

@loginbp.route("/force_change_password", methods=["GET", "POST"])
def force_change_password():
    # Make sure user is in pending_change_password session
    if "pending_change_password" not in session:
        flash("Session expired. Please login again.")
        return redirect(url_for("login.login_"))

    user_data = session["pending_change_password"]
    email = user_data["email"]

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or not confirm_password:
            flash("Please fill in all fields.")
            return render_template("change_password.html")

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return render_template("change_password.html")

        # ✅ Update password in MongoDB
        db_account.update_one(
            {"email": email},
            {
                "$set": {
                    "password": new_password,   # you can hash it with bcrypt or werkzeug if needed
                    "force_change_password": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Clear session
        session.pop("pending_change_password", None)

        flash("Password updated successfully. Please login again.")
        return redirect(url_for("login.login_"))

    return render_template("change_password.html")

