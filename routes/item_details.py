from datetime import datetime
from flask import Flask, url_for, redirect, render_template, session, flash, request, Blueprint
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
        print(f"Size selection value: {size_selection}")  
        
        split_values = size_selection.split('|')
        if len(split_values) != 4:
            return "Error: Invalid format for size selection", 400

        item_code, item_size, item_price, item_quantities = split_values
        item_price = float(item_price)

        cart_entry = {
            "image": item['image'],
            "email": session["user"]['email'],
            "item_id": item["_id"],
            "itemCode": item_code,
            "item_name": item["item_name"],
            "item_category": item_category,
            "item_quantity": item_quantity,
            "size": item_size,
            "item_price": item_price,
            "total_amount": round(item_price * item_quantity, 2)
        }

        query = {'email': user_email, 'itemCode': item_code}
        existing_entry = db_cart.find_one(query)

        if existing_entry:
            updated_quantity = existing_entry.get("item_quantity", 0) + item_quantity
            updated_total_amount = updated_quantity * item_price
            db_cart.update_one(
                {'itemCode': existing_entry['itemCode']},
                {'$set': {"item_quantity": updated_quantity, "total_amount": round(updated_total_amount, 2)}}
            )
        else:
            db_cart.insert_one(cart_entry)

        return redirect(url_for('cart.cart'))

    else:  
        item_price = float(item["item_price"]) 
        total_amount = item_price * item_quantity

        cart_entry = { 
            "image": item['image'],
            "email": session["user"]['email'],
            "item_id": item["_id"],
            "itemCode": item['itemCode'],
            "item_name": item["item_name"],
            "item_category": item_category,
            "item_quantity": item_quantity,
            "item_price": item_price,
            "total_amount": round(total_amount, 2)
        }

        query = {'email': user_email, 'itemCode': item["itemCode"]}
        existing_entry = db_cart.find_one(query)

        if existing_entry:
           
            updated_quantity = existing_entry.get("item_quantity", 0) + item_quantity
            updated_total_amount = updated_quantity * item_price
            db_cart.update_one(
                {'itemCode': existing_entry['itemCode']},
                {'$set': {"item_quantity": updated_quantity, "total_amount": round(updated_total_amount, 2)}}
            )
        else:
            # Insert a new cart entry if it doesn't exist
            db_cart.insert_one(cart_entry)

        return redirect(url_for('cart.cart'))

@itemdt_bp.route("/preorder", methods=["POST"])
def preorder():
    if 'user' not in session:
        flash("Please log in to place a pre-order", "warning")
        return redirect(url_for('login.login_'))

    user_email = session['user']['email']
    item_id = request.form.get("item_id")
    size_selection = request.form.get("size_selection")  # only exists for size-based items

    # default values
    item_code = None
    size = None
    price = None

    if size_selection:  
        # size format: itemCode|size|price|quantity
        parts = size_selection.split("|")
        item_code, size, price, qty = parts[0], parts[1], parts[2], parts[3]
    else:
        # non-size item (from hidden input)
        item_code = request.form.get("item_code")

    preorder_doc = {
        "email": user_email,
        "itemCode": item_code,
        "size": size if size_selection else None,
        "status": "pending",   # pending until restock
        "created_at": datetime.utcnow()
    }

    # insert into preorders collection
    db_preorder.insert_one(preorder_doc)

    flash("Your pre-order has been placed. We'll notify you when it's back in stock.", "success")
    return redirect(url_for("home"))