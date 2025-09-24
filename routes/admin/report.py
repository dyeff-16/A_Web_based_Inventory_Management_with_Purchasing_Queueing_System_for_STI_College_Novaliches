# from datetime import datetime
# from flask import Flask, url_for, redirect, render_template, session, request, Blueprint
# import pytz
# from db_proware import *

# reportbp = Blueprint('report', __name__, url_prefix='/report')

# @reportbp.route('/monthly_report', methods=['GET'])
# def monthly_report():
#     if 'user' not in session:
#         return redirect(url_for('home'))
#     # Get the current date and extract the month and year
#     current_date = datetime.now(pytz.timezone('Asia/Manila'))
#     current_month = current_date.month
#     current_year = current_date.year

#     # Query order history for orders placed in the current month and year
#     history = db_orders_history.find({
#         "date": {
#             "$regex": f"^{current_year}-{current_month:02d}",  # Filter by current year and month (e.g., "2025-04")
#             "$options": "i"
#         }
#     })

#     # Calculate total orders and total amount
#     total_orders = 0
#     total_amount = 0.0

#     for order in history:
#         total_orders += 1
#         total_amount += order.get('total_amount', 0.0)  # Make sure 'amount' field is available

#     # Render the result in the template
#     return render_template('reports.html', total_orders=total_orders, total_amount=total_amount, current_year=current_year, current_month=current_month)

from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, Blueprint
import pytz
from db_proware import *

reportbp = Blueprint('report', __name__, url_prefix='/report')

@reportbp.route('/generate', methods=['GET', 'POST'])
def generate_report():
    if 'user' not in session:
        return redirect(url_for('home'))

    report_type = request.form.get('report_type')
    current_time = datetime.now(pytz.timezone('Asia/Manila'))

    result = []
    total_income = 0
    message = ""

    if request.method == 'POST':
        if report_type == 'monthly':
            year = current_time.year
            month = current_time.month
            history = db_orders_history.find({
                "order_date": {"$regex": f"^{year}-{month:02d}", "$options": "i"}
            })
            result = list(history)
            total_income = sum(order.get('total_amount', 0.0) for order in result)
            month_name = current_time.strftime('%B')
            message = f"Monthly Report for {month_name} {year}"

        elif report_type == 'weekly':
            start_week = current_time - timedelta(days=current_time.weekday())  # Monday
            end_week = start_week + timedelta(days=6)  # Sunday
            history = db_orders_history.find()
            result = []

            for h in history:
                try:
                    order_date = datetime.strptime(h['order_date'], '%Y-%m-%d')
                    if start_week.date() <= order_date.date() <= end_week.date():
                        result.append(h)
                except:
                    continue

            total_income = sum(order.get('total_amount', 0.0) for order in result)
            message = f"Weekly Report: {start_week.strftime('%B %d, %Y')} - {end_week.strftime('%B %d, %Y')}"

        elif report_type == 'sales':
            history = db_orders_history.find()
            items = {}
            for order in history:
                for item in order.get('items', []):
                    name = item['item_name']
                    qty = item['quantity']
                    items[name] = items.get(name, 0) + qty
            return render_template('reports.html', items=items, report_type='sales', message="Item Sales Report (All-Time)")

        else:
            return render_template('reports.html', message="Select a report type")

    return render_template('reports.html', report_type=report_type, orders=result, total_income=total_income, message=message)
