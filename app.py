import base64
from flask import Flask, url_for, redirect, render_template, session, flash, request
from db_proware import *
from routes.cart import cartbp
from routes.queue import queuebp
from routes.login import loginbp
from routes.item_details import itemdt_bp
from routes.check_out import check_outbp
from routes.notif import notifbp
from routes.purchase import purchasebp

from routes.admin.items import itembp
from routes.admin.orders import orderbp
from routes.admin.report import reportbp
from routes.admin.queue import queueadminbp

from routes.system_admin import system_adminbp

from routes.admin.id_generate import *
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm


app = Flask(__name__)
app.secret_key = 'LGHHGtUqp'
app.config['EMAIL_USER'] = 'stinovalichesproware@gmail.com'
app.config['EMAIL_PASSWORD'] = 'iocv jahk rprh hijv'
bcrypt = Bcrypt(app) 
#csrf = CSRFProtect(app)
#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
# db.createUser({ user: "Proware", pwd: "Stinovalichesproware-15", roles: [ { role: "root", db: "admin" } ] })
#admin blueprint
app.register_blueprint(itembp)
app.register_blueprint(orderbp)
app.register_blueprint(reportbp)
app.register_blueprint(queueadminbp)

#system_admin blueprint
app.register_blueprint(system_adminbp)

#user blueprint
app.register_blueprint(cartbp)
app.register_blueprint(loginbp)
app.register_blueprint(itemdt_bp)
app.register_blueprint(check_outbp)
app.register_blueprint(notifbp)
app.register_blueprint(purchasebp)
app.register_blueprint(queuebp)


def check_role(required_role):
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    if session['user']['roles'] == required_role:
        return True 
    return False

@app.route('/', methods=['GET','POST'])
def dashboard():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

@app.route("/home", methods=['GET','POST'])
def home():
    #get ung data from form html
    category = request.args.get('category', '').strip()
    search_query = request.form.get('search_item', '').strip()

    #query para sa items    
    if search_query:
            items = db_items.find({'item_name': {'$regex': search_query, '$options': 'i'}})
    else:
            items = db_items.find()
    #query para sa category
    if category:
        items = db_items.find({'item_category': {'$regex': category, '$options': 'i'}})

    #check roles dito   
    check_roles = check_role("Student")
    if not check_roles:
        return redirect(url_for('dashboard'))
    
    return render_template('index.html', items=items)

@app.route("/admin", methods=["POST","GET"])
def admin():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    check_roles = check_role("admin")
    if not check_roles:
        return redirect(url_for('dashboard'))
    
    return render_template('admin.html')
    
@app.route("/system_admin", methods=["POST","GET"])
def system_admin():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    check_roles = check_role("system_admin")
    if not check_roles:
        return redirect(url_for('dashboard'))
    
    return render_template('system_admin.html')

@app.route("/account", methods=['POST', 'GET'])
def account():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    user_data = session.get('user')
    email = user_data.get('email')
     
    
    if request.method == 'POST':
      profile = request.files.get("profile")
      print('succes profile')
      image_data = profile.read()
      image_base64 = base64.b64encode(image_data).decode('utf-8')
      db_account.update_one({'email': email}, {'$set': {'profile': image_base64}})        

    acc = db_account.find_one({"email": email})   
    return render_template('profile.html', account=acc)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port="5000",debug=True)



