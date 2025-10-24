from email.message import EmailMessage
import random
import smtplib
import string
from flask import Flask, current_app, url_for, redirect, render_template, session, flash, request, Blueprint
from db_proware import *


check_outbp = Blueprint('checkout', __name__, url_prefix='/check_out')

def get_email():
    user_email = session['user']['email']
    return user_email

@check_outbp.route('/check_out', methods=['GET', 'POST'])
def check_out():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    if request.method == 'POST':
        selected_ids = request.form.getlist('selected_items')

        print("Items by user only:", list(db_cart.find({'user': get_email()})))
        print(f"Selected IDs: {selected_ids}")  

        if not selected_ids:
            flash('No items selected for checkout.', 'warning')
            return redirect(url_for('cart.cart')) 

        cart_items = list(db_cart.find({
            'itemCode': {'$in': selected_ids},
            'email': get_email() 
        }))

        total_amount = sum(float(item.get('total_amount', 0)) for item in cart_items)

        return render_template('checkout.html', user=get_email(), items=cart_items, total=total_amount)

    return render_template('checkout.html')

def generate_reference_number(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

@check_outbp.route('/place_order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    selected_ids = request.form.getlist('selected_items')
    if not selected_ids:
        flash('No items selected for checkout.', 'warning')
        return redirect(url_for('cart.cart'))

    user_email = session['user']

    # Get selected cart items for this user
    cart_items = list(db_cart.find({
        'itemCode': {'$in': selected_ids},
        'email': get_email()
    }))

    if not cart_items:
        flash('No matching items found in your cart.', 'warning')
        return redirect(url_for('cart.cart'))

    total_amount = sum(int(item.get('total_amount', 0)) for item in cart_items)
    ref_number = generate_reference_number()

    # Format items with only essential fields
    ordered_items = [{
        'item_id': item['item_id'],
        'item_name': item['item_name'],
        'itemCode': item['itemCode'],
        'quantity': item['item_quantity'],
        'price': item['item_price'],
        'size': item.get('size', 'N/A'),
        'subtotal': item['total_amount']
    } for item in cart_items]

    # Create a single order document
    from datetime import datetime
    import pytz

    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    date_str = ph_time.strftime('%Y-%m-%d')
    time_str = ph_time.strftime('%H:%M:%S')

    order_doc = {
        'reference_number': ref_number,
        'email': user_email['email'],
        'name': user_email['fullname'],
        'student_id': user_email['student_id'],
        'items': ordered_items,
        'total_amount': total_amount,
        'order_date': date_str,
        'order_time': time_str,
        'status': 'Placed_Order'
    }
    order_notif = {
        'reference_number': ref_number,
        'email': user_email['email'],
        'name': user_email['fullname'],
        'items': ordered_items,
        'total_amount': total_amount,
        'unread': True,
        'thread':[
            {"status": "Placed Order",
             'order_date': date_str,
             'order_time': time_str,
             "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }]
    }
    


    db_orders.insert_one(order_doc)
    db_notification.insert_one(order_notif)
    send_order_confirmation(
    to_email=user_email['email'],
    fullname=user_email['fullname'],
    student_id=user_email['student_id'],
    ref_number=ref_number,
    date_str=date_str,
    time_str=time_str,
    total_amount=total_amount,
    ordered_items=ordered_items
    )
    # Remove items from the cart
    for item in selected_ids:
        db_cart.delete_one({'email': get_email(), 'itemCode': item})

    return redirect(url_for('purchase.purchase'))


def send_order_confirmation(to_email, fullname, student_id, ref_number, date_str, time_str, total_amount, ordered_items):


    # Format items as a readable list
    items_list = "\n".join(
        [f"- {item['item_name']} (x{item['quantity']}) - {item['subtotal']}" for item in ordered_items]
    )

    msg = EmailMessage()
    msg['Subject'] = 'STI ProWare – Order Confirmation'
    msg['From'] = current_app.config['EMAIL_USER']
    msg['To'] = to_email
    msg.set_content(f"""Good day {fullname},

Thank you for placing your order with STI ProWare!

Your order has been successfully placed and is now being processed. Below are your order details:

Reference Number: {ref_number}
Student ID: {student_id}
Order Date: {date_str}
Order Time: {time_str}
Total Amount: {total_amount}
Order Status: Placed Order

Items Ordered:
{items_list}

Please keep this reference number for future inquiries regarding your order.

Warm regards,
ProWare Team
""")
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(current_app.config['EMAIL_USER'], current_app.config['EMAIL_PASSWORD'])
        server.send_message(msg)
