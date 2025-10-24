import csv
import io
from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
from db_proware import *
from routes.audit_log import audit_log

system_adminbp = Blueprint('system_admin', __name__, url_prefix='/system_admin')

@system_adminbp.route('/logout', methods=['GET', 'POST'])
def logout():
   if 'user' in session:
        print("logout account")
        session.pop('user')
   return redirect(url_for('login.login_'))

@system_adminbp.route('/edit_account/<int:student_id>', methods=['GET', 'POST'])
def edit_account(student_id):

    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    account = db_account.find_one({'student_id': student_id})

    if not account:
        print("Account not found", "danger")
        return redirect(url_for('system_admin.accounts'))

    return render_template('system_admin/edit_accounts.html', account=account)


@system_adminbp.route('/submitRoles', methods=['POST'])
def submitRoles():
    data = request.get_json()
    email = data.get('email')
    roles = data.get('selectRoles')
    status = data.get('selectStatus')
    productPermission = data.get('productPermission')
    reportsPermission = data.get('reportsPermission')
    ordersPermission = data.get('ordersPermission')
    queuePermission = data.get('queuePermission')

    dictPermission = {
        'product': productPermission,
        'report': reportsPermission,
        'orders': ordersPermission,
        'queue': queuePermission
    }
    
    db_account.update_one(
                {'email': email},
                {'$set': {
                    'roles': roles,
                    'status': status,
                    'permissions': dictPermission
                }}
            )
    return jsonify({
        'message': 'success update account'
    })    
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

@system_adminbp.route('/audit-log', methods=['GET', 'POST'])
def audit_log():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    return render_template('system_admin/audit_log.html')

@system_adminbp.route('/auditLog', methods=['GET', 'POST'])
def auditlog():
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form or {}
        query = (data.get('inputAuditlog') or '').strip()
        filter_type = (data.get('selectFilter') or 'all').strip()
    else:
        query, filter_type = '', 'all'

    filter_query = {}

    if query:
        rx = {'$regex': query, '$options': 'i'}
        if filter_type == 'datetime':
            filter_query['datetime'] = rx
        elif filter_type == 'email':
            filter_query['email'] = rx
        elif filter_type == 'action':
            filter_query['action'] = rx
        else:
            filter_query['$or'] = [
                {'email': rx},
                {'datetime': rx},
                {'action': rx}
            ]
    audit_log = list(
        db_auditlog.find(filter_query, {'_id': 0}).sort('_id', -1)
    )

    return jsonify({'auditlog': audit_log})

@system_adminbp.route('/accounts', methods=['GET', 'POST'])
def accounts():
    if 'user' not in session:
        return redirect(url_for('login.login_'))
    
    return render_template('system_admin/accounts.html')
     
@system_adminbp.route('/getAccount', methods=['GET','POST'])
def getAccount():
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    per_page = 20

    if request.method == 'GET':
        accounts = list(db_account.find({}).limit(per_page))
        for acc in accounts:
            acc['_id'] = str(acc['_id'])
        return jsonify({'accounts': accounts, 'message': 'Loaded first 20 (GET)'})

    
    data   = request.get_json()
    search = (data.get('searchInput')  or '').strip()
    status = (data.get('statusSelect') or '').strip().lower()
    role   = (data.get('roleSelect')   or '').strip().lower()


    IGNORED = {'', 'all', 'any', 'role', 'status', 'select'}
    query = {}

    if search:
        regex = {'$regex': search, '$options': 'i'}
        query['$or'] = [
            {'email': regex},
            {'roles': regex},    
            {'status': regex},
        ]

    if status not in IGNORED:
        query['status'] = {'$regex': f'^{status}$', '$options': 'i'}

    if role not in IGNORED:
        query['roles'] = {'$regex': role, '$options': 'i'}

    accounts = list(db_account.find(query).limit(per_page))
    for acc in accounts:
        acc['_id'] = str(acc['_id'])

    return jsonify({'accounts': accounts, 'message': 'Search results (POST)', 'query': query})

@system_adminbp.before_app_request
def maintenance_block():
    # paths that must always work
    allowed_paths = {
        '/system_admin', 
        '/system_admin/maintenance',       # maintenance page itself
        '/system_admin/toggle_maintenance' # your admin toggle endpoint (POST)
    }
    # always allow static files
    if request.path.startswith('/static/'):
        return None

    is_maintenance = bool(current_app.config.get('MAINTENANCE_MODE'))
    is_logged_in  = bool(session.get('user_id'))   # <- use your actual login key

    # If maintenance ON and user is NOT logged in → block to maintenance page
    if is_maintenance and not is_logged_in:
        if request.path in allowed_paths:
            return None

        # If it's an API call expecting JSON
        if request.accept_mimetypes.best == 'application/json':
            return jsonify({"status": "maintenance", "message": "Service temporarily unavailable."}), 503

        # Otherwise show the maintenance page
        return redirect(url_for('system_admin.maintenance_page'))
    
@system_adminbp.route('/maintenance')
def maintenance_page():
    return render_template('system_admin/maintenance.html'), 503

@system_adminbp.route('/toggle_maintenance', methods=['POST'])
def toggle_maintenance():
    # Only allow admins to call this (add your own admin check)
    current_app.config['MAINTENANCE_MODE'] = not current_app.config.get('MAINTENANCE_MODE', False)
    return {
        "maintenance": current_app.config['MAINTENANCE_MODE'],
        "message": "🛠 ON" if current_app.config['MAINTENANCE_MODE'] else "✅ OFF"
    }