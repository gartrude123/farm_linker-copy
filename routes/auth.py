"""Authentication routes"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Farmer, Buyer, Admin, _oid
from services.db import get_db
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        # Check account status on every request
        role = session.get("user_role", "buyer")
        db = get_db()
        if db is not None:
            if role == "admin":
                user = db.admins.find_one({"_id": _oid(session["user_id"])})
            elif role == "farmer":
                user = db.farmers.find_one({"_id": _oid(session["user_id"])})
            else:
                user = db.buyers.find_one({"_id": _oid(session["user_id"])})
            if user and user.get("accountStatus") != "active":
                status = user.get("accountStatus", "suspended")
                session.clear()
                flash(f"Your account has been {status}. Please contact the administrator for assistance.", "danger")
                return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(allowed_roles):
    from functools import wraps

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login", next=request.path))
            if session.get("user_role") not in allowed_roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("auth.dashboard"))
            return f(*args, **kwargs)
        return decorated
    return decorator


farmer_required = role_required(["farmer", "admin"])
buyer_required = role_required(["buyer", "admin"])
admin_required = role_required(["admin"])


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role", "buyer")
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        full_name = (request.form.get("full_name") or "").strip()
        phone = (request.form.get("phone") or "").strip()

        db = get_db()
        if db is None:
            flash("Database unavailable. Please configure MONGO_URI and restart the app.", "danger")
            return render_template("register.html")

        errors = []
        if not email or "@" not in email:
            errors.append("Valid email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if not full_name:
            errors.append("Full name is required.")
        if role not in ("buyer", "farmer", "admin"):
            role = "buyer"

        password_confirm = request.form.get("password_confirm") or ""
        if password != password_confirm:
            errors.append("Password and confirmation do not match.")

        if role == "farmer":
            district = (request.form.get("district") or "").strip()
            village = (request.form.get("village") or "").strip()
            farm_size = request.form.get("farmSizeAcres") or 0
            main_crops = request.form.getlist("mainCrops")
            if not district:
                errors.append("District is required for farmers.")
            if not village:
                errors.append("Village is required for farmers.")
            if len(main_crops) < 2:
                errors.append("Please select at least two main crops.")
            if Farmer.find_by_email(email):
                errors.append("Email already registered as a farmer.")
        elif role == "admin":
            # Single admin enforcement
            existing_admins = Admin.find_all()
            if existing_admins:
                # Store pending replacement request
                db.admin_replacements.update_one(
                    {},
                    {"$set": {
                        "email": email,
                        "fullName": full_name,
                        "phone": phone,
                        "password_hash": Admin.hash_password(password),
                        "requested_at": datetime.utcnow(),
                        "status": "pending",
                    }},
                    upsert=True,
                )
                errors.append(
                    "An administrator account already exists. "
                    "The current admin has been notified and must approve or deny your request."
                )
            else:
                district = (request.form.get("district") or "").strip()
                village = (request.form.get("village") or "").strip()
                if not district:
                    errors.append("District is required.")
                if not village:
                    errors.append("Village is required.")
            if Admin.find_by_email(email):
                errors.append("Email already registered as an admin.")
        else:
            business_name = (request.form.get("businessName") or "").strip()
            contact_person = (request.form.get("contactPerson") or "").strip()
            buyer_type = request.form.get("buyerType", "Market Vendor")
            preferred_produce = request.form.getlist("preferredProduce")
            if not business_name:
                errors.append("Business name is required for buyers.")
            if Buyer.find_by_email(email):
                errors.append("Email already registered as a buyer.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html")

        if role == "farmer":
            user_id = Farmer.create({
                "email": email,
                "password": Farmer.hash_password(password),
                "fullName": full_name,
                "phone": phone,
                "district": district,
                "village": village,
                "farmSizeAcres": int(farm_size) if farm_size else 0,
                "mainCrops": main_crops,
                "location": {"type": "Point", "coordinates": [0.0, 0.0]},
                "isVerified": False,
                "accountStatus": "active",
                "rating": 0,
                "reviewsCount": 0,
            })
        elif role == "admin":
            user_id = Admin.create({
                "email": email,
                "password": Admin.hash_password(password),
                "fullName": full_name,
                "phone": phone,
                "district": district,
                "village": village,
                "location": {"type": "Point", "coordinates": [0.0, 0.0]},
                "accountStatus": "active",
            })
        else:
            user_id = Buyer.create({
                "email": email,
                "password": Buyer.hash_password(password),
                "businessName": business_name,
                "contactPerson": contact_person,
                "phone": phone,
                "buyerType": buyer_type,
                "preferredProduce": preferred_produce,
                "location": {"type": "Point", "coordinates": [0.0, 0.0]},
                "accountStatus": "active",
                "rating": 0,
                "reviewsCount": 0,
            })

        if not user_id:
            flash("Could not create account: database unavailable.", "danger")
            return render_template("register.html")

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        role = request.form.get("role", "buyer")

        db = get_db()
        if db is None:
            flash("Database unavailable. Please set a real MONGO_URI in .env and restart the app.", "danger")
            return render_template("login.html")

        user = None
        user_role = None
        user_type = None
        check_pw = None

        if role == "farmer":
            user = Farmer.find_by_email(email)
            if user:
                user_role = "farmer"
                user_type = "farmer"
                check_pw = Farmer.check_password(user["password"], password)
        elif role == "admin":
            user = Admin.find_by_email(email)
            if user:
                user_role = "admin"
                user_type = "admin"
                check_pw = Admin.check_password(user["password"], password)
        if not user:
            user = Buyer.find_by_email(email)
            if user:
                user_role = "buyer"
                user_type = "buyer"
                check_pw = Buyer.check_password(user["password"], password)

        if not user:
            flash("Invalid email or account type.", "danger")
            return render_template("login.html")

        if not check_pw:
            flash("Invalid password.", "danger")
            return render_template("login.html")

        account_status = user.get("accountStatus", "active")
        if account_status != "active":
            if account_status == "suspended":
                flash("Your account has been suspended. Please contact the administrator for assistance.", "danger")
            elif account_status == "blocked":
                flash("Your account has been blocked. Please contact the administrator for assistance.", "danger")
            else:
                flash(f"Your account is {account_status}. Please contact the administrator.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = str(user["_id"])
        session["user_role"] = user_role
        session["user_type"] = user_type
        session["user_name"] = user.get("fullName") or user.get("businessName") or email
        flash(f"Welcome back, {session['user_name']}.", "success")

        next_url = request.args.get("next")
        if next_url:
            return redirect(next_url)
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    role = session.get("user_role", "buyer")
    if role == "farmer":
        return redirect(url_for("farmer.dashboard"))
    return redirect(url_for("buyer.dashboard"))


@auth_bp.route("/profile")
@login_required
def profile():
    user_id = session["user_id"]
    role = session.get("user_role", "buyer")
    if role == "farmer":
        user = Farmer.find_by_id(user_id)
        template = "farmers/profile.html"
    elif role == "admin":
        user = Admin.find_by_id(user_id)
        template = "admin/profile.html"
    else:
        user = Buyer.find_by_id(user_id)
        template = "buyers/profile.html"
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.logout"))
    return render_template(template, user=user, role=role)
