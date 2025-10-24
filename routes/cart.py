from flask import jsonify, url_for, redirect, render_template, session, flash, request, Blueprint
from db_proware import *

cartbp = Blueprint('cart', __name__, url_prefix='/cart')

def get_email():
    user_email = session['user']['email']
    return user_email

# @cartbp.route('/getCartItem', methods=['GET','POST'])
# def getCartItem():
#     cart_items = list(db_cart.find({"email": get_email()}))
#     for item in cart_items:
#         item['_id'] = str(item['_id'])
#     return jsonify(cart_items)

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
    
    data = request.get_json()
    action = data.get('action')
    item_code = data.get('itemCode')
    item_id = data.get('item_id')

   
    cart_item = db_cart.find_one({"item_id": item_id, "email": get_email(), "itemCode": item_code})
    stock_item = db_items.find_one({"_id": item_id})
    current_qty = int(cart_item.get("item_quantity", 1))
    print(action, item_code, item_id, current_qty)

    if not cart_item or not stock_item:
        return jsonify({"message":"Item Not Found"}), 404
    
    if cart_item and stock_item and stock_item.get("sizes"):
            available_stock = 0
            for s in stock_item["sizes"]:
                if s.get("itemCode", "").strip() == item_code.strip():
                    available_stock = int(s.get("quantity", 0))
                    break

            if action == "add":
                new_quantity = min(current_qty + 1, available_stock, 10)
            elif action == "minus":
                new_quantity = max(current_qty - 1, 1)
            else:
                return jsonify({"message": "Invalid action"}), 400

            total_amount = int(cart_item["item_price"] * new_quantity)
            print(total_amount)
            db_cart.update_one(
                {"item_id": cart_item["item_id"], "email": get_email(), "itemCode": item_code},
                {"$set": {"item_quantity": new_quantity, "total_amount": total_amount}}
            )

            return jsonify({
                            "message": f"Quantity updated to {new_quantity}",
                            "new_quantity": new_quantity,
                            "total_amount": total_amount
                        }), 200
    
    if cart_item and stock_item:
        
            available_stock = int(stock_item.get("item_quantity", 0))
            new_quantity = max(1, min(current_qty, available_stock))

            if action == "add":
                new_quantity = min(current_qty + 1, available_stock, 10)
            elif action == "minus":
                new_quantity = max(current_qty - 1, 1)
            else:
                return jsonify({"message": "Invalid action"}), 400
            
            total_amount = int(cart_item["item_price"] * new_quantity)
            print(total_amount)
            db_cart.update_one(
                {"item_id": cart_item["item_id"]},
                {"$set": {"item_quantity": new_quantity, "total_amount": total_amount}}
            )
            print('walang sizes')
            return jsonify({
                                "message": f"Quantity updated to {new_quantity}",
                                "new_quantity": new_quantity,
                                "total_amount": total_amount
                            }), 200

@cartbp.route('/pre-order')
def preOrder():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    user = session.get('user')
    email = user.get('email')

    preOrderUser = list(db_preorder.find({'email': email}).sort([("order_date", -1), ("order_time", -1)]))
    # item_size = db_items.find(item_size = db_items.find_one({'sizes.itemCode': itemCode}))
    # item = db_items.find_one({'itemCode': itemCode})

    return render_template('pre-order.html',preOrderUser = preOrderUser)

# @cartbp.route('/update_quantity', methods=['POST','GET'])
# def update_quantity():
#     if 'user' not in session:
#         return redirect(url_for('login.login_'))

#     item_id = request.args.get('item_id')
#     item_code = request.args.get('item_code')
#     item_quantity = int(request.args.get('item_quantity'))
   
#     cart_item = db_cart.find_one({"item_id": item_id, "email": get_email(), "itemCode": item_code})
#     stock_item = db_items.find_one({"_id": item_id})

#     if cart_item and stock_item and stock_item.get("sizes"):
#         available_stock = 0
#         for s in stock_item["sizes"]:
#             if s.get("itemCode", "").strip() == item_code.strip():
#                 available_stock = int(s.get("quantity", 0))
#                 break

#         new_quantity = max(1, min(item_quantity, available_stock))
#         if new_quantity > 10:
#             new_quantity = 10

#         total_amount = int(cart_item["item_price"] * new_quantity)

#         result = db_cart.update_one(
#             {"item_id": cart_item["item_id"], "email": get_email(), "itemCode": item_code},
#             {"$set": {"item_quantity": new_quantity, "total_amount": total_amount}}
#         )

#         # print("cart quantity:", cart_item["item_quantity"])
#         # print("new quantity:", new_quantity)
#         # print("total amount:", total_amount)
#         # print(result.raw_result)s
#         # print("sizes updated")
#         return redirect(url_for('cart.cart'))
    
#     if cart_item and stock_item:
        
#         available_stock = int(stock_item.get("item_quantity", 0))
#         new_quantity = max(1, min(item_quantity, available_stock))

#         if new_quantity > 10:
#             new_quantity = 10
        
#         total_amount = int(cart_item["item_price"] * new_quantity)

#         db_cart.update_one(
#             {"item_id": cart_item["item_id"]},
#             {"$set": {"item_quantity": new_quantity, "total_amount": total_amount}}
#         )
#         print('walang sizes')
#         return redirect(url_for('cart.cart'))
#     else:  
#         print("⚠️ Item not found in stock or cart")
#         return redirect(url_for('cart.cart'))
