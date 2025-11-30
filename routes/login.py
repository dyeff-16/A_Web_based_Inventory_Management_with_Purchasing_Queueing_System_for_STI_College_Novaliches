from email.message import EmailMessage
import random
import smtplib
import requests
import bcrypt
from flask import jsonify, url_for, redirect, render_template, session, flash, request, Blueprint
from db_proware import *
from flask_bcrypt import Bcrypt
from flask import current_app
from datetime import datetime, timedelta, timezone

loginbp = Blueprint('login', __name__, url_prefix='/auth')

bcrypt = Bcrypt()

failed_otp_attempts = {}  # { 'IP': { 'count': int, 'last_attempt': datetime } }
failed_signup_attempts = {}  # { 'IP': { 'count': int, 'last_attempt': datetime } }
BLOCK_TIME = timedelta(minutes=5)
MAX_ATTEMPTS = 5


def check_role(required_role):
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    if session['user']['roles'] == required_role:
        return True 
    return False

@loginbp.route('/hasRead', methods=['POST'])
def hasRead():
    data = request.get_json()
    email = data.get('email')

    user = db_account.find_one({'email': email})

    if not user:
        return jsonify({'message': True})
    
    return jsonify({
        'exists': True,
        'hasRead': user.get('hasRead', False)
    })


@loginbp.route('/logout', methods=['GET','POST'])
def logout():
    if 'user' in session:
        print("logout user")
        session.pop('user')
    return redirect(url_for('dashboard'))

@loginbp.route('/resend_sms', methods=['POST'])
def resendSMS():
    if 'login_pending' not in session:
        return jsonify({'success': False, 'error': 'no_session'}), 401

    login_pending = session['login_pending']
    new_otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    login_pending['otp'] = new_otp
    session['login_pending'] = login_pending

    send_otp_sms(login_pending['number'], new_otp)
    print("New OTP:", new_otp)
    return jsonify({'success': True})

@loginbp.route('/resend_email', methods=['POST'])
def resendEmail():
    if 'login_pending' not in session:
        return jsonify({'success': False, 'error': 'no_session'}), 401

    login_pending = session['login_pending']
    new_otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    login_pending['otp'] = new_otp
    session['login_pending'] = login_pending

    send_otp_email(login_pending['email'], new_otp)
    print("New OTP:", new_otp)
    print(login_pending)
    return jsonify({'success': True})

@loginbp.route('/cancel_verification')
def cancel_verification():

    session.pop('login_pending', None)
    return redirect(url_for('login.login_')) 

@loginbp.route('/postLogin', methods=['POST'])
def login():

    if 'user' in session:
        return redirect(url_for('home'))

    if request.method == 'POST': 

        data = request.get_json()
        email = data.get('inputEmail')
        password = data.get('inputPassword')   
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
                    # return redirect(url_for('login.otp_force_change_password'))
                    return jsonify({
                        'change_force_password': True
                    })
                
                session['login_pending'] = {
                        'fullname': user['fullname'],
                        'number': user['number'],
                        'email': user['email'],
                        'student_id': user['student_id'],
                        'roles': user['roles'],
                        'otp_attempts': 0
                    }

                # send_otp_email(email, otp)
                # print("Login OTP sent")
                # return redirect(url_for('login.otp_verification_login'))
                return jsonify({
                    'login_pending': True
                })
            else:
                print("Incorrect password")

                return jsonify({
                    'message': "Incorrect password"
                })
        else:
            print('Account not found')
            return jsonify({
                    'message': "Incorrect Email"
                })

@loginbp.route("/login")
def login_():   
    if 'user' in session:
        return redirect(url_for('home'))

    return render_template('login.html')

@loginbp.route('/login-mfa', methods=['GET', 'POST'])
def MFA():

    if 'user' in session:
        return redirect(url_for('home'))
    
    if 'login_pending' not in session:
        return redirect(url_for('login.login_'))

    lp = session['login_pending']

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        sms_flag   = data.get('sms_otp')
        email_flag = data.get('email_otp')

        if sms_flag:
            otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
            lp['otp'] = otp
            lp['otp_created_at'] = datetime.utcnow().isoformat()
            session['login_pending'] = lp         
            number = lp.get('number')
           
            send_otp_sms(number, otp)
            
            print("SMS OTP Session:", session['login_pending'])
            return jsonify({'sms': True})

        if email_flag:
            otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
            lp['otp'] = otp
            lp['otp_created_at'] = datetime.utcnow().isoformat()
            session['login_pending'] = lp         
            email_addr = lp.get('email')           
          
            send_otp_email(email_addr, otp)
               
            print("EMAIL OTP Session:", session['login_pending'])
            return jsonify({'email': True})

        return jsonify({'error': 'bad_request'}), 400


    return render_template('MFA_choices.html')

@loginbp.route('/otpValidationLogin', methods=['GET', 'POST'])
def otpValidationLogin():

    if 'user' in session:
        return redirect(url_for('home'))

    login_pending = session.get('login_pending')
    if not login_pending:
        print('Session expired. Please login again.')
        return redirect(url_for('login.login_'))

    ip = request.remote_addr
    now = datetime.utcnow()

    # Block IP if too many failed attempts
    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                print('Too many failed attempts. Try again later.')
                return jsonify({
                    'back_to_login': True,
                    'message': 'Too many failed attempts. Try again later.'
                })
            else:
                # Reset block after BLOCK_TIME
                failed_otp_attempts.pop(ip)

    if request.method == 'POST':
        data = request.get_json()
        user_otp = data.get('inputOTP')
        otp_time = datetime.fromisoformat(login_pending['otp_created_at'])
        timer = (datetime.utcnow() - otp_time).total_seconds()

        if datetime.utcnow() - otp_time > timedelta(minutes=5):
            #mag pop ung session pag naubos ung time
            session.pop('login_pending')
            print('OTP expired. Please login again.')
            return jsonify({
                'back_to_login': True,
                'message': 'OTP expired. Please login again.'
            })


        if login_pending['otp_attempts'] >= 5:
            #mag pop ung session pag naubos attempts
            session.pop('login_pending')
            print('Too many attempts. Please login again.')
            return jsonify({
                'back_to_login', True,
                'message' 'Too many attempts. Please login again.'
            }) 

        if user_otp == login_pending['otp']:
            session['user'] = {
                'fullname': login_pending['fullname'],
                'email': login_pending['email'],
                'student_id': login_pending['student_id'],
                'roles': login_pending['roles'],
            }
            #tugma otp mag pop login pending sa otp
            session.pop('login_pending')
            user = session.get('user')
            # Reset ip failure count on success
            failed_otp_attempts.pop(ip, None)
            return jsonify({
                'success': True,
                'roles': user['roles']
            })

        else:
            login_pending['otp_attempts'] += 1
            session['login_pending'] = login_pending
            print('Invalid OTP. Try again.')

            # Track ip failed attempts
            failed_otp_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_otp_attempts[ip]['count'] += 1
            failed_otp_attempts[ip]['last_attempt'] = now
        
            return jsonify({
            'message' : 'Invalid OTP. Try again.'
            })
         
@loginbp.route('/otp_login', methods=['GET', 'POST'])
def otp_verification_login():
    if 'user' in session:
        return redirect(url_for('home'))
    
    if 'login_pending' not in session:
        return redirect(url_for('login.login_'))
    
    lp = session.get('login_pending')
    otp_created = lp.get('otp_created_at')

    if not otp_created:
        print(lp)
        return redirect(url_for('login.MFA'))

    
    login_pending = session.get('login_pending')
    otpEmail = login_pending['email']
    otp_time = datetime.fromisoformat(login_pending['otp_created_at'])
    elapsed = (datetime.utcnow() - otp_time).total_seconds()
    remaining = max(0, 300 - int(elapsed)) 

    return render_template('otp_login.html', timer=remaining, email=otpEmail)

@loginbp.route('/sms_otp', methods=['GET', 'POST'])
def smsValidationLogin():
    if 'user' in session:
        return redirect(url_for('home'))

    login_pending = session.get('login_pending')
    if not login_pending:
        print('Session expired. Please login again.')
        return redirect(url_for('login.login_'))

    ip = request.remote_addr
    now = datetime.utcnow()

    # Block IP if too many failed attempts
    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                print('Too many failed attempts. Try again later.')
                return jsonify({
                    'back_to_login': True,
                    'message': 'Too many failed attempts. Try again later.'
                })
            else:
                # Reset block after BLOCK_TIME
                failed_otp_attempts.pop(ip)

    if request.method == 'POST':
        data = request.get_json()
        user_otp = data.get('inputOTP')
        otp_time = datetime.fromisoformat(login_pending['otp_created_at'])
        timer = (datetime.utcnow() - otp_time).total_seconds()

        if datetime.utcnow() - otp_time > timedelta(minutes=5):
            #mag pop ung session pag naubos ung time
            session.pop('login_pending')
            print('OTP expired. Please login again.')
            return jsonify({
                'back_to_login': True,
                'message': 'OTP expired. Please login again.'
            })


        if login_pending['otp_attempts'] >= 5:
            #mag pop ung session pag naubos attempts
            session.pop('login_pending')
            print('Too many attempts. Please login again.')
            return jsonify({
                'back_to_login', True,
                'message' 'Too many attempts. Please login again.'
            }) 

        if user_otp == login_pending['otp']:
            session['user'] = {
                'fullname': login_pending['fullname'],
                'email': login_pending['email'],
                'student_id': login_pending['student_id'],
                'roles': login_pending['roles'],
            }
            #tugma otp mag pop login pending sa otp
            session.pop('login_pending')
            user = session.get('user')
            # Reset ip failure count on success
            failed_otp_attempts.pop(ip, None)
            return jsonify({
                'success': True,
                'roles': user['roles']
            })

        else:
            login_pending['otp_attempts'] += 1
            session['login_pending'] = login_pending
            print('Invalid OTP. Try again.')

            # Track ip failed attempts
            failed_otp_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_otp_attempts[ip]['count'] += 1
            failed_otp_attempts[ip]['last_attempt'] = now
        
            return jsonify({
            'message' : 'Invalid OTP. Try again.'
            })
        
@loginbp.route('sms_login', methods=['GET', 'POST'])
def sms_otp():
    if 'user' in session:
        return redirect(url_for('home'))
    
    if 'login_pending' not in session:
        return redirect(url_for('login.login_'))
    
    login_pending = session.get('login_pending')
    number = str(login_pending.get('number', ''))   # ensure string

  
    last4 = number[-4:] if len(number) >= 4 else number
    masked_number = '*' * max(0, len(number) - 4) + last4
    otp_time = datetime.fromisoformat(login_pending['otp_created_at'])
    elapsed = (datetime.utcnow() - otp_time).total_seconds()
    remaining = max(0, 300 - int(elapsed)) 

    return render_template('otp_sms.html', timer=remaining, number=masked_number)

@loginbp.route("/enter_info", methods=['GET', 'POST'])
def info():

    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')

        acc = db_account.find_one({'email': email})
        if acc:            
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            session['otp_pending'] = {'email': email, 'otp': otp, 'otp_created_at': datetime.utcnow().isoformat()}
            send_otp_email(email, otp)
            flash("OTP has been sent to your email.")
            return jsonify({'success': True})
        else:
            return jsonify({'message': 'account not found'})

    return render_template("info.html")

@loginbp.route('/otp_verify_password', methods=['GET', 'POST'])
def otp_VerifyPassword():
    if 'otp_pending' not in session:
        return redirect(url_for('login.info'))
    
    session_email = session['otp_pending']
    otp_time = datetime.fromisoformat(session_email['otp_created_at'])
    elapsed = (datetime.utcnow() - otp_time).total_seconds()
    remaining = max(0, 300 - int(elapsed)) 
    ip = request.remote_addr
    now = datetime.utcnow()

    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                block_time_left = BLOCK_TIME - (now - attempt_info['last_attempt'])
                block_minutes = block_time_left.seconds // 60
                block_seconds = block_time_left.seconds % 60
                message = f'Too many failed attempts. Your IP is blocked for {block_minutes} minutes and {block_seconds} seconds. Please try again later.'
                return jsonify({ 'message': message})
            else:
                failed_otp_attempts.pop(ip)

    if request.method == 'POST':

        data = request.get_json()
        user_otp = data.get('inputOTP')

        otp_data = session['otp_pending']

        if user_otp == otp_data['otp']:
            session['usr_resetpassword'] = {'email': otp_data['email']}
            session.pop('otp_pending', None)
            failed_otp_attempts.pop(ip, None)  

            return jsonify({'success': True})
        else:
            failed_otp_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_otp_attempts[ip]['count'] += 1
            failed_otp_attempts[ip]['last_attempt'] = now

            return jsonify({'message': 'invalid code'})
        
    return render_template("otp_ResetPassword.html", email=session_email['email'], timer=remaining)

@loginbp.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    
    if 'usr_resetpassword' not in session:
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

    if "pending_change_password" not in session:
        return redirect(url_for("login.login_"))
    
    pending_cpass = session['pending_change_password']
    otp_time = datetime.fromisoformat(pending_cpass['otp_created_at'])
    elapsed = (datetime.utcnow() - otp_time).total_seconds()
    remaining = max(0, 300 - int(elapsed)) 
    print(pending_cpass)
    ip = request.remote_addr
    now = datetime.utcnow()

    if ip in failed_otp_attempts:
        attempt_info = failed_otp_attempts[ip]
        if attempt_info['count'] >= MAX_ATTEMPTS:
            if now - attempt_info['last_attempt'] < BLOCK_TIME:
                block_time_left = BLOCK_TIME - (now - attempt_info['last_attempt'])
                block_minutes = block_time_left.seconds // 60
                block_seconds = block_time_left.seconds % 60
                message = f'Too many failed attempts. Your IP is blocked for {block_minutes} minutes and {block_seconds} seconds. Please try again later.'
                return jsonify({ 'message': message})
            else:
                failed_otp_attempts.pop(ip)

    if request.method == 'POST':
        data = request.get_json()
        user_otp = data.get('inputOTP')
        otp_data = session['pending_change_password']

        if user_otp == otp_data['otp']:

            session['pending_change_password'] = {'email': otp_data['email']}
            failed_otp_attempts.pop(ip, None)  
            return jsonify({'success': True})
        else:
        
            failed_otp_attempts.setdefault(ip, {'count': 0, 'last_attempt': now})
            failed_otp_attempts[ip]['count'] += 1
            failed_otp_attempts[ip]['last_attempt'] = now
            return jsonify({'message': 'invalid code'})

    return render_template("otp_f_change_pass.html", email=pending_cpass['email'], timer=remaining )

@loginbp.route("/force_change_password", methods=["GET", "POST"])
def force_change_password():
    # Make sure user is in pending_change_password session
    if "pending_change_password" not in session:
        return redirect(url_for("login.login_"))

    user_data = session["pending_change_password"]
    email = user_data["email"]
    number = request.form.get('number')

    if request.method == "POST":
        new_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or not confirm_password:
            flash("Please fill in all fields.")
            return render_template("change_password.html")

        if new_password != confirm_password:
            flash("Passwords do not match.")
            return render_template("change_password.html")

        db_account.update_one(
            {"email": email},
            {
                "$set": {
                    "password": new_password,  
                    "force_change_password": False,
                    'hasRead': True,
                    "number": number
                }
            }
        )

        # Clear session
        session.pop("pending_change_password", None)

        flash("Password updated successfully. Please login again.")
        return redirect(url_for("login.login_"))

    return render_template("change_password.html")

# @loginbp.route('/login_admin')
# def login_admin():
#     return render_template('login_admin.html')

@loginbp.route('/signupPost', methods=['POST'])
def signup_post():
    data = request.get_json() or {}
    
    email = (data.get('inputEmail') or '').strip()
    password = data.get('inputPassword') or ''
    code = (data.get('inputCode') or '').strip().lower()
    number = data.get('inputNumber')

    if not email or not password or not code or not number:
        return jsonify({'message': 'All fields are required'}), 400

    if not email.endswith("@novaliches.sti.edu.ph"):
        return jsonify({'message': 'STI Novaliches account required'}), 400
    
    if code != "stiadmin2025":
        return jsonify({'message': 'Invalid invite code'}), 400
    
    db_account_pending.insert_one({
        'email': email,
        'password': password,
        'student_id': 1,
        'roles': 'admin',
        'number': int(number),
        'force_change_password': False,
        'status': 'active'
    })
    return jsonify({'success': True, 'message': 'Admin account created successfully'})

@loginbp.route('/signup',methods=['GET'])
def signup():

    return render_template('signup.html')


def send_otp_sms(number, otp):
    API_TOKEN = '4fcbae81935679f94bf6179b6a1d3114aabb2825'
    message = f'Your One Time Password in Stiprowarenovaliches: {otp}' 

    url = 'https://sms.iprogtech.com/api/v1/sms_messages'

    payload = {
        "api_token"   : API_TOKEN,
        "phone_number": number,
        "message"     : message
    }

    resp = requests.post(url, json=payload)
    print("Response JSON:", resp.json())

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
