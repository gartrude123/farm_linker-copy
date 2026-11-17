"""Admin routes"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Farmer, Buyer, Listing, Order, Review, Admin, _oid
from services.db import get_db
from datetime import datetime
from routes.auth import login_required, admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    db = get_db()
    pending_replacement = db.admin_replacements.find_one({"status": "pending"}) if db is not None else None
    existing_admin = Admin.find_all()
    stats = {
        "farmers": Farmer.find_all().__len__(),
        "buyers": Buyer.find_all().__len__(),
        "listings": Listing.find_all().__len__(),
        "orders": Order.find_all().__len__(),
        "pending_orders": len([o for o in Order.find_all() if o.get("orderStatus") == "Pending"]),
        "completed_orders": len([o for o in Order.find_all() if o.get("orderStatus") == "Completed"]),
        "reviews": Review.find_all().__len__(),
    }
    return render_template("admin/dashboard.html", stats=stats, pending_replacement=pending_replacement)


@admin_bp.route("/admin-replacement/approve")
@login_required
@admin_required
def approve_admin_replacement():
    db = get_db()
    pending = db.admin_replacements.find_one({"status": "pending"})
    if not pending:
        flash("No pending admin replacement request.", "info")
        return redirect(url_for("admin.dashboard"))

    # Remove existing admin
    existing_admins = Admin.find_all()
    for ea in existing_admins:
        Admin.delete(ea["_id"])

    # Create new admin from pending data
    new_admin = {
        "email": pending["email"],
        "password": pending["password_hash"],
        "fullName": pending["fullName"],
        "phone": pending.get("phone", ""),
        "district": pending.get("district", ""),
        "village": pending.get("village", ""),
        "location": {"type": "Point", "coordinates": [0.0, 0.0]},
        "accountStatus": "active",
        "isVerified": True,
    }
    Admin.create(new_admin)

    # Mark replacement as approved
    db.admin_replacements.update_one(
        {"_id": pending["_id"]},
        {"$set": {"status": "approved", "approved_at": datetime.utcnow()}},
    )

    flash("Admin replacement approved. The new administrator account is now active.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin-replacement/deny")
@login_required
@admin_required
def deny_admin_replacement():
    db = get_db()
    pending = db.admin_replacements.find_one({"status": "pending"})
    if not pending:
        flash("No pending admin replacement request.", "info")
        return redirect(url_for("admin.dashboard"))

    db.admin_replacements.update_one(
        {"_id": pending["_id"]},
        {"$set": {"status": "denied", "denied_at": datetime.utcnow()}},
    )

    flash("Admin replacement request denied.", "info")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/farmers")
@login_required
@admin_required
def farmers():
    farmers = Farmer.find_all()
    return render_template("admin/farmers.html", farmers=farmers)


@admin_bp.route("/setup", methods=["GET", "POST"])
def setup():
    """Create the first admin account if none exists."""
    from models import Farmer, Buyer
    from werkzeug.security import generate_password_hash

    db = get_db()
    if db is None:
        flash("Database unavailable.", "danger")
        return render_template("admin/setup.html")

    existing_admin = Admin.find_all()
    if existing_admin:
        flash("Admin account already exists.", "info")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        full_name = (request.form.get("full_name") or "Administrator").strip()

        if not email or "@" not in email:
            flash("Valid email is required.", "danger")
            return render_template("admin/setup.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("admin/setup.html")

        admin_data = {
            "email": email,
            "password": Admin.hash_password(password),
            "fullName": full_name,
            "phone": "",
            "district": "",
            "village": "",
            "location": {"type": "Point", "coordinates": [0.0, 0.0]},
            "accountStatus": "active",
            "isVerified": True,
        }
        result = Admin.create(admin_data)
        if result:
            flash("Admin account created successfully. Please log in.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash("Failed to create admin account.", "danger")

    return render_template("admin/setup.html")


@admin_bp.route("/farmers/verify/<id>")
@login_required
@admin_required
def verify_farmer(id):
    verified = request.args.get("verified", "true").lower() == "true"
    Farmer.verify(id, verified)
    flash(f"Farmer verification {'granted' if verified else 'revoked'}.", "success")
    return redirect(url_for("admin.farmers"))


@admin_bp.route("/farmers/status/<id>/<status>")
@login_required
@admin_required
def farmer_status(id, status):
    if status not in ("active", "suspended", "blocked"):
        flash("Invalid account status.", "danger")
        return redirect(url_for("admin.farmers"))
    Farmer._col().update_one({"_id": _oid(id)}, {"$set": {"accountStatus": status}})
    flash(f"Farmer account {status}.", "success")
    return redirect(url_for("admin.farmers"))


@admin_bp.route("/buyers/status/<id>/<status>")
@login_required
@admin_required
def buyer_status(id, status):
    if status not in ("active", "suspended", "blocked"):
        flash("Invalid account status.", "danger")
        return redirect(url_for("admin.buyers"))
    Buyer._col().update_one({"_id": _oid(id)}, {"$set": {"accountStatus": status}})
    flash(f"Buyer account {status}.", "success")
    return redirect(url_for("admin.buyers"))


@admin_bp.route("/buyers")
@login_required
@admin_required
def buyers():
    buyers = Buyer.find_all()
    return render_template("admin/buyers.html", buyers=buyers)


@admin_bp.route("/listings")
@login_required
@admin_required
def listings():
    listings = Listing.find_all()
    return render_template("admin/listings.html", listings=listings)


@admin_bp.route("/orders")
@login_required
@admin_required
def orders():
    orders = Order.find_all()
    return render_template("admin/orders.html", orders=orders)


@admin_bp.route("/reviews")
@login_required
@admin_required
def reviews():
    reviews = Review.find_all()
    return render_template("admin/reviews.html", reviews=reviews)
