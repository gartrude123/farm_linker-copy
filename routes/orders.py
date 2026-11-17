"""Order routes (shared/general)"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Order, Listing, Farmer, Buyer
from routes.auth import login_required

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/")
@login_required
def list_orders():
    role = session.get("user_role", "buyer")
    user_id = session["user_id"]
    if role == "farmer":
        orders = Order.find_by_farmer(user_id)
    else:
        orders = Order.find_by_buyer(user_id)
    return render_template("orders.html", orders=orders, role=role)
