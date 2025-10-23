from datetime import datetime
from flask import Flask, url_for, redirect, render_template, session, flash, request, Blueprint
import pytz
from db_proware import *
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm

itemdt_bp = Blueprint('item_details', __name__, url_prefix='/item_info')

@itemdt_bp.route("/item/<item_id>")
def item_detail(item_id):
    item = db_items.find_one({"_id": item_id})

    if item and "sizes" in item and item["sizes"]:
        print("sizes item details")
    else:
        print("quantity item details")

    return render_template("item_detail.html", item=item)


# @itemdt_bp.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     if 'user' not in session:
#         return redirect(url_for('login.login_'))

#     item_id = request.form.get('item_id')
#     item_quantity = int(request.form.get("quantity", 1))
#     item_category = request.form['item_category']
#     user_email = session["user"]['email']
#     item = db_items.find_one({"_id": item_id})
#     if not item:
#         return "Item not found", 404

#     if item.get('sizes'): 
#         size_selection = request.form.get('size_selection')
#         print(f"Size selection value: {size_selection}")  
        
#         split_values = size_selection.split('|')
#         if len(split_values) != 4:
#             return "Error: Invalid format for size selection", 400

#         item_code, item_size, item_price, item_quantities = split_values
#         item_price = float(item_price)

#         cart_entry = {
#             "image": item['image'],
#             "email": session["user"]['email'],
#             "item_id": item["_id"],
#             "itemCode": item_code,
#             "item_name": item["item_name"],
#             "item_category": item_category,
#             "item_quantity": item_quantity,
#             "size": item_size,
#             "item_price": item_price,
#             "total_amount": round(item_price * item_quantity, 2)
#         }

#         query = {'email': user_email, 'itemCode': item_code}
#         existing_entry = db_cart.find_one(query)

#         if existing_entry:
#             updated_quantity = existing_entry.get("item_quantity", 0) + item_quantity
#             updated_total_amount = updated_quantity * item_price
#             db_cart.update_one(
#                 {'itemCode': existing_entry['itemCode']},
#                 {'$set': {"item_quantity": updated_quantity, "total_amount": round(updated_total_amount, 2)}}
#             )
#         else:
#             db_cart.insert_one(cart_entry)

#         return redirect(url_for('cart.cart'))

#     else:  
#         item_price = float(item["item_price"]) 
#         total_amount = item_price * item_quantity

#         cart_entry = { 
#             "image": item['image'],
#             "email": session["user"]['email'],
#             "item_id": item["_id"],
#             "itemCode": item['itemCode'],
#             "item_name": item["item_name"],
#             "item_category": item_category,
#             "item_quantity": item_quantity,
#             "item_price": item_price,
#             "total_amount": round(total_amount, 2)
#         }

#         query = {'email': user_email, 'itemCode': item["itemCode"]}
#         existing_entry = db_cart.find_one(query)

#         if existing_entry:
           
#             updated_quantity = existing_entry.get("item_quantity", 0) + item_quantity
#             updated_total_amount = updated_quantity * item_price
#             db_cart.update_one(
#                 {'itemCode': existing_entry['itemCode']},
#                 {'$set': {"item_quantity": updated_quantity, "total_amount": round(updated_total_amount, 2)}}
#             )
#         else:
#             # Insert a new cart entry if it doesn't exist
#             db_cart.insert_one(cart_entry)

#         return redirect(url_for('cart.cart'))


@itemdt_bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    item_id = request.form.get('item_id')
    item_quantity = int(request.form.get("quantity", 1))
    item_category = request.form['item_category']
    user_email = session["user"]['email']
    item = db_items.find_one({"_id": item_id})
    if not item:
        return "Item not found", 404

    if item.get('sizes'):
        size_selection = request.form.get('size_selection')
        split_values = size_selection.split('|')
        if len(split_values) != 4:
            return "Error: Invalid format for size selection", 400

        item_code, item_size, item_price, item_quantities = split_values
        item_price = float(item_price)
        item_stock = int(item_quantities)  # stock available for this size

        query = {'email': user_email, 'itemCode': item_code}
        existing_entry = db_cart.find_one(query)

        # Calculate new quantity
        current_qty = existing_entry.get("item_quantity", 0) if existing_entry else 0
        updated_quantity = current_qty + item_quantity

        if updated_quantity > item_stock:
            updated_quantity = item_stock
            flash(f"⚠️ Only {item_stock} stock(s) available for this item.", "warning")
            return redirect(url_for('item_details.item_detail',item_id=item_id))


        if updated_quantity > 10:
            updated_quantity = 10
            flash("⚠️ You can only add up to 10 per item in the cart.", "warning")
            return redirect(url_for('item_details.item_detail',item_id=item_id))

        updated_total_amount = round(updated_quantity * item_price, 2)

        if existing_entry:
            db_cart.update_one(
                {'_id': existing_entry['_id']},
                {'$set': {"item_quantity": updated_quantity, "total_amount": updated_total_amount}}
            )
        else:
            cart_entry = {
                "image": item['image'],
                "email": user_email,
                "item_id": item["_id"],
                "itemCode": item_code,
                "item_name": item["item_name"],
                "item_category": item_category,
                "item_quantity": updated_quantity,
                "size": item_size,
                "item_price": item_price,
                "total_amount": updated_total_amount
            }
            db_cart.insert_one(cart_entry)

        return redirect(url_for('cart.cart'))

    else:
        item_price = float(item["item_price"])
        item_stock = int(item.get("item_quantity", 99999))  # fallback if stock not set

        query = {'email': user_email, 'itemCode': item["itemCode"]}
        existing_entry = db_cart.find_one(query)

        current_qty = existing_entry.get("item_quantity", 0) if existing_entry else 0
        updated_quantity = current_qty + item_quantity

        # Respect stock limit
        if updated_quantity > item_stock:
            updated_quantity = item_stock
            flash(f"⚠️ Only {item_stock} stock(s) available for this item.", "warning")
            return redirect(url_for('item_details.item_detail',item_id=item_id))
        # Respect max 10 limit
        if updated_quantity > 10:
            updated_quantity = 10
            flash("⚠️ You can only add up to 10 per item in the cart.", "warning")
            return redirect(url_for('item_details.item_detail',item_id=item_id))
        
        updated_total_amount = round(updated_quantity * item_price, 2)

        if existing_entry:
            db_cart.update_one(
                {'_id': existing_entry['_id']},
                {'$set': {"item_quantity": updated_quantity, "total_amount": updated_total_amount}}
            )
        else:
            cart_entry = {
                "image": item['image'],
                "email": user_email,
                "item_id": item["_id"],
                "itemCode": item['itemCode'],
                "item_name": item["item_name"],
                "item_category": item_category,
                "item_quantity": updated_quantity,
                "item_price": item_price,
                "total_amount": updated_total_amount
            }
            db_cart.insert_one(cart_entry)

        return redirect(url_for('cart.cart'))

@itemdt_bp.route("/preorder", methods=["POST"])
def preorder():
    if 'user' not in session:
        flash("Please log in to place a pre-order", "warning")
        return redirect(url_for('login.login_'))

    user_email = session['user']['email']
    item_id = request.form.get("item_id")
    item_name = request.form.get('item_name')
    size_selection = request.form.get("size_selection") 
    

    item_code = None
    size = None
    price = None

    if size_selection:  
     
        parts = size_selection.split("|")
        item_code, size, price, qty = parts[0], parts[1], parts[2], parts[3]
    else:
        # non-size item (from hidden input)
        item_code = request.form.get("item_code")
        price = int(request.form.get('item_price'))
        
    ph_time = datetime.now(pytz.timezone('Asia/Manila'))
    date_str = ph_time.strftime('%Y-%m-%d')
    time_str = ph_time.strftime('%H:%M:%S')  # military time
    
    preorder_doc = {
        "email": user_email,
        "item_name": item_name,
        "item_id": item_id,
        "itemCode": item_code,
        "item_price": price,
        "size": size if size_selection else None,
        "status": "pre-order",   
        "created_at": ph_time,
        "date": date_str,
        "time": time_str
    }

    db_preorder.insert_one(preorder_doc)

    flash("Your pre-order has been placed. We'll notify you when it's back in stock.", "success")
    return redirect(url_for("home"))