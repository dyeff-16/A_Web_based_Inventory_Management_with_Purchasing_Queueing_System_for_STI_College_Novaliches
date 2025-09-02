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
    # Check if the user is logged in
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    # Get data from the form
    item_id = request.form.get('item_id')
    item_quantity = int(request.form.get("quantity", 1))
    item_category = request.form['item_category']
    
    # Find the item in the database
    item = db_items.find_one({"_id": item_id})
    if not item:
        return "Item not found", 404

    if item.get('sizes'):  # For items with sizes like 'Uniform' or 'Proware'
        size_selection = request.form.get('size_selection')
        print(f"Size selection value: {size_selection}")  # Debugging print statement
        
        # Split and check if there are exactly 2 parts
        split_values = size_selection.split('|')
        if len(split_values) != 3:
            return "Error: Invalid format for size selection", 400

        item_code, item_size, item_price = split_values
        item_price = float(item_price)

        # Prepare the cart entry for this item
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

        # Check if this item already exists in the cart
        query = {'email': session["user"], 'itemCode': item_code}
        existing_entry = db_cart.find_one(query)

        if existing_entry:
            # Update quantity and total amount if the item already exists
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

    else:  # For items without sizes (non-Uniform, non-Proware)
        item_price = float(item["item_price"])  # For items that don't have 'sizes'
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

        # Check if this item already exists in the cart
        query = {'email': session["user"], 'itemCode': item["itemCode"]}
        existing_entry = db_cart.find_one(query)

        if existing_entry:
            # Update quantity and total amount if the item already exists
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
