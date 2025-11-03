from flask import Blueprint, jsonify, render_template, redirect, url_for, request
from datetime import datetime
from db_proware import *

dashboardbp = Blueprint('admin_dashboard', __name__,url_prefix='/admin_dashboard')  

@dashboardbp.route('/topItems')
def topItems():
    orders = db_orders_history.find({}, {'items': 1})
    items = {}

    for order in orders:
        if 'items' in order:
            for item in order['items']:
                code = item.get("itemCode") or item.get("item_code")
                name = item.get("item_name", "Unknown Item")
                qty = item.get("qty", 1)  

                if code:
                    if code not in items:
                        items[code] = {"name": name, "orders": 0, "total_qty": 0}
                    items[code]["orders"] += 1       
                    items[code]["total_qty"] += qty  


    top_items = sorted(items.values(), key=lambda x: x["total_qty"], reverse=True)[:10]

    return jsonify(top_items)

@dashboardbp.route('/totalBenta')
def totalBenta():

    orders = db_orders_history.find({})
    total = 0

    for order in orders:
        total += order['total_amount']

    return jsonify({'total': total})


@dashboardbp.route('/pieStock')
def pieStock():
    noStock = db_items.count_documents({"item_quantity": {"$lte": 0}})
    onStock = db_items.count_documents({"item_quantity": {"$gt": 0}})

    noStockSize = db_items.count_documents({
        "sizes": {"$exists": True, "$not": {"$elemMatch": {"quantity": {"$gt": 0}}}}
    })
    onStockSize = db_items.count_documents({
        "sizes": {"$elemMatch": {"quantity": {"$gt": 0}}}
    })
    print(f'noStock: sizes {noStockSize} and {noStock}')
    print(f'onStock: sizes {onStockSize} and {onStock}')

    out_of_stock = noStock + noStockSize
    on_stock = onStock + onStockSize

    return jsonify({"out_of_stock": out_of_stock, "on_stock": on_stock})

@dashboardbp.route('/lowStock')
def lowStock():

    lowStock = db_items.count_documents({
        "item_quantity": {"$gt": 0, "$lt": 10}
    })

    lowStockSize = db_items.count_documents({
        "sizes": {"$elemMatch": {"quantity": {"$gt": 0, "$lt": 10}}}
    })

    lowstock = lowStock + lowStockSize 

    return jsonify({"lowstock": lowstock})

@dashboardbp.route('/highStock')
def highStock():

    highStock = db_items.count_documents({
        "item_quantity": {"$gt": 100}
    })
 
    highStockSize = db_items.count_documents({
        "sizes": {"$elemMatch": {"quantity": {"$gt": 100}}}
    })

    highstock = highStock + highStockSize

    return jsonify({"highstock": highstock})