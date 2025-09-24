import base64
from datetime import datetime
from email.message import EmailMessage
import smtplib
import pytz
from flask import Flask, current_app, url_for, redirect, render_template, session, request, Blueprint
from routes.id_generate import generate_item_id, safe_int
from db_proware import *

itembp = Blueprint('item', __name__, url_prefix='/item')

@itembp.route('/products', methods=['GET','POST'])   
def products(): 

    item_uniform = list(db_items.find({"item_category": "Uniform"}))
    item_proware = db_items.find({"item_category" : "Proware"})
    item_textbook = db_items.find({"item_category" : "Textbook"})

    if 'user' in session:
        return render_template('admin/products.html',
            uniforms=item_uniform,
            prowares=item_proware,
            textbooks=item_textbook)
    else:
     return redirect(url_for('login.login_'))

@itembp.route('/add_uniform', methods=['POST', 'GET']) 
def add_uniform():
    if request.method == 'POST':
        item_category = "Uniform"
        item_img = request.files['item_img']
        item_name = request.form['item_name']
        item_selection = request.form.get('item_selection')
        item_program = request.form.get('program_selection')
        item_description = request.form.get("description", "").strip()        

        image_data = item_img.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        item_data = {
            "image": image_base64,
            "item_name": item_name,
            "item_category": item_category,
            "item_program": item_program,
            "item_description": item_description,
        }
        sizes = []
        size_map = {
            "Extra Small": ("ItemCode_XS", "quantity_XS", "price_XS"),
            "Small": ("ItemCode_S", "quantity_small", "price_small"),
            "Medium": ("ItemCode_M", "quantity_medium", "price_medium"),
            "Large": ("ItemCode_L", "quantity_large", "price_large"),
            "Extra Large": ("ItemCode_XL", "quantity_XL", "price_XL"),
            "2XL": ("ItemCode_2XL", "quantity_2XL", "price_2XL"),
            "3XL": ("ItemCode_3XL", "quantity_3XL", "price_3XL"),
            "4XL": ("ItemCode_4XL", "quantity_4XL", "price_4XL"),
            "5XL": ("ItemCode_5XL", "quantity_5XL", "price_5XL")
        }

        def safe_int(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0

        for size_label, (code_field, qty_field, price_field) in size_map.items():
            item_code = request.form.get(code_field, "")
            quantity = request.form.get(qty_field)
            price = request.form.get(price_field)

            # Skip if all fields are empty or zero
            if not item_code and not quantity and not price:
                continue

            sizes.append({
                "size": size_label,
                "itemCode": item_code,
                "quantity": safe_int(quantity),
                "price": safe_int(price)
        })

        item_data["_id"] = generate_item_id("UNIF")
        item_data['sizes'] = sizes


        if item_selection == 'quantity':
            item_data['itemCode'] = request.form.get('quantity_itemcode')
            item_data['item_quantity'] = request.form.get('quantity_stock')
            item_data['item_price'] = request.form.get('quantity_price')

        db_items.insert_one(item_data)
        return redirect(url_for('item.products'))

    # Handle GET request inside the function
    if 'user' in session:
        return render_template('admin/add_uniform.html')
    else:
        return redirect(url_for('login.login_'))

@itembp.route('/add_proware', methods=['POST', 'GET']) 
def add_proware():
    if request.method == 'POST':
        item_category = "Proware"
        item_img = request.files['item_img']
        item_name = request.form['item_name']
        item_selection = request.form.get('item_selection')
        item_description = request.form.get("description", "").strip()

        image_data = item_img.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        item_data = {
            "image": image_base64,
            "item_name": item_name,
            "item_category": item_category,
            "item_description": item_description,
        }

        sizes = []
        size_map = {
            "Extra Small": ("ItemCode_XS", "quantity_XS", "price_XS"),
            "Small": ("ItemCode_S", "quantity_small", "price_small"),
            "Medium": ("ItemCode_M", "quantity_medium", "price_medium"),
            "Large": ("ItemCode_L", "quantity_large", "price_large"),
            "Extra Large": ("ItemCode_XL", "quantity_XL", "price_XL"),
            "2XL": ("ItemCode_2XL", "quantity_2XL", "price_2XL"),
            "3XL": ("ItemCode_3XL", "quantity_3XL", "price_3XL"),
            "4XL": ("ItemCode_4XL", "quantity_4XL", "price_4XL"),
        }

        for size_label, (code_field, qty_field, price_field) in size_map.items():
            item_code = request.form.get(code_field, "")
            quantity = request.form.get(qty_field)
            price = request.form.get(price_field)

            # Skip if all fields are empty or zero
            if not item_code and not quantity and not price:
                continue

            sizes.append({
                "size": size_label,
                "itemCode": item_code,
                "quantity": safe_int(quantity),
                "price": safe_int(price)
        })

        item_data["_id"] = generate_item_id("PRW")
        item_data['sizes'] = sizes

        if item_selection == 'quantity':
            item_data['itemCode'] = request.form.get('quantity_itemcode', "")
            item_data['item_quantity'] = safe_int(request.form.get('quantity_stock'))
            item_data['item_price'] = safe_int(request.form.get('quantity_price'))

        db_items.insert_one(item_data)
        return redirect(url_for('item.products'))

    # Handle GET request
    if 'user' in session:
        return render_template('admin/add_proware.html')
    else:
        return redirect(url_for('login.login_'))

@itembp.route('/add_textbook', methods=['POST', 'GET']) 
def add_textbook():
    if request.method == 'POST':
        item_category = "Textbook"
        item_img = request.files['item_img']
        item_name = request.form['item_name']
        item_description = request.form['description']      

        image_data = item_img.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        item_data = {
            "image": image_base64,
            "item_name": item_name,
            "item_category": item_category,
            'itemCode': request.form.get('quantity_itemcode'),
            'item_quantity': request.form.get('quantity_stock'),
            'item_price': request.form.get('quantity_price'),
            "item_description": item_description,
         }
        item_data["_id"] = generate_item_id("TXTB")
        db_items.insert_one(item_data)
        return redirect(url_for('item.products'))

    # Handle GET request inside the function
    if 'user' in session:
        return render_template('admin/add_textbook.html')
    else:
        return redirect(url_for('login.login_'))

@itembp.route('/add_erm', methods=['POST', 'GET'])
def add_erm():
    return render_template('admin/add_erm.html')

@itembp.route('/add_mkt', methods=['POST', 'GET'])
def add_mkt():
    return render_template('admin/add_mkt.html')

@itembp.route('/add_rtw', methods=['POST', 'GET'])
def add_rtw():
    return render_template('admin/add_rtw.html')

@itembp.route('/add_sms', methods=['POST', 'GET'])
def add_sms():
    return render_template('admin/add_sms.html')

@itembp.route('/add_wnu', methods=['POST', 'GET'])
def add_wnu():
    return render_template('admin/add_wnu.html')

@itembp.route('/update_items', methods=['GET', 'POST'])
def update_items():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        filter_category = request.form.get('filter_category')
        
        # Build search query based on selected filter
        query = {}
        if filter_category == 'item_name':
            query["item_name"] = {"$regex": search_query, "$options": "i"}
        elif filter_category == 'itemCode':
            query["$or"] = [
                {"itemCode": {"$regex": search_query, "$options": "i"}},
                {"sizes.itemCode": {"$regex": search_query, "$options": "i"}}
            ]
        elif filter_category == 'item_category':
            query["item_category"] = {"$regex": search_query, "$options": "i"}
        
        # Search for items that match the query
        items = db_items.find(query)
        return render_template('admin/update_item.html', items=items)
    
    return render_template('admin/update_item.html', items=None)

@itembp.route('/edit/<item_code>', methods=['GET', 'POST'])
def edit_item(item_code):
    # Try to find by top-level itemCode
    item = db_items.find_one({"itemCode": item_code})
    if item:
        print('Found top-level item')
        return render_template('admin/edit_item.html', item=item, item_code=item_code, size_data=None)

    # Not found top-level, try finding it inside sizes.itemCode
    item_size = db_items.find_one({"sizes.itemCode": item_code})
    if item_size:
        print(item_size['item_name'])
        print('Found inside sizes')
        # Grab the specific size object
        matched_size = next((s for s in item_size.get('sizes', []) if s.get('itemCode') == item_code), None)
        if matched_size:
            return render_template('admin/edit_item.html', item=item_size, item_code=item_code, size_data=matched_size)

    # Still not found
    return "Item not found", 404

@itembp.route('/confirm_update/<itemCode>', methods=['POST', 'GET'])
def confirm_update(itemCode):
    
    action_type = request.form['action']
    price = request.form['price']
    reason = request.form['reason']

    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    date_str = ph_time.strftime('%Y-%m-%d')
    time_str = ph_time.strftime('%H:%M:%S')  # military time
    item = db_items.find_one({'itemCode': itemCode})

    if item:
        item['item_quantity'] = int(item['item_quantity'])  
        if action_type == 'restock':
            new_quantity_str = request.form.get('new_quantity', '').strip()
            new_quantity = int(new_quantity_str)
            item['item_quantity'] += new_quantity
            item['action'] = action_type
            item['date_modified'] =  date_str
            item['time_modified'] = time_str
            db_items.replace_one({'_id': item['_id']}, item)
            notify_preorders(itemCode)
        elif action_type == 'deduct':
            new_quantity_str = request.form.get('new_quantity', '').strip()
            new_quantity = int(new_quantity_str)

            if not new_quantity_str.isdigit():
                print('Please enter a valid quantity.', 'error')
                return redirect(url_for('item.update_items'))  # Stop further execution if invalid

            new_quantity = int(new_quantity_str)
            item['item_quantity'] -= new_quantity 
            item['action'] = action_type
            item['date_modified'] = date_str
            item['time_modified'] = time_str
            item['reason'] = reason

            db_items.replace_one({'_id': item['_id']}, item)

        elif action_type == 'price':
            item['item_price'] = price
            item['action'] = action_type
            item['date_modified'] =  date_str
            item['time_modified'] = time_str
            db_items.replace_one({'_id': item['_id']}, item)

    print('Updated top-level item_quantity')
    item_size = db_items.find_one({'sizes.itemCode': itemCode})

    if item_size and 'sizes' in item_size and item_size['sizes']:
        print("Sizes found:", item_size['sizes'])
        for s in item_size['sizes']:
            print('Checking size:', s['itemCode'])
            if s['itemCode'] == itemCode:
                
                if action_type == 'restock':
                        new_quantity_str = request.form.get('new_quantity', '').strip()
                        new_quantity = int(new_quantity_str)
                        s['quantity'] += new_quantity
                        s['action'] = action_type
                        s['date_modified'] = date_str
                        s['time_modified'] = time_str


                        print('Updated quantity, action, and date_modified in sizes array')

                        db_items.update_one(
                            {'sizes.itemCode': itemCode},
                            {'$set': {
                                'sizes.$.quantity': s['quantity'],
                                'sizes.$.action': s['action'],
                                'sizes.$.date_modified': s['date_modified'],
                                'sizes.$.time_modified': s['time_modified']
                            }})
                                
                        notify_preorders(itemCode)
                elif action_type == 'deduct':
                    new_quantity_str = request.form.get('new_quantity', '').strip()
                    new_quantity = int(new_quantity_str)

                    if not new_quantity_str.isdigit():
                        print('Please enter a valid quantity.', 'error')
                        return redirect(url_for('item.update_items')) 
                    s['quantity'] -= new_quantity
                    s['reason'] = reason
                    s['action'] = action_type
                    s['date_modified'] = date_str
                    s['time_modified'] = time_str

                    print('Updated quantity, action, and date_modified in sizes array')

                    db_items.update_one(
                        {'sizes.itemCode': itemCode},
                        {'$set': {
                            'sizes.$.quantity': s['quantity'],
                            'sizes.$.action': s['action'],
                            'sizes.$.reason': s['reason'], 
                            'sizes.$.date_modified': s['date_modified'],
                            'sizes.$.time_modified': s['time_modified']
                        }}
                    )

                elif action_type == 'price':
                    s['price'] = price                
                    s['action'] = action_type
                    s['date_modified'] = date_str
                    s['time_modified'] = time_str


                    print('Updated price, action, and date_modified in sizes array')

                    db_items.update_one(
                        {'sizes.itemCode': itemCode},
                        {'$set': {
                            'sizes.$.price': s['price'],
                            'sizes.$.action': s['action'],
                            'sizes.$.date_modified': s['date_modified'],
                            'sizes.$.time_modified': s['time_modified']
                        }}
                    )
                break
        else:
            print("No sizes found or item_size is None")
        
    return redirect(url_for('item.update_items'))

def notify_preorders(item_code):
    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    date_str = ph_time.strftime('%Y-%m-%d')
    time_str = ph_time.strftime('%H:%M:%S')

    preorders = list(db_preorder.find({
        "itemCode": item_code,
        "status": "pending"
    }))

    for preorder in preorders:
        user_email = preorder["email"]
        user_name = preorder.get("name", "Customer")

        db_notification.insert_one({
            "reference_number": f"PRE-{item_code}-{date_str}{time_str}",
            "email": user_email,
            "name": user_name,
            "status": "Restocked",
            "message": f"Good news {user_name}! The item {item_code} you preordered is now back in stock.",
            "date": date_str,
            "time": time_str
        })
        send_preorder_restock_notification(
            to_email=user_email,
            fullname=user_name,
    
            item_code=item_code,
            date_str=date_str,
            time_str=time_str
        )


        print(f" Notified {user_email}: Item {item_code} is now restocked!")

    db_preorder.update_many(
        {"itemCode": item_code, "status": "pending"},
        {"$set": {"status": "notified"}}
    )

def send_preorder_restock_notification(to_email, fullname, item_code, date_str, time_str):
    msg = EmailMessage()
    msg['Subject'] = 'STI ProWare – Preorder Restock Notification'
    msg['From'] = current_app.config['EMAIL_USER']
    msg['To'] = to_email
    msg.set_content(f"""Good day {fullname},

Great news! 🎉 The item you preordered is now back in stock.

Here are the details:

Item Code: {item_code}

Restock Date: {date_str}
Restock Time: {time_str}
Status: Available for purchase

Please visit STI ProWare to complete your purchase before stocks run out again!

Warm regards,  
ProWare Team
""")
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(current_app.config['EMAIL_USER'], current_app.config['EMAIL_PASSWORD'])
        server.send_message(msg)

