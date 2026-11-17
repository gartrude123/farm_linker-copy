"""MongoDB collection models using PyMongo"""

from services.db import get_db
from bson import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


def _oid(value):
    try:
        return ObjectId(str(value))
    except Exception:
        return None


__all__ = ["_oid", "Farmer", "Buyer", "Admin", "Listing", "Order", "Review"]


# =====================================================================
# FARMERS
# =====================================================================
class Farmer:
    collection = None

    @classmethod
    def _col(cls):
        if cls.collection is None:
            db = get_db()
            if db is None:
                return None
            cls.collection = db.farmers
        return cls.collection

    @classmethod
    def create(cls, data):
        if cls._col() is None:
            return None
        data.setdefault("createdAt", datetime.utcnow())
        data.setdefault("isVerified", False)
        data.setdefault("accountStatus", "active")
        data.setdefault("rating", 0)
        data.setdefault("reviewsCount", 0)
        result = cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, fid):
        if cls._col() is None:
            return None
        return cls._col().find_one({"_id": _oid(fid)})

    @classmethod
    def find_by_email(cls, email):
        if cls._col() is None:
            return None
        return cls._col().find_one({"email": email})

    @classmethod
    def find_all(cls):
        if cls._col() is None:
            return []
        return list(cls._col().find())

    @classmethod
    def search(cls, query):
        if cls._col() is None:
            return []
        return list(cls._col().find({
            "$or": [
                {"fullName": {"$regex": query, "$options": "i"}},
                {"district": {"$regex": query, "$options": "i"}},
                {"village": {"$regex": query, "$options": "i"}},
            ]
        }))

    @classmethod
    def update(cls, fid, data):
        if cls._col() is None:
            return None
        return cls._col().update_one({"_id": _oid(fid)}, {"$set": data})

    @classmethod
    def delete(cls, fid):
        if cls._col() is None:
            return None
        return cls._col().delete_one({"_id": _oid(fid)})

    @classmethod
    def verify(cls, fid, verified=True):
        if cls._col() is None:
            return None
        return cls._col().update_one({"_id": _oid(fid)}, {"$set": {"isVerified": verified}})

    @classmethod
    def add_rating(cls, fid, rating):
        if cls._col() is None:
            return
        farmer = cls.find_by_id(fid)
        if not farmer:
            return
        current_rating = farmer.get("rating", 0)
        count = farmer.get("reviewsCount", 0)
        new_count = count + 1
        new_rating = ((current_rating * count) + rating) / new_count if new_count > 0 else rating
        cls._col().update_one(
            {"_id": _oid(fid)},
            {"$set": {"rating": round(new_rating, 2), "reviewsCount": new_count}},
        )

    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password)

    @classmethod
    def check_password(cls, stored_hash, password):
        return check_password_hash(stored_hash, password)


# =====================================================================
# BUYERS
# =====================================================================
class Buyer:
    collection = None

    @classmethod
    def _col(cls):
        if cls.collection is None:
            db = get_db()
            if db is None:
                return None
            cls.collection = db.buyers
        return cls.collection

    @classmethod
    def create(cls, data):
        if cls._col() is None:
            return None
        data["createdAt"] = datetime.utcnow()
        data["accountStatus"] = "active"
        data["rating"] = 0
        data["reviewsCount"] = 0
        result = cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, bid):
        if cls._col() is None:
            return None
        return cls._col().find_one({"_id": _oid(bid)})

    @classmethod
    def find_by_email(cls, email):
        if cls._col() is None:
            return None
        return cls._col().find_one({"email": email})

    @classmethod
    def find_all(cls):
        if cls._col() is None:
            return []
        return list(cls._col().find())

    @classmethod
    def search(cls, query):
        if cls._col() is None:
            return []
        return list(cls._col().find({
            "$or": [
                {"businessName": {"$regex": query, "$options": "i"}},
                {"contactPerson": {"$regex": query, "$options": "i"}},
                {"buyerType": {"$regex": query, "$options": "i"}},
            ]
        }))

    @classmethod
    def update(cls, bid, data):
        if cls._col() is None:
            return None
        return cls._col().update_one({"_id": _oid(bid)}, {"$set": data})

    @classmethod
    def delete(cls, bid):
        if cls._col() is None:
            return None
        return cls._col().delete_one({"_id": _oid(bid)})

    @classmethod
    def add_rating(cls, bid, rating):
        if cls._col() is None:
            return
        buyer = cls.find_by_id(bid)
        if not buyer:
            return
        current_rating = buyer.get("rating", 0)
        count = buyer.get("reviewsCount", 0)
        new_count = count + 1
        new_rating = ((current_rating * count) + rating) / new_count if new_count > 0 else rating
        cls._col().update_one(
            {"_id": _oid(bid)},
            {"$set": {"rating": round(new_rating, 2), "reviewsCount": new_count}},
        )

    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password)

    @classmethod
    def check_password(cls, stored_hash, password):
        return check_password_hash(stored_hash, password)


# =====================================================================
# ADMINS (separate collection for system administrators)
# =====================================================================
class Admin:
    collection = None

    @classmethod
    def _col(cls):
        if cls.collection is None:
            db = get_db()
            if db is None:
                return None
            cls.collection = db.admins
        return cls.collection

    @classmethod
    def create(cls, data):
        if cls._col() is None:
            return None
        data.setdefault("createdAt", datetime.utcnow())
        data.setdefault("accountStatus", "active")
        data.setdefault("isVerified", True)
        result = cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, aid):
        if cls._col() is None:
            return None
        return cls._col().find_one({"_id": _oid(aid)})

    @classmethod
    def find_by_email(cls, email):
        if cls._col() is None:
            return None
        return cls._col().find_one({"email": email})

    @classmethod
    def find_all(cls):
        if cls._col() is None:
            return []
        return list(cls._col().find())

    @classmethod
    def update(cls, aid, data):
        if cls._col() is None:
            return None
        return cls._col().update_one({"_id": _oid(aid)}, {"$set": data})

    @classmethod
    def delete(cls, aid):
        if cls._col() is None:
            return None
        return cls._col().delete_one({"_id": _oid(aid)})

    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password)

    @classmethod
    def check_password(cls, stored_hash, password):
        return check_password_hash(stored_hash, password)


# =====================================================================
# PRODUCE LISTINGS
# =====================================================================
class Listing:
    collection = None

    @classmethod
    def _col(cls):
        if cls.collection is None:
            db = get_db()
            if db is None:
                return None
            cls.collection = db.produceListings
        return cls.collection

    @classmethod
    def create(cls, data):
        if cls._col() is None:
            return None
        data["createdAt"] = datetime.utcnow()
        result = cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, lid):
        if cls._col() is None:
            return None
        return cls._col().find_one({"_id": _oid(lid)})

    @classmethod
    def find_by_farmer(cls, fid):
        if cls._col() is None:
            return []
        return list(cls._col().find({"farmerId": _oid(fid)}))

    @classmethod
    def find_all(cls):
        if cls._col() is None:
            return []
        return list(cls._col().find())

    @classmethod
    def search(cls, query):
        if cls._col() is None:
            return []
        return list(cls._col().find({
            "$or": [
                {"cropName": {"$regex": query, "$options": "i"}},
                {"category": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
            ]
        }))

    @classmethod
    def filter(cls, crop=None, district=None, min_price=None, max_price=None):
        if cls._col() is None:
            return []
        filter_query = {}
        if crop:
            filter_query["cropName"] = {"$regex": crop, "$options": "i"}
        if district:
            filter_query["district"] = {"$regex": district, "$options": "i"}
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = float(min_price)
            if max_price is not None:
                price_filter["$lte"] = float(max_price)
            filter_query["pricePerUnit"] = price_filter
        return list(cls._col().find(filter_query))

    @classmethod
    def update(cls, lid, data):
        if cls._col() is None:
            return None
        return cls._col().update_one({"_id": _oid(lid)}, {"$set": data})

    @classmethod
    def delete(cls, lid):
        if cls._col() is None:
            return None
        return cls._col().delete_one({"_id": _oid(lid)})


# =====================================================================
# ORDERS
# =====================================================================
class Order:
    collection = None

    @classmethod
    def _col(cls):
        if cls.collection is None:
            db = get_db()
            if db is None:
                return None
            cls.collection = db.orders
        return cls.collection

    @classmethod
    def create(cls, data):
        if cls._col() is None:
            return None
        data["createdAt"] = datetime.utcnow()
        data["orderStatus"] = data.get("orderStatus", "Pending")
        data["paymentStatus"] = data.get("paymentStatus", "Unpaid")
        data["deliveryNotified"] = False
        data["deliveryConfirmed"] = False
        result = cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    def find_by_id(cls, oid):
        if cls._col() is None:
            return None
        return cls._col().find_one({"_id": _oid(oid)})

    @classmethod
    def find_by_farmer(cls, fid):
        if cls._col() is None:
            return []
        return list(cls._col().find({"farmerId": _oid(fid)}))

    @classmethod
    def find_by_buyer(cls, bid):
        if cls._col() is None:
            return []
        return list(cls._col().find({"buyerId": _oid(bid)}))

    @classmethod
    def find_active(cls):
        """Orders that are not completed - for active views."""
        if cls._col() is None:
            return []
        return list(cls._col().find({
            "orderStatus": {"$nin": ["Completed"]}
        }))

    @classmethod
    def find_completed(cls):
        if cls._col() is None:
            return []
        return list(cls._col().find({"orderStatus": "Completed"}))

    @classmethod
    def find_all(cls):
        if cls._col() is None:
            return []
        return list(cls._col().find())

    @classmethod
    def update(cls, oid, data):
        if cls._col() is None:
            return None
        return cls._col().update_one({"_id": _oid(oid)}, {"$set": data})

    @classmethod
    def delete(cls, oid):
        if cls._col() is None:
            return None
        return cls._col().delete_one({"_id": _oid(oid)})

    @classmethod
    def update_status(cls, oid, status):
        if cls._col() is None:
            return None
        return cls._col().update_one({"_id": _oid(oid)}, {"$set": {"orderStatus": status}})

    @classmethod
    def mark_delivery_notified(cls, oid, notes, place, time):
        if cls._col() is None:
            return None
        return cls._col().update_one(
            {"_id": _oid(oid)},
            {"$set": {
                "deliveryNotified": True,
                "deliveryNotes": notes,
                "deliveryPlace": place,
                "deliveryTime": time,
                "deliveryNotificationDate": datetime.utcnow(),
                "orderStatus": "In Transit",
            }},
        )

    @classmethod
    def mark_payment_paid(cls, oid, method=None, date=None):
        if cls._col() is None:
            return None
        update = {"paymentStatus": "Paid"}
        if method:
            update["paymentMethod"] = method
        if date:
            update["paymentDate"] = date
        return cls._col().update_one({"_id": _oid(oid)}, {"$set": update})

    @classmethod
    def mark_completed(cls, oid):
        if cls._col() is None:
            return None
        return cls._col().update_one(
            {"_id": _oid(oid)},
            {"$set": {
                "orderStatus": "Completed",
            }},
        )


# =====================================================================
# REVIEWS
# =====================================================================
class Review:
    collection = None

    @classmethod
    def _col(cls):
        if cls.collection is None:
            db = get_db()
            if db is None:
                return None
            cls.collection = db.reviews
        return cls.collection

    @classmethod
    def create(cls, data):
        if cls._col() is None:
            return None
        data["reviewDate"] = datetime.utcnow()
        result = cls._col().insert_one(data)
        return str(result.inserted_id)

    @classmethod
    def find_by_order(cls, order_id):
        if cls._col() is None:
            return []
        return list(cls._col().find({"orderId": _oid(order_id)}))

    @classmethod
    def find_by_reviewer(cls, reviewer_id):
        if cls._col() is None:
            return []
        return list(cls._col().find({"reviewerId": _oid(reviewer_id)}))

    @classmethod
    def find_by_reviewee(cls, reviewee_id):
        if cls._col() is None:
            return []
        return list(cls._col().find({"revieweeId": _oid(reviewee_id)}))

    @classmethod
    def find_all(cls):
        if cls._col() is None:
            return []
        return list(cls._col().find())

    @classmethod
    def delete(cls, rid):
        if cls._col() is None:
            return None
        return cls._col().delete_one({"_id": _oid(rid)})
