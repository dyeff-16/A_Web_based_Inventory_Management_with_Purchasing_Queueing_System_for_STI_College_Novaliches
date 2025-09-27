from datetime import datetime
from email.message import EmailMessage
import smtplib
from flask import Flask, current_app, url_for, redirect, render_template, session, request, Blueprint
import pytz
from db_proware import *

orderbp = Blueprint('orders', __name__, url_prefix='/order')


@orderbp.route('/order_history', methods=['POST','GET'])
def order_history():
    search_query = request.form.get('search_query')
    filter_category = request.form.get('filter_category')

    if search_query and filter_category:
        if filter_category == 'email':
            history = db_orders_history.find({"user_email": {"$regex": f"^{search_query}", "$options": "i"}})
        elif filter_category == 'reference_number':
            history = db_orders_history.find({"reference_number": {"$regex": f"^{search_query}", "$options": "i"}})
        elif filter_category == 'name':
            history = db_orders_history.find({"name": {"$regex": f"^{search_query}", "$options": "i"}})
        elif filter_category == 'date':
            history = db_orders_history.find({"order_date": {"$regex": f"^{search_query}", "$options": "i"}})
        elif filter_category == 'std_id':
            history = db_orders_history.find({"student_id": {"$regex": f"^{search_query}", "$options": "i"}})
        else:
            history = db_orders_history.find().sort([("order_date", -1), ("order_time", -1)])
    else:   
        history = db_orders_history.find().sort([("order_date", -1), ("order_time", -1)])
    return render_template('admin/order_history.html', history=list(history))

@orderbp.route('/orders', methods=['POST', 'GET'])
def orders_list():
    
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    search_query = request.form.get('search_query')
    filter_category = request.form.get('filter_category')

    if search_query and filter_category:
        if filter_category == 'email':
            orders = db_orders.find({"user_email": {"$regex": f"^{search_query}", "$options": "i"}})
        elif filter_category == 'reference_number':
            orders = db_orders.find({"reference_number": {"$regex": f"^{search_query}", "$options": "i"}})
        elif filter_category == 'name':
            orders = db_orders.find({"name": {"$regex": f"^{search_query}", "$options": "i"}})
        else:
            orders = db_orders.find().sort([("order_date", -1), ("order_time", -1)])
    else:   
        orders = db_orders.find().sort([("order_date", -1), ("order_time", -1)])

    return render_template('admin/orders.html', orders=list(orders))
    
@orderbp.route('/update_order_status', methods=['POST'])
def update_order_status():
   
    if 'user' not in session:
      return redirect(url_for('login.login_'))
     
    rfr_num = request.form.get('rfr_num')
    new_status = request.form.get('status')
    ref_receipt = request.form.get('ref_receipt')
    decline = request.form.get('decline')
    
    if decline:
        db_orders.update_one(
            {"reference_number": rfr_num},
            {"$unset": {"receipt": ""}}
        )
        print(decline)
    if rfr_num and new_status and ref_receipt:
        db_orders.update_one(
            {"reference_number": rfr_num},
            {"$set": {"status": new_status, "ref_receipt": ref_receipt}}
        )
        print(new_status)

    if rfr_num and new_status:
        db_orders.update_one(
            {"reference_number": rfr_num},
            {"$set": {"status": new_status}}
        )
        print(new_status)
    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    date_str = ph_time.strftime('%Y-%m-%d')
    time_str = ph_time.strftime('%H:%M:%S')  # military time
    

    
    order = db_orders.find_one({'reference_number': rfr_num})
    if order['status'] == "Paid":
        for item in order.get('items', []):
                item_code = item['itemCode']
                quantity = int(item['quantity'])

                # First try to deduct from a sized item
                result = db_items.update_one(
                    {"sizes.itemCode": item_code},
                    {"$inc": {"sizes.$.quantity": -quantity}}
                )

                # If not found in sizes, deduct from non-sized item
                if result.modified_count == 0:
                    db_items.update_one(
                        {"itemCode": item_code},
                        {"$inc": {"item_quantity": -quantity}}
                    )

        db_notification.update_one(
                {"reference_number": rfr_num, "email": order['email']},
                {
                    "$push": {
                        "thread": {
                            "status": "Paid",
                            "order_date": date_str,
                            "order_time": time_str,
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                },
                upsert=True
            )


        send_order_paid_notification(
            to_email=order['email'],
            fullname=order['name'],
            student_id=order['student_id'],
            ref_number=order['reference_number'],
            date_str=date_str,
            time_str=time_str,
            total_amount=order['total_amount']
        )

    if order['status'] == "Claimed":
        #insert sa history ung order 
        order['date'] = date_str
        order['time'] = time_str
        db_orders_history.insert_one(order)
        db_history.insert_one(order)
        #delete ung order kase tapos na hehehe
        db_orders.delete_one({'_id': order['_id']})

        db_notification.update_one(
                {"reference_number": rfr_num, "email": order['email']},
                {
                    "$push": {
                        "thread": {
                            "status": "Claimed",
                            "order_date": date_str,
                            "order_time": time_str,
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                },
                upsert=True
            )

        send_order_claimed_notification(
            to_email=order['email'],
            fullname=order['name'],
            student_id=order['student_id'],
            ref_number=order['reference_number'],
            date_str=date_str,
            time_str=time_str
        )
        
    return redirect(url_for('orders.orders_list'))

@orderbp.route('/pre-order', methods=['POST','GET'])
def pre_order():
    return render_template('admin/pre_order.html')

def send_order_paid_notification(to_email, fullname, student_id, ref_number, date_str, time_str, total_amount):
    msg = EmailMessage()
    msg['Subject'] = 'STI ProWare – Payment Confirmation'
    msg['From'] = current_app.config['EMAIL_USER']
    msg['To'] = to_email
    msg.set_content(f"""Good day {fullname},

Your payment for the order with STI ProWare has been confirmed!

Here are the details of your order:

Reference Number: {ref_number}
Student ID: {student_id}
Payment Date: {date_str}
Payment Time: {time_str}
Total Amount Paid: {total_amount}
Order Status: Paid

Thank you for your payment! Your order will now be prepared for claiming.

Warm regards,
ProWare Team
""")
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(current_app.config['EMAIL_USER'], current_app.config['EMAIL_PASSWORD'])
        server.send_message(msg)


def send_order_claimed_notification(to_email, fullname, student_id, ref_number, date_str, time_str):
    msg = EmailMessage()
    msg['Subject'] = 'STI ProWare – Order Claimed'
    msg['From'] = current_app.config['EMAIL_USER']
    msg['To'] = to_email
    msg.set_content(f"""Good day {fullname},

We are happy to inform you that your order has been successfully claimed!

Here are your order details:

Reference Number: {ref_number}
Student ID: {student_id}
Claim Date: {date_str}
Claim Time: {time_str}
Order Status: Claimed

Thank you for using STI ProWare! We hope to serve you again soon.

Warm regards,
ProWare Team
""")
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(current_app.config['EMAIL_USER'], current_app.config['EMAIL_PASSWORD'])
        server.send_message(msg)
