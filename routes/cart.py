from flask import Flask, url_for, redirect, render_template, session, flash, request, Blueprint
from db_proware import *

cartbp = Blueprint('cart', __name__, url_prefix='/cart')

def get_email():
    user_email = session['user']['email']
    return user_email

@cartbp.route('/cart', methods=['POST','GET'])
def cart():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    cart_items = list(db_cart.find({"email": get_email()}))
    
    return render_template('cart.html', cart_items=cart_items)

@cartbp.route('/remove_from_cart', methods=['GET'])
def remove_from_cart():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    item_id = request.args.get('item_id')
    item_code = request.args.get('item_code')
 

    if item_code:
        db_cart.delete_one({"email": get_email(), "itemCode": item_code})
    elif item_id:
        db_cart.delete_one({"email": get_email(), "item_id": item_id})

    return redirect(url_for('cart.cart'))


@cartbp.route('/update_quantity', methods=['POST','GET'])
def update_quantity():
    if 'user' not in session:
        return redirect(url_for('login.login_'))

    item_id = request.args.get('item_id')
    item_code = request.args.get('item_code')
    item_quantity = int(request.args.get('item_quantity'))
   
    cart_item = db_cart.find_one({"item_id": item_id, "email": get_email(), "itemCode": item_code})
    stock_item = db_items.find_one({"_id": item_id})

    if cart_item and stock_item and stock_item.get("sizes"):
        available_stock = 0
        for s in stock_item["sizes"]:
            if s.get("itemCode", "").strip() == item_code.strip():
                available_stock = int(s.get("quantity", 0))
                break

        new_quantity = max(1, min(item_quantity, available_stock))
        if new_quantity > 10:
            new_quantity = 10

        total_amount = int(cart_item["item_price"] * new_quantity)

        result = db_cart.update_one(
            {"item_id": cart_item["item_id"], "email": get_email(), "itemCode": item_code},
            {"$set": {"item_quantity": new_quantity, "total_amount": total_amount}}
        )

        # print("cart quantity:", cart_item["item_quantity"])
        # print("new quantity:", new_quantity)
        # print("total amount:", total_amount)
        # print(result.raw_result)s
        # print("sizes updated")
        return redirect(url_for('cart.cart'))
    
    if cart_item and stock_item:
        
        available_stock = int(stock_item.get("item_quantity", 0))
        new_quantity = max(1, min(item_quantity, available_stock))

        if new_quantity > 10:
            new_quantity = 10
        
        total_amount = int(cart_item["item_price"] * new_quantity)

        db_cart.update_one(
            {"item_id": cart_item["item_id"]},
            {"$set": {"item_quantity": new_quantity, "total_amount": total_amount}}
        )
        print('walang sizes')
        return redirect(url_for('cart.cart'))
    else:  
        print("⚠️ Item not found in stock or cart")
        return redirect(url_for('cart.cart'))
