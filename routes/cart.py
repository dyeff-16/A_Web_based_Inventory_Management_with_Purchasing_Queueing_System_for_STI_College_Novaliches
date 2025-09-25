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


    if cart_item:
        
        new_quantity = min(max(item_quantity, 1), 10)
        total_amount = int(cart_item["item_price"] * new_quantity)

        db_cart.update_one(
            {'_id': cart_item['_id']},
            {'$set': {"item_quantity": new_quantity, "total_amount": total_amount}}
        )

    return redirect(url_for('cart.cart'))
