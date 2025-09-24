import csv
import io
from bson import ObjectId, Regex
from flask import Blueprint, redirect, render_template, request, session, url_for
from db_proware import *
from routes.audit_log import audit_log

system_adminbp = Blueprint('system_admin', __name__, url_prefix='/system_admin')
 
    
# @system_adminbp.route('/login', methods=['GET', 'POST'])
# def login():
#     if 'sys_admin' in session:
#         return redirect(url_for('index'))

#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         sys_admin = db_account.find_one({"email": email})
#         print(sys_admin)

#         if sys_admin:
#             if sys_admin['password'] == password:
#                 if sys_admin.get('roles') == 'system_admin':
#                     session['system_admin'] = {
#                         'fullname': sys_admin['fullname'],
#                         'email': sys_admin['email'],
#                         'roles': sys_admin['roles'],}
#                     return redirect(url_for('system_admin'))
#                 else:
#                     print("Access denied: Not a system admin.")
#                     return render_template('login.html')
#             else:
#                 print("Incorrect password.")
#                 return render_template('login.html')
#         else:
#              print("Email not found.")
#              return render_template('login.html')

#     return render_template('login.html')

@system_adminbp.route('/logout', methods=['GET', 'POST'])
def logout():
   if 'user' in session:
        print("logout account")
        session.pop('user')
   return redirect(url_for('login.login_'))

@system_adminbp.route('/edit_account/<account_id>', methods=['GET', 'POST'])
def edit_account(account_id):
    if 'user'in session:
        #audit_log("Edit Account Page")
        account = db_account.find_one({'_id': ObjectId(account_id)})

        if not account:
            print("Account not found", "danger")
            return redirect(url_for('accounts'))

        if request.method == 'POST':
            new_role = request.form.get('role')
            new_status = request.form.get('status')
            new_permissions = request.form.getlist('permissions')  

            db_account.update_one(
                {'_id': ObjectId(account_id)},
                {'$set': {
                    'role': new_role,
                    'status': new_status,
                    'permissions': new_permissions
                }}
            )

            print("Account updated successfully", "success")
            #audit_log("Edit Account Modified")
            return redirect(url_for('system_admin.accounts'))

        return render_template('system_admin/edit_accounts.html', account=account)
    else:
        return redirect(url_for('login.login_'))

@system_adminbp.route('/accounts', methods=['GET', 'POST'])
def accounts():
    if 'user'in session:
        #audit_log("Viewed Accounts")
        search = request.form.get('search', '').strip()
        filter_by = request.form.get('filter_by', 'email')  

        if request.method == 'POST' and search:
            query = {}
            if filter_by == 'email':
                query = {'email': {'$regex': search, '$options': 'i'}}
            elif filter_by == 'role':
                query = {'role': {'$regex': search, '$options': 'i'}}
            accounts = list(db_account.find(query))
        else:
            accounts = list(db_account.find())

        return render_template('system_admin/accounts.html', accounts=accounts, search=search, filter_by=filter_by)
    else:
        return redirect(url_for('login.login_'))

@system_adminbp.route('/dt_mgrt', methods=['GET', 'POST'])
def data_mgrt():
    if 'user'in session:
        #audit_log("Batch Upload Page")
        return render_template('system_admin/dt_migrate.html')
    else:
        return redirect(url_for('login.login_'))

@system_adminbp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            print("Please upload a valid CSV file.")
            return redirect(url_for('system_admin.data_mgrt'))

        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)

        inserted = 0
        skipped = 0

        for row in reader:
            student_id = row.get('student_id')
            if not student_id:
                continue

            # icheck dito kung if exist ba pag oo skip sa csv row
            existing = db_account.find_one({"student_id": student_id})
            if existing:
                skipped += 1    
                continue

            # Insert siya pag di existing student 
            db_account.insert_one(row)
            inserted += 1

        print(f"Upload complete: {inserted} inserted, {skipped} skipped (existing).")
        #audit_log("Data Migration")
        return redirect(url_for('system_admin.data_mgrt'))

    return redirect(url_for('system_admin.data_mgrt'))
 
@system_adminbp.route('/audit_log-access', methods=['GET', 'POST'])
def audit_log_access():
    if 'user'in session:
        #audit_log("Audit Log Accessing Page")
        if request.method == 'POST':
            entered_password = request.form['password']
            admin = db_account.find_one({"email": 'catalan.299018@novaliches.sti.edu.ph'})
        
            if admin and admin['password'] == entered_password:
                session['audit_verified'] = True
                return redirect(url_for('system_admin.audit_log'))
            else:
                return render_template('system_admin/audit.html', error="Wrong password!")

        return render_template('system_admin/audit.html')
    else:
        return redirect(url_for('login.login_'))

@system_adminbp.route('/audit-log')
def audit_log():
    if 'user'in session:
        #audit_log("Audit Log Viewing")
        query = request.args.get('query', '').strip().lower()
        filter_type = request.args.get('filter', 'all')

        filter_query = {}

        if query:
            if filter_type == 'date':
                filter_query['timestamp'] = {
                    "$regex": Regex(query, "i")
                }
            elif filter_type == 'email':
                filter_query['admin_email'] = {'$regex': query, '$options': 'i'}
            elif filter_type == 'action':
                filter_query['action'] = {'$regex': query, '$options': 'i'}
            else:
                filter_query['$or'] = [
                    {'admin_email': {'$regex': query, '$options': 'i'}},
                    {'action': {'$regex': query, '$options': 'i'}},
                    {'timestamp': {'$regex': query, '$options': 'i'}}
                ]

        logs = list(db_auditlog.find(filter_query).sort('timestamp', -1))
        return render_template('system_admin/audit_log.html', logs=logs, query=query, filter_type=filter_type)
    else:
        return redirect(url_for('login.login_'))

