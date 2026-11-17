"""Buyer routes"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Farmer, Listing, Order, Review, Buyer
from routes.auth import login_required, buyer_required
from bson import ObjectId

buyer_bp = Blueprint("buyer", __name__, url_prefix="/buyer")


@buyer_bp.route("/dashboard")
@login_required
@buyer_required
def dashboard():
    buyer_id = session["user_id"]
    listings = Listing.find_all()
    orders = Order.find_by_buyer(buyer_id)
    # Active orders (not completed)
    active = [o for o in orders if o.get("orderStatus") != "Completed"]
    completed = [o for o in orders if o.get("orderStatus") == "Completed"]
    return render_template(
        "buyers/dashboard.html",
        listings=listings,
        orders=orders,
        active=active,
        completed=completed,
    )


@buyer_bp.route("/listings")
@login_required
@buyer_required
def listings():
    crop = request.args.get("crop", "")
    district = request.args.get("district", "")
    min_price = request.args.get("min_price", "")
    max_price = request.args.get("max_price", "")
    listings = Listing.filter(
        crop=crop or None,
        district=district or None,
        min_price=min_price or None,
        max_price=max_price or None,
    )
    return render_template("buyers/listings.html", listings=listings,
                           crop=crop, district=district,
                           min_price=min_price, max_price=max_price)


@buyer_bp.route("/farmers")
@login_required
@buyer_required
def farmers():
    query = (request.args.get("q") or "").strip()
    if query:
        farmers = Farmer.search(query)
    else:
        farmers = Farmer.find_all()
    return render_template("buyers/farmers.html", farmers=farmers, query=query)


@buyer_bp.route("/orders")
@login_required
@buyer_required
def orders():
    buyer_id = session["user_id"]
    orders = Order.find_by_buyer(buyer_id)
    farmers = Farmer.find_all()
    return render_template("buyers/orders.html", orders=orders, farmers=farmers)


@buyer_bp.route("/orders/create", methods=["GET", "POST"])
@login_required
@buyer_required
def create_order():
    if request.method == "POST":
        listing_id = request.form.get("listingId")
        listing = Listing.find_by_id(listing_id)
        if not listing:
            flash("Listing not found.", "danger")
            return redirect(url_for("buyer.listings"))
        farmer_id = str(listing["farmerId"])
        quantity = float(request.form.get("quantityOrdered") or 0)
        price_per_unit = float(listing.get("pricePerUnit") or 0)
        total_price = price_per_unit * quantity
        data = {
            "listingId": ObjectId(listing_id),
            "farmerId": ObjectId(farmer_id),
            "buyerId": ObjectId(session["user_id"]),
            "quantityOrdered": quantity,
            "totalPrice": total_price,
            "unitPriceSnapshot": price_per_unit,
            "cropNameSnapshot": listing.get("cropName"),
            "orderStatus": "Pending",
            "paymentStatus": "Unpaid",
            "paymentMethod": request.form.get("paymentMethod", ""),
            "paymentDate": request.form.get("paymentDate") or None,
            "deliveryMethod": request.form.get("deliveryMethod", "Pickup"),
            "deliveryNotified": False,
            "deliveryConfirmed": False,
        }
        Order.create(data)
        flash("Order placed successfully. The farmer will review it.", "success")
        return redirect(url_for("buyer.orders"))
    listings = Listing.find_all()
    farmers = Farmer.find_all()
    return render_template("buyers/create_order.html", listings=listings, farmers=farmers)


@buyer_bp.route("/orders/edit/<id>", methods=["GET", "POST"])
@login_required
@buyer_required
def edit_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["buyerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("buyer.orders"))
    if order.get("orderStatus") not in ("Pending",):
        flash("Only pending orders can be edited.", "warning")
        return redirect(url_for("buyer.orders"))
    if request.method == "POST":
        Order.update(id, {
            "quantityOrdered": float(request.form.get("quantityOrdered") or 0),
            "paymentMethod": request.form.get("paymentMethod", ""),
            "paymentDate": request.form.get("paymentDate") or None,
            "deliveryMethod": request.form.get("deliveryMethod", "Pickup"),
        })
        flash("Order updated successfully.", "success")
        return redirect(url_for("buyer.orders"))
    return render_template("buyers/edit_order.html", order=order)


@buyer_bp.route("/orders/pay/<id>", methods=["POST"])
@login_required
@buyer_required
def pay_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["buyerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("buyer.orders"))
    if order.get("paymentStatus") == "Paid":
        flash("Order already paid.", "info")
        return redirect(url_for("buyer.orders"))
    method = request.form.get("paymentMethod", order.get("paymentMethod", "Cash on delivery"))
    date = request.form.get("paymentDate") or None
    Order.mark_payment_paid(id, method=method, date=date)
    flash("Payment recorded successfully.", "success")
    return redirect(url_for("buyer.orders"))
@buyer_bp.route("/orders/cancel/<id>")
@login_required
@buyer_required
def cancel_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["buyerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("buyer.orders"))
    if order.get("orderStatus") != "Pending":
        flash("Only pending orders can be cancelled.", "warning")
        return redirect(url_for("buyer.orders"))
    Order.delete(id)
    flash("Order cancelled.", "info")
    return redirect(url_for("buyer.orders"))


@buyer_bp.route("/orders/confirm/<id>")
@login_required
@buyer_required
def confirm_delivery(id):
    order = Order.find_by_id(id)
    if not order or str(order["buyerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("buyer.orders"))
    if order.get("orderStatus") != "In Transit":
        flash("Order is not in transit.", "warning")
        return redirect(url_for("buyer.orders"))
    Order.mark_delivery_confirmed(id)
    flash("Delivery confirmed. Order completed.", "success")
    return redirect(url_for("buyer.orders"))


@buyer_bp.route("/reviews/add/<order_id>", methods=["GET", "POST"])
@login_required
@buyer_required
def add_review(order_id):
    order = Order.find_by_id(order_id)
    if not order or str(order["buyerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("buyer.orders"))
    if order.get("orderStatus") != "Completed":
        flash("You can only review completed orders.", "warning")
        return redirect(url_for("buyer.orders"))
    if request.method == "GET":
        farmer = Farmer.find_by_id(order["farmerId"])
        existing_review = Review.find_by_order(order_id)
        return render_template("buyers/add_review.html", order=order, farmer=farmer, existing_review=existing_review)
    rating = int(request.form.get("rating") or 0)
    comment = (request.form.get("comment") or "").strip()
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "danger")
        return redirect(url_for("buyer.orders"))
    Review.create({
        "orderId": ObjectId(order_id),
        "reviewerId": ObjectId(session["user_id"]),
        "revieweeId": order["farmerId"],
        "rating": rating,
        "comment": comment,
    })
    Farmer.add_rating(str(order["farmerId"]), rating)
    Order.update(order_id, {"reviewed": True})
    flash("Review submitted. Thank you!", "success")
    return redirect(url_for("buyer.orders"))
