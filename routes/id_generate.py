import base64
from flask import Flask, url_for, redirect, render_template, session, request, Blueprint
import pymongo
from db_proware import *

def generate_item_id(category_prefix):
    last_item = db_items.find_one(
        {"_id": {"$regex": f"^{category_prefix}-"}}, 
        sort=[("_id", -1)]
    )
    if last_item:
        last_id_num = int(last_item["_id"].split("-")[1])
    else:
        last_id_num = 0
    new_id = f"{category_prefix}-{last_id_num + 1:04d}"
    return new_id

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
         return 0