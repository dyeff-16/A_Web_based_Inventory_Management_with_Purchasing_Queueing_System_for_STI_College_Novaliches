from pymongo import MongoClient

dbClient = MongoClient("mongodb+srv://stinovalichesproware:!Stinovalichesproware_15@prowarestinovaliches.fy5dqzc.mongodb.net/")

db_admin = dbClient.Proware
db_items = db_admin.items  # Collection for items/products
db_account = db_admin.accounts  # Collection for user accounts
db_cart = db_admin.cart  # Collection for user carts
db_orders = db_admin.orders  # Collection for user orders
db_notification = db_admin.notification
db_orders_history = db_admin.order_history
db_history = db_admin.user_history
