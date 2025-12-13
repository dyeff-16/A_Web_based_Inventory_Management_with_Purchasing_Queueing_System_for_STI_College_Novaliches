from pymongo import MongoClient

# dbClient = MongoClient("mongodb+srv://stinovalichesproware:!Stinovalichesproware_15@prowarestinovaliches.fy5dqzc.mongodb.net/")
dbClient = MongoClient("mongodb://Proware:Stinovalichesproware-15@72.60.196.33:27017/admin")

db_admin = dbClient.Proware
db_items = db_admin.items  # Collection for items/products
db_account = db_admin.accounts  # Collection for user accounts
db_cart = db_admin.cart  # Collection for user carts
db_orders = db_admin.orders  # Collection for user orders
db_notification = db_admin.notification
db_orders_history = db_admin.order_history
db_history = db_admin.user_history
db_info =db_admin.info
db_preorder = db_admin.pre_order
db_auditlog = db_admin.audit_log
db_account_pending = db_admin.pendingAccount
textbookdb = db_admin.textbook