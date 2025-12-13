from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, Blueprint, jsonify
import pytz
from db_proware import *

reportbp = Blueprint('report', __name__, url_prefix='/report')

@reportbp.route('/rangeDate', methods=['GET','POST'])
def getRangeReports():
    data = request.get_json()
    startDate = data.get('dateStart')
    endDate = data.get('dateEnd')

    order = db_orders_history.find(
        {
            "order_date": {"$gte": startDate, "$lte": endDate}
        })
    result = list(order)
    for id in result:
        id['_id'] = str(id['_id'])

    totalRange = sum(doc.get("total_amount", 0) or 0 for doc in result)

    return jsonify({
        "result": result,
        "totalRange": totalRange,
        "dateStart": startDate,
        "dateEnd": endDate
    })

@reportbp.route('/weekly', methods=['GET'])
def getWeeklyReports():
  current_time = datetime.now(pytz.timezone('Asia/Manila'))
  start_week = current_time - timedelta(days=current_time.weekday())  
  end_week = start_week + timedelta(days=6)  
  order = db_orders_history.find()
  result = []

  for h in order:
                try:
                    order_date = datetime.strptime(h['order_date'], '%Y-%m-%d')
                    if start_week.date() <= order_date.date() <= end_week.date():
                        result.append(h)
                except:
                    continue

  total_income = sum(order.get('total_amount', 0.0) for order in result)
  for order in result:
    order['_id'] = str(order['_id'])
  return jsonify({
      'result': result,
      'totalWeekly': total_income
  })
  
@reportbp.route('/monthly', methods=['GET'])
def getMonthlyReports():
   
   current_time = datetime.now(pytz.timezone('Asia/Manila'))
   year = current_time.year
   month = current_time.month
   strYear = str(year)
   history = db_orders_history.find({ "order_date": {"$regex": f"^{year}-{month:02d}", "$options": "i"}})
   result = list(history)
   print( month, year)

   match month:
        case 1:
            strMonth = "January"
        case 2:
            strMonth = "February"
        case 3:
            strMonth = "March"
        case 4:
            strMonth = "April"
        case 5:
            strMonth = "May"
        case 6:
            strMonth = "June"
        case 7:
            strMonth = "July"
        case 8:
            strMonth = "August"
        case 9:
            strMonth = "September"
        case 10:
            strMonth = "October"
        case 11:
            strMonth = "November"
        case 12:
            strMonth = "December"
        case _:
            strMonth = "Invalid month"

   totalMonthSales = sum(order.get('total_amount', 0.0) for order in result)
   for order in result:
    order['_id'] = str(order['_id'])

   return jsonify({
       'result': result,
       'totalMonthly': totalMonthSales,
       'month': strMonth,
       'year': strYear
   })

@reportbp.route('/reports')
def reports():
    return render_template('admin/reports.html')
@reportbp.route('/txt-reports')
def txtreports():
    return render_template('admin/txtbkreports.html')


@reportbp.route('/rangeDateTxt', methods=['GET', 'POST'])
def getRangeReportsTxt():
    data = request.get_json()
    startDate = data.get('dateStart')
    endDate = data.get('dateEnd')

    order = textbookdb.find(
        {
            "order_date": {"$gte": startDate, "$lte": endDate}
        })
    result = list(order)
    for doc in result:
        doc['_id'] = str(doc['_id'])

    totalRange = sum(doc.get("total_amount", 0) or 0 for doc in result)

    return jsonify({
        "result": result,
        "totalRange": totalRange,
        "dateStart": startDate,
        "dateEnd": endDate
    })


@reportbp.route('/weeklyTxt', methods=['GET'])
def getWeeklyReportsTxt():
    current_time = datetime.now(pytz.timezone('Asia/Manila'))
    start_week = current_time - timedelta(days=current_time.weekday())
    end_week = start_week + timedelta(days=6)
    order = textbookdb.find()
    result = []

    for h in order:
        try:
            order_date = datetime.strptime(h['order_date'], '%Y-%m-%d')
            if start_week.date() <= order_date.date() <= end_week.date():
                result.append(h)
        except:
            continue

    total_income = sum(order.get('total_amount', 0.0) for order in result)
    for order in result:
        order['_id'] = str(order['_id'])
    return jsonify({
        'result': result,
        'totalWeekly': total_income
    })


@reportbp.route('/monthlyTxt', methods=['GET'])
def getMonthlyReportsTxt():
    current_time = datetime.now(pytz.timezone('Asia/Manila'))
    year = current_time.year
    month = current_time.month
    strYear = str(year)
    history = textbookdb.find(
        {"order_date": {"$regex": f"^{year}-{month:02d}", "$options": "i"}})
    result = list(history)

    match month:
        case 1:
            strMonth = "January"
        case 2:
            strMonth = "February"
        case 3:
            strMonth = "March"
        case 4:
            strMonth = "April"
        case 5:
            strMonth = "May"
        case 6:
            strMonth = "June"
        case 7:
            strMonth = "July"
        case 8:
            strMonth = "August"
        case 9:
            strMonth = "September"
        case 10:
            strMonth = "October"
        case 11:
            strMonth = "November"
        case 12:
            strMonth = "December"
        case _:
            strMonth = "Invalid month"

    totalMonthSales = sum(order.get('total_amount', 0.0) for order in result)
    for order in result:
        order['_id'] = str(order['_id'])

    return jsonify({
        'result': result,
        'totalMonthly': totalMonthSales,
        'month': strMonth,
        'year': strYear
    })