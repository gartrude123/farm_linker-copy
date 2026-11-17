"""Farmer routes"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Farmer, Listing, Order, Review, Buyer
from routes.auth import login_required, farmer_required
from bson import ObjectId

farmer_bp = Blueprint("farmer", __name__, url_prefix="/farmer")


@farmer_bp.route("/dashboard")
@login_required
@farmer_required
def dashboard():
    farmer_id = session["user_id"]
    listings = Listing.find_by_farmer(farmer_id)
    orders = Order.find_by_farmer(farmer_id)
    # Count orders by status
    pending = [o for o in orders if o.get("orderStatus") == "Pending"]
    approved = [o for o in orders if o.get("orderStatus") == "Approved"]
    in_transit = [o for o in orders if o.get("orderStatus") == "In Transit"]
    completed = [o for o in orders if o.get("orderStatus") == "Completed"]
    return render_template(
        "farmers/dashboard.html",
        listings=listings,
        orders=orders,
        pending=pending,
        approved=approved,
        in_transit=in_transit,
        completed=completed,
    )


@farmer_bp.route("/listings")
@login_required
@farmer_required
def listings():
    farmer_id = session["user_id"]
    listings = Listing.find_by_farmer(farmer_id)
    return render_template("farmers/listings.html", listings=listings)


@farmer_bp.route("/listings/add", methods=["GET", "POST"])
@login_required
@farmer_required
def add_listing():
    if request.method == "POST":
        data = {
            "farmerId": ObjectId(session["user_id"]),
            "cropName": (request.form.get("cropName") or "").strip(),
            "category": request.form.get("category", ""),
            "quantity": float(request.form.get("quantity") or 0),
            "unit": request.form.get("unit", ""),
            "pricePerUnit": float(request.form.get("pricePerUnit") or 0),
            "harvestDate": request.form.get("harvestDate") or None,
            "expiryDate": request.form.get("expiryDate") or None,
            "description": (request.form.get("description") or "").strip(),
            "images": [],
        }
        if not data["cropName"]:
            flash("Crop name is required.", "danger")
            return redirect(url_for("farmer.add_listing"))
        Listing.create(data)
        flash("Produce listing added successfully.", "success")
        return redirect(url_for("farmer.listings"))
    return render_template("farmers/add_listing.html")


@farmer_bp.route("/listings/edit/<id>", methods=["GET", "POST"])
@login_required
@farmer_required
def edit_listing(id):
    listing = Listing.find_by_id(id)
    if not listing:
        flash("Listing not found.", "danger")
        return redirect(url_for("farmer.listings"))
    if str(listing["farmerId"]) != session["user_id"]:
        flash("You can only edit your own listings.", "danger")
        return redirect(url_for("farmer.listings"))
    if request.method == "POST":
        Listing.update(id, {
            "cropName": (request.form.get("cropName") or "").strip(),
            "category": request.form.get("category", ""),
            "quantity": float(request.form.get("quantity") or 0),
            "unit": request.form.get("unit", ""),
            "pricePerUnit": float(request.form.get("pricePerUnit") or 0),
            "harvestDate": request.form.get("harvestDate") or None,
            "expiryDate": request.form.get("expiryDate") or None,
            "description": (request.form.get("description") or "").strip(),
        })
        flash("Listing updated successfully.", "success")
        return redirect(url_for("farmer.listings"))
    return render_template("farmers/edit_listing.html", listing=listing)


@farmer_bp.route("/listings/delete/<id>")
@login_required
@farmer_required
def delete_listing(id):
    listing = Listing.find_by_id(id)
    if listing and str(listing["farmerId"]) == session["user_id"]:
        Listing.delete(id)
        flash("Listing deleted.", "info")
    else:
        flash("Not authorized to delete this listing.", "danger")
    return redirect(url_for("farmer.listings"))


@farmer_bp.route("/buyers")
@login_required
@farmer_required
def buyers():
    query = (request.args.get("q") or "").strip()
    if query:
        buyers = Buyer.search(query)
    else:
        buyers = Buyer.find_all()
    return render_template("farmers/buyers.html", buyers=buyers, query=query)


@farmer_bp.route("/orders")
@login_required
@farmer_required
def orders():
    farmer_id = session["user_id"]
    orders = Order.find_by_farmer(farmer_id)
    buyers = Buyer.find_all()
    return render_template("farmers/orders.html", orders=orders, buyers=buyers)


@farmer_bp.route("/orders/approve/<id>")
@login_required
@farmer_required
def approve_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["farmerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("farmer.orders"))
    Order.update_status(id, "Approved")
    flash("Order approved.", "success")
    return redirect(url_for("farmer.orders"))


@farmer_bp.route("/orders/reject/<id>")
@login_required
@farmer_required
def reject_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["farmerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("farmer.orders"))
    Order.update_status(id, "Rejected")
    flash("Order rejected.", "info")
    return redirect(url_for("farmer.orders"))


@farmer_bp.route("/orders/reply/<id>", methods=["POST"])
@login_required
@farmer_required
def reply_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["farmerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("farmer.orders"))
    Order.mark_delivery_notified(
        id,
        notes=(request.form.get("deliveryNotes") or "").strip(),
        place=(request.form.get("deliveryPlace") or "").strip(),
        time=(request.form.get("deliveryTime") or "").strip(),
    )
    flash("Delivery notification sent to buyer.", "success")
    return redirect(url_for("farmer.orders"))


@farmer_bp.route("/orders/pay/<id>", methods=["POST"])
@login_required
@farmer_required
def pay_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["farmerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("farmer.orders"))
    if order.get("paymentStatus") == "Paid":
        flash("Order already paid.", "info")
        return redirect(url_for("farmer.orders"))
    method = request.form.get("paymentMethod", order.get("paymentMethod", "Cash on delivery"))
    date = request.form.get("paymentDate") or None
    Order.mark_payment_paid(id, method=method, date=date)
    flash("Payment recorded as received.", "success")
    return redirect(url_for("farmer.orders"))
@farmer_bp.route("/orders/complete/<id>", methods=["POST"])
@login_required
@farmer_required
def complete_order(id):
    order = Order.find_by_id(id)
    if not order or str(order["farmerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("farmer.orders"))
@farmer_bp.route("/reviews/add/<order_id>", methods=["GET", "POST"])
@login_required
@farmer_required
def add_review(order_id):
    order = Order.find_by_id(order_id)
    if not order or str(order["farmerId"]) != session["user_id"]:
        flash("Order not found or not authorized.", "danger")
        return redirect(url_for("farmer.orders"))
    if order.get("orderStatus") != "Completed":
        flash("You can only review completed orders.", "warning")
        return redirect(url_for("farmer.orders"))
    if request.method == "GET":
        buyer = Buyer.find_by_id(order["buyerId"])
        existing_review = Review.find_by_order(order_id)
        return render_template("farmers/add_review.html", order=order, buyer=buyer, existing_review=existing_review)
    rating = int(request.form.get("rating") or 0)
    comment = (request.form.get("comment") or "").strip()
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "danger")
        return redirect(url_for("farmer.orders"))
    Review.create({
        "orderId": ObjectId(order_id),
        "reviewerId": ObjectId(session["user_id"]),
        "revieweeId": order["buyerId"],
        "rating": rating,
        "comment": comment,
    })
    Buyer.add_rating(str(order["buyerId"]), rating)
    Order.update(order_id, {"reviewed": True})
    flash("Review submitted. Thank you!", "success")
    return redirect(url_for("farmer.orders"))
