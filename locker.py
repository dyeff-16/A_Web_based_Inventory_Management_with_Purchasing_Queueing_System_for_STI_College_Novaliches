from email.message import EmailMessage
import random
import smtplib
from flask import Flask, flash, render_template, url_for, request, redirect, session
from flask_bcrypt import Bcrypt
from flask_wtf import RecaptchaField
from pymongo import MongoClient
from datetime import datetime, timedelta
import requests

#flask
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=1)
#bcrypt
bcrypt = Bcrypt(app) 
#Mongodb
dbClient = MongoClient('localhost', 27017)

#secret key daw
app.secret_key = '05162003abcd'
#Mongodb database securevault
database_securevault= dbClient.securevault
#Collections of database securevault
database_account = database_securevault.account
database_admin = database_securevault.admin
dashboard_report = database_securevault.dashboard_reports
id_repository = database_securevault.id_repository
database_locker = database_securevault.locker_num
database_history_user = database_securevault.history

recaptcha = RecaptchaField()
# reCAPTCHA configuration
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdkReYpAAAAACzrIbQVt1omiOBsjfVgMyK2ZZHC'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdkReYpAAAAAOPwF_86-3pyGbJGTC4y24Im8py9'
app.config['EMAIL_USER'] = 'jeffersoncatalan04@gmail.com'
app.config['EMAIL_PASSWORD'] = 'wjqb lwdp tatv iifx'

@app.route('/', methods=['POST', 'GET'])
def home():

    current_user_id = session.get('user_info', {}).get('user_id')
    
    if not current_user_id:
        return redirect(url_for('login'))

    locker1 = database_locker.find_one({"locker_id": "LCK001"})
    locker2 = database_locker.find_one({"locker_id": "LCK002"})
    locker3 = database_locker.find_one({"locker_id": "LCK003"})

    if locker1 and locker1.get("status") and locker1.get("user_id") == current_user_id:
        return redirect(url_for("locker_one"))
    elif locker2 and locker2.get("status") and locker2.get("user_id") == current_user_id:
        return redirect(url_for("locker_two"))
    elif locker3 and locker3.get("status") and locker3.get("user_id") == current_user_id:
        return redirect(url_for("locker_three"))

    locked1 = locked2 = locked3 = None

    if locker1 and locker1.get("status") and locker1.get("user_id") != current_user_id:
        locked1 = "locked"
    if locker2 and locker2.get("status") and locker2.get("user_id") != current_user_id:
        locked2 = "locked"
    if locker3 and locker3.get("status") and locker3.get("user_id") != current_user_id:
        locked3 = "locked"

    return render_template('index.html', locked1=locked1, locked2=locked2, locked3=locked3)

def update_locker_status(locker_id, status, user_id=None):
    update_data = {"status": status}
    if user_id is not None:
        update_data["user_id"] = user_id
    else:
        update_data["user_id"] = None

    result = database_locker.update_one(
        {"locker_id": locker_id},
        {"$set": update_data}
    )
    if result.matched_count > 0:
        print(f"Locker {locker_id} status updated to {status} with user_id {user_id}")
    else:
        print(f"Locker {locker_id} not found")

@app.route("/locker_one", methods=["POST", "GET"])
def locker_one():
    if 'time_in' not in session:
        now = datetime.now()
        session['time_in'] = now.strftime("%H:%M:%S")
    session["location"] = "AYALA FAIRVIEW TERRACES"
    
    current_user_id = session.get('user_info', {}).get('user_id')
    if not current_user_id:
        return redirect(url_for('login'))

    locker1 = database_locker.find_one({"locker_id": "LCK001"})
    if locker1 and locker1.get("status") and locker1.get("user_id") != current_user_id:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if 'end' in request.form:
            message = "Confirm?"
            return render_template("locker_one.html", message=message)

    if locker1:
        update_locker_status("LCK001", True, current_user_id)
    return render_template("locker_one.html")

@app.route("/locker_two", methods=["POST", "GET"])
def locker_two():
    if 'time_in' not in session:
        now = datetime.now()
        session['time_in'] = now.strftime("%H:%M:%S")
    session["location"] = "SM FAIRVIEW"
    
    current_user_id = session.get('user_info', {}).get('user_id')
    if not current_user_id:
        return redirect(url_for('login'))

    locker2 = database_locker.find_one({"locker_id": "LCK002"})
    if locker2 and locker2.get("status") and locker2.get("user_id") != current_user_id:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if 'end' in request.form:
            message = "Confirm?"
            return render_template("locker_two.html", message=message)
    
    if locker2:
        update_locker_status("LCK002", True, current_user_id)
    return render_template("locker_two.html")

@app.route("/locker_three", methods=["POST", "GET"])
def locker_three():
    if 'time_in' not in session:
        now = datetime.now()
        session['time_in'] = now.strftime("%H:%M:%S")
    session["location"] = "AYALA CLOVER LEAF"

    current_user_id = session.get('user_info', {}).get('user_id')
    if not current_user_id:
        return redirect(url_for('login'))
    
    locker3 = database_locker.find_one({"locker_id": "LCK003"})
    if locker3 and locker3.get("status") and locker3.get("user_id") != current_user_id:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if 'end' in request.form:
             message = "Confirm?"
             return render_template("locker_three.html", message=message)
    
    if locker3:
        update_locker_status("LCK003", True, current_user_id)
    return render_template("locker_three.html")

#bago
@app.route('/end_locker', methods=["POST"])
def end_locker():
    if 'endlocker' in request.form:
        locker_id = request.form['endlocker']
        update_locker_status(locker_id, False)
        session.pop(f'locker_{locker_id[-1]}', None)

        now = datetime.now()
        time_in = session.get('time_in')
        current_date = now.date().isoformat()
        time_out = now.strftime("%H:%M:%S")
        location = session.get("location")
        user_id = session['user_info']['user_id']

        database_history_user.insert_one({
            "user_id": user_id,
            "date": current_date,
            "locker": locker_id,
            "time_in": time_in,
            "time_out": time_out,
            "location": location
        })

        dashboard_report.insert_one({
            "user_id": user_id,
            "locker_id": locker_id,
            "date": current_date,
            "time_in": time_in,
            "time_out": time_out,
            "location": location
        })

    return redirect(url_for('home'))


@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'admin' in session:
        # Fetch all reports from the dashboard_report collection
        all_reports = list(dashboard_report.find().sort([("date", -1), ("time_out", -1)]))
        # Create an empty list to store user reports
        user_reports = []

        # Iterate through each report
        for report in all_reports:
            user_id = report.get('user_id')
            locker_id = report.get('locker_id')

            # Query the database to get user and locker information based on their IDs
            user_info = database_account.find_one({"_id": user_id})
            locker_info = database_locker.find_one({"locker_id": locker_id})

            # If user and locker information is found, add the report details along with user and locker information
            if user_info and locker_info:
                user_report = {
                    "user": user_info.get('_id'),
                    "locker": locker_info.get('locker_id'),
                    "date": report.get('date'),
                    "time_in": report.get('time_in'),
                    "time_out": report.get('time_out'),
                    "location" : report.get('location')
                }
                user_reports.append(user_report)

        # Render the dashboard template with user reports
        return render_template('dashboard.html', user_reports=user_reports)
    else:
        # Redirect to login page if not logged in as admin
        return redirect(url_for('login'))
    
@app.route('/locker_info', methods=['GET', 'POST'])
def locker_info():
    sm_north = sm_fairview = moa = False
    locked1 = locked2 = locked3 = None
    user1 = user2 = user3 = None

    locker1 = database_locker.find_one({"locker_id": "LCK001"})
    locker2 = database_locker.find_one({"locker_id": "LCK002"})
    locker3 = database_locker.find_one({"locker_id": "LCK003"})

    if locker1:
        locked1 = locker1.get("status", False)
        user1 = locker1.get("user_id")
    if locker2:
        locked2 = locker2.get("status", False)
        user2 = locker2.get("user_id")
    if locker3:
        locked3 = locker3.get("status", False)
        user3 = locker3.get("user_id")

    if request.method == 'POST':
        location = request.form['location']
        if location == 'sm_north':
            sm_north = True
        elif location == 'sm_fairview':
            sm_fairview = True
        elif location == 'mall_of_asia':
            moa = True

    return render_template(
        "locker_info.html", 
        sm_north=sm_north, 
        sm_fairview=sm_fairview, 
        moa=moa,
        locked1=locked1,
        locked2=locked2,
        locked3=locked3,
        user1=user1,
        user2=user2,
        user3=user3
    )

@app.route('/sales_info')
def sales_info():
    now = datetime.now()
    current_date = now.date().isoformat() 
    current_time = now.strftime("%H:%M") 

    return render_template('sales_info.html', date= current_date, time=current_time)

@app.route('/account', methods=['GET', 'POST'])
def account():
    
    if request.method == 'POST':
        if 'logoutbtn' in request.form:
            return redirect(url_for('logout'))

        # if 'deleteacc' in request.form:
        #     email = session['user_info']['email']
        #     database_account.delete_one({"email": email})
        #     session.pop('user_info', None)
        #     return redirect(url_for('home'))
        # else:
        #     return redirect(url_for('login'))

    if 'user_info' in session:
        user_info = session['user_info']
        return render_template("account.html", user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        admin_email = database_admin.find_one({"email": email})
        user_document = database_account.find_one({"email": email})

        if admin_email:
            if password == admin_email.get('password'):
                admin_email['_id'] = str(admin_email['_id'])
                session['admin'] = admin_email
                flash('Admin login successful', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Password incorrect', 'error')
        elif user_document:
            if bcrypt.check_password_hash(user_document['password'], password):
                user_data = {
                    "user_id": user_document['_id'],
                    "fullname": user_document['fullname'],
                    "email": user_document['email'],
                    "contactnum": user_document['contactnum'],
                    "address": user_document['address']
                }
                session.permanent = True
                session['user_info'] = user_data
                flash('User login successful', 'success')
                return redirect(url_for('home'))
            else:
                flash('Password incorrect', 'error')
        else:
            flash('Email not found', 'error')
    
    return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    #logout admin or user account
    if 'admin' in session:
        session.pop('admin', None)
    if 'user_info' in session:
        session.pop('user_info', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    #site key ng recaptcha to
    site_key = app.config['RECAPTCHA_PUBLIC_KEY']
    message = None
    
    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        address = request.form['address']
        phonenum = request.form['phonenum']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        recaptcha_response = request.form['g-recaptcha-response']

        # Verify reCAPTCHA token
        recaptcha_response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': app.config['RECAPTCHA_PRIVATE_KEY'],
                'response': recaptcha_response
            }
        )
        result = recaptcha_response.json()

        if not result.get('success'):
            flash("reCAPTCHA validation failed. Please try again.")
            return render_template('signup.html', message=message, site_key=site_key)

        # Check if email already exists
        if database_account.find_one({"email": email}):
           flash("Email already exists")
           return render_template("signup.html", message=message, site_key=site_key)

        # Check if phone number already exists
        if database_account.find_one({"contactnum": phonenum}):
            flash("Phone number already exists")
            return render_template("signup.html", message=message, site_key=site_key)

        # Check if passwords match
        if password != confirmpassword: 
            flash("Passwords do not match")
            return render_template("signup.html", message=message, site_key=site_key)

        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])        
        session['otp'] = otp
        session['user_info'] = {
            "fullname": fullname,
            "email": email,
            "contactnum": phonenum,
            "address": address,
            "password": bcrypt.generate_password_hash(password).decode('utf-8')
        }
        send_otp_email(email, otp)
        return redirect(url_for('OTP'))

        # # Hash the password before storing
        # hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # user_id = generate_unique_id("USR")
        # # Insert new user into the database
        # database_account.insert_one({
        #     "_id": user_id,
        #     "fullname": fullname,
        #     "email": email,
        #     "contactnum": phonenum,
        #     "address": address,
        #     "password": hashed_password
        # })

        # # Log in the user after successful signup
        # user_data = {
        #     "fullname": fullname,
        #      "email": email,
        #      "contactnum": phonenum,
        #      "address": address,
        #     }

        # session['user_info'] = user_data
        # if 'user_info' in session:
        #         print("use in a session")

        # flash('You were successfully registered and logged in')
       
        # return redirect(url_for('home'))

    return render_template('signup.html', message=message, site_key=site_key)
@app.route('/OTP_Verification', methods=['GET', 'POST'])
def OTP():
    if request.method == 'POST':
        input_otp = request.form['otp_verification']

        if input_otp == session.get('otp'):
            user_info = session.pop('user_info', None)
            if user_info:
                user_id = generate_unique_id("USR")
                database_account.insert_one({
                    "_id": user_id,
                    **user_info
                })
                flash('You were successfully registered and logged in')
                return redirect(url_for('home'))
            else:
                flash('Session expired. Please sign up again.')
                return redirect(url_for('signup'))
        else:
            flash('Invalid OTP. Please try again.')
            return render_template('OTP_verification.html')

    return render_template('OTP_verification.html')

def send_otp_email(to_email, otp):
    msg = EmailMessage()
    msg['Subject'] = 'OTP Verification'
    msg['From'] = app.config['EMAIL_USER']
    msg['To'] = to_email
    msg.set_content(f'Good day!'
                      'Thank you for using STI ProWare!'
                    'Warning: Do not give this to anyone. This code can be used to login to your Account. '
                    'Your One-Time Password (OTP) is given below. It is valid for the next  5 minutes. '
                    'One-Time Password(OTP): 000000'
                    'If you did not request this code, please disregard this message Warm regards,'
                    'ProWare')

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(app.config['EMAIL_USER'], app.config['EMAIL_PASSWORD'])
        server.send_message(msg)

def generate_unique_id(prefix):
    # Fetch the current numeric portion from the repository collection
    id_doc = id_repository.find_one_and_update(
        {"_id": prefix},
        {"$inc": {"sequence": 1}},
        upsert=True,
        return_document=True
    )
    return f"{prefix}{id_doc['sequence']:06d}"  # Concatenate prefix with padded numeric portion

if __name__ == "__main__":
    app.run(debug=True) 


#host='0.0.0.0' port='5000'