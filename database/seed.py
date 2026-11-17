"""Seed sample data into MongoDB Atlas for testing.

Idempotent by default: existing users are reused (matched by email), and
listings/orders/reviews are created only when matching sample records are
missing. Use --reset to clear seeded collections first.
"""

import argparse
from datetime import datetime

from bson import ObjectId

from models import Buyer, Farmer, Listing, Order, Review
from services.db import get_db


def _require_db():
    db = get_db()
    if db is None:
        raise SystemExit("Database unavailable. Check MONGO_URI in your .env file.")
    return db


def _upsert_user(model, collection, email, data):
    existing = collection.find_one({"email": email})
    if existing:
        collection.update_one({"_id": existing["_id"]}, {"$set": data})
        return str(existing["_id"])
    result = collection.insert_one(data)
    return str(result.inserted_id)


def _ensure_listing(farmer_id, crop_name, data):
    existing = Listing._col().find_one(
        {"farmerId": ObjectId(farmer_id), "cropName": crop_name}
    )
    if existing:
        Listing._col().update_one({"_id": existing["_id"]}, {"$set": data})
        return str(existing["_id"])
    return Listing.create(data)


def _ensure_order(farmer_id, buyer_id, listing_id, data):
    existing = Order._col().find_one(
        {
            "farmerId": ObjectId(farmer_id),
            "buyerId": ObjectId(buyer_id),
            "listingId": ObjectId(listing_id),
        }
    )
    if existing:
        Order._col().update_one({"_id": existing["_id"]}, {"$set": data})
        return str(existing["_id"])
    return Order.create(data)


def _ensure_review(order_id, reviewer_id, reviewee_id, data):
    existing = Review._col().find_one(
        {
            "orderId": ObjectId(order_id),
            "reviewerId": ObjectId(reviewer_id),
            "revieweeId": ObjectId(reviewee_id),
        }
    )
    if existing:
        Review._col().update_one({"_id": existing["_id"]}, {"$set": data})
        return str(existing["_id"])
    return Review.create(data)


def seed(reset=False):
    db = _require_db()

    if reset:
        db.farmers.delete_many({})
        db.buyers.delete_many({})
        db.produceListings.delete_many({})
        db.orders.delete_many({})
        db.reviews.delete_many({})
        for model in (Farmer, Buyer, Listing, Order, Review):
            model.collection = None

    now = datetime.utcnow()

    farmers = [
        {
            "email": "farmer1@example.com",
            "password": Farmer.hash_password("password123"),
            "fullName": "John Kato",
            "phone": "+256700123456",
            "district": "Mukono",
            "village": "Nakifuma",
            "farmSizeAcres": 5,
            "mainCrops": ["Maize", "Beans"],
            "location": {"type": "Point", "coordinates": [32.7, 0.4]},
            "isVerified": True,
            "rating": 4.5,
            "reviewsCount": 10,
            "createdAt": now,
        },
        {
            "email": "farmer2@example.com",
            "password": Farmer.hash_password("password123"),
            "fullName": "Mary Namuddu",
            "phone": "+256700234567",
            "district": "Wakiso",
            "village": "Kira",
            "farmSizeAcres": 3,
            "mainCrops": ["Tomatoes", "Cabbage"],
            "location": {"type": "Point", "coordinates": [32.5, 0.3]},
            "isVerified": True,
            "rating": 4.8,
            "reviewsCount": 15,
            "createdAt": now,
        },
    ]

    buyers = [
        {
            "email": "buyer1@example.com",
            "password": Buyer.hash_password("password123"),
            "businessName": "Kampala Fresh Market",
            "contactPerson": "Robert Ssekyanzi",
            "phone": "+256700345678",
            "buyerType": "Market Vendor",
            "preferredProduce": ["Maize", "Tomatoes"],
            "location": {"type": "Point", "coordinates": [32.6, 0.3]},
            "rating": 4.2,
            "reviewsCount": 8,
            "createdAt": now,
        },
        {
            "email": "buyer2@example.com",
            "password": Buyer.hash_password("password123"),
            "businessName": "City Restaurant Ltd",
            "contactPerson": "Sarah Nalwanga",
            "phone": "+256700456789",
            "buyerType": "Restaurant",
            "preferredProduce": ["Cabbage", "Carrots"],
            "location": {"type": "Point", "coordinates": [32.55, 0.32]},
            "rating": 4.0,
            "reviewsCount": 5,
            "createdAt": now,
        },
    ]

    f_ids = [_upsert_user(Farmer, db.farmers, f["email"], f) for f in farmers]
    b_ids = [_upsert_user(Buyer, db.buyers, b["email"], b) for b in buyers]

    listings = [
        {
            "farmerId": ObjectId(f_ids[0]),
            "cropName": "Maize",
            "category": "Grains",
            "quantity": 1000,
            "unit": "kg",
            "pricePerUnit": 1500,
            "harvestDate": "2026-11-01",
            "expiryDate": "2027-05-01",
            "description": "Fresh dry maize from Mukono district",
            "images": [],
            "createdAt": now,
        },
        {
            "farmerId": ObjectId(f_ids[1]),
            "cropName": "Tomatoes",
            "category": "Vegetables",
            "quantity": 500,
            "unit": "kg",
            "pricePerUnit": 2500,
            "harvestDate": "2026-10-28",
            "expiryDate": "2026-11-05",
            "description": "Fresh organic tomatoes",
            "images": [],
            "createdAt": now,
        },
    ]
    l_ids = [
        _ensure_listing(f_ids[0], "Maize", listings[0]),
        _ensure_listing(f_ids[1], "Tomatoes", listings[1]),
    ]

    orders = [
        {
            "listingId": ObjectId(l_ids[0]),
            "farmerId": ObjectId(f_ids[0]),
            "buyerId": ObjectId(b_ids[0]),
            "quantityOrdered": 200,
            "totalPrice": 300000,
            "unitPriceSnapshot": 1500,
            "cropNameSnapshot": "Maize",
            "orderStatus": "Pending",
            "paymentStatus": "Unpaid",
            "paymentMethod": "Cash on delivery",
            "deliveryMethod": "Pickup",
            "deliveryNotified": False,
            "deliveryConfirmed": False,
            "createdAt": now,
        },
        {
            "listingId": ObjectId(l_ids[1]),
            "farmerId": ObjectId(f_ids[1]),
            "buyerId": ObjectId(b_ids[1]),
            "quantityOrdered": 50,
            "totalPrice": 125000,
            "unitPriceSnapshot": 2500,
            "cropNameSnapshot": "Tomatoes",
            "orderStatus": "Completed",
            "paymentStatus": "Paid",
            "paymentMethod": "Mobile money",
            "deliveryMethod": "Delivery",
            "deliveryNotified": True,
            "deliveryConfirmed": True,
            "deliveryNotes": "Delivered at restaurant gate",
            "deliveryPlace": "City Restaurant Ltd",
            "deliveryTime": "2026-10-30 09:00",
            "deliveryNotificationDate": now,
            "createdAt": now,
        },
    ]
    o_ids = [
        _ensure_order(f_ids[0], b_ids[0], l_ids[0], orders[0]),
        _ensure_order(f_ids[1], b_ids[1], l_ids[1], orders[1]),
    ]

    review = {
        "orderId": ObjectId(o_ids[1]),
        "reviewerId": ObjectId(b_ids[1]),
        "revieweeId": ObjectId(f_ids[1]),
        "rating": 5,
        "comment": "Great quality tomatoes and timely delivery.",
        "reviewDate": now,
    }
    r_id = _ensure_review(o_ids[1], b_ids[1], f_ids[1], review)

    print("Seed complete." if not reset else "Seed reset complete.")
    print(f"Farmers: {', '.join(f_ids)}")
    print(f"Buyers: {', '.join(b_ids)}")
    print(f"Listings: {', '.join(l_ids)}")
    print(f"Orders: {', '.join(o_ids)}")
    print(f"Review: {r_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Farm_linker sample data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear seeded collections before inserting sample data.",
    )
    args = parser.parse_args()
    seed(reset=args.reset)
