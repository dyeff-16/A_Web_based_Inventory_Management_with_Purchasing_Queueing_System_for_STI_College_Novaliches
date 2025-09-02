from flask import Blueprint, Flask, url_for, redirect, render_template, session, flash, request
from db_proware import *


queuebp= Blueprint('queue', __name__, url_prefix='/queue')

@queuebp.route("/queue")
def queue():
    # Get orders that are Waiting or Ready, sorted by pickup_number
    orders = list(db_orders.find(
        {"pickup_status": {"$in": ["Waiting", "Ready"]}}
    ).sort("pickup_number", 1))

    now_serving = orders[0]["pickup_number"] if orders else None
    upcoming = [o["pickup_number"] for o in orders[1:5]]  # next 4 numbers

    return render_template("queue.html",
                           now_serving=now_serving,
                           upcoming=upcoming)
