import base64
from datetime import datetime
from flask import Blueprint, jsonify, url_for, redirect, render_template, session, flash, request
import pytz
from db_proware import *


notifbp= Blueprint('notif', __name__, url_prefix='/notification')

@notifbp.route('/notificaiton', methods=['POST'])
def notification():
  if 'user' not in session:
        return redirect(url_for('login.login_'))
  
  user = session['user']['email']
  print(user)
  notif = list(db_notification.find({'email': user}).sort([("order_date", -1), ("order_time", -1)])) 
  return render_template('notification.html', notification=notif)

@notifbp.route('/purchase')
def purchase():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    #i2 ay upload sa resibo
    if request.method == "POST":
        # Handle receipt upload only if file is provided
        if 'img_reciept' in request.files and request.files['img_reciept'].filename != '':
            image_reciept = request.files['img_reciept']
            ref_num = request.form.get('ref_number')

            image_data = image_reciept.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            db_orders.update_one(
                {"reference_number": ref_num},
                {"$set": {'receipt': image_base64}}
            )

        # Handle status update
        rfr_num = request.form.get('rfr_num')
        new_status = request.form.get('status')
        if rfr_num and new_status:
            db_orders.update_one(
                {"reference_number": rfr_num},
                {"$set": {"status": new_status}}
            )

    user_data = session.get('user')
    if user_data:
        name = user_data.get('fullname')
        email = user_data.get('email')
        std_id = user_data.get('student_id')

    user_orders = db_orders.find({"email": email})
    

    return render_template('purchase.html', orders=user_orders, std_id=std_id, name=name, email=email)

@notifbp.route('/getImageItem', methods=['GET','POST'])
def getItemImage():
    data = request.get_json()
    _id = data.get('item_id')

    item = db_items.find_one({'_id': _id})
    if item and 'image' in item:
        image = item['image']
        return jsonify({'imageBase64': image}), 200
    else:
        return jsonify({"NO IMAGE FOUND"}), 400
    
@notifbp.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    if 'img_reciept' in request.files and request.files['img_reciept'].filename != '':
        image_reciept = request.files['img_reciept']
        ref_num = request.form.get('ref_number')

        image_data = image_reciept.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        db_orders.update_one(
            {"reference_number": ref_num},
            {"$set": {'receipt': image_base64}}
        )

    # Handle status update
    rfr_num = request.form.get('rfr_num')
    new_status = request.form.get('status')
    if rfr_num and new_status:
        db_orders.update_one(
            {"reference_number": rfr_num},
            {"$set": {"status": new_status}}
        )

    return redirect(url_for('notif.purchase'))

@notifbp.route('/Paid', methods=['GET','POST'])
def paid():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    user_data = session.get('user')
    if user_data:
        name = user_data.get('fullname')
        email = user_data.get('email')
        std_id = user_data.get('student_id')
    user_orders = list(db_orders.find({"email": email})) 
    return render_template('paid.html', orders=user_orders, std_id=std_id, name=name, email=email)

@notifbp.route('/Claim',methods=['GET','POST'])
def claim():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    btn_claim_ref = request.form.get('btn_claim')
    email = request.form.get('email')
    db_orders.update_one(
            {"reference_number": btn_claim_ref},
            {"$set": {'status': 'Claim'}}
        )
    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    date_str = ph_time.strftime('%Y-%m-%d')
    time_str = ph_time.strftime('%H:%M:%S')  # military time
    print(email)
    db_notification.update_one(
                {"reference_number": btn_claim_ref, "email": email},
                {
                    "$push": {
                        "thread": {
                            "status": "Claim",
                            "order_date": date_str,
                            "order_time": time_str,
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                },
                upsert=True
            )
    user_data = session.get('user')
    if user_data:
        name = user_data.get('fullname')
        email = user_data.get('email')
        std_id = user_data.get('student_id')
    user_orders = list(db_orders.find({"email": email})) 
    return render_template('claim.html', orders=user_orders, std_id=std_id, name=name, email=email)

@notifbp.route('/Order_History', methods=['GET','POST'])
def order_history():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    user_data = session.get('user')
    
    if user_data:
        email = user_data.get('email')
 
    history = db_orders_history.find({'email': email}).sort([("order_date", -1), ("order_time", -1)])
    return render_template('order_history.html', history=list(history))
  
