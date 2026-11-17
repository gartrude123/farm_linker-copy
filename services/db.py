"""Database service - PyMongo connection to MongoDB (local via Compass)"""

from pymongo import MongoClient
from config import Config


_client = None
_db = None


def get_client():
    global _client
    if _client is None:
        try:
            _client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        except Exception as e:
            print(f"[DB] Failed to create MongoDB client: {e}")
            return None
    return _client


def get_db():
    global _db
    if _db is None:
        client = get_client()
        if client is None:
            return None
        try:
            _db = client[Config.DATABASE_NAME]
            _create_indexes(_db)
        except Exception as e:
            print(f"[DB] Failed to get database: {e}")
            return None
    return _db


def _create_indexes(db):
    """Create indexes for performance and uniqueness."""
    try:
        db.farmers.create_index("email", unique=True)
        db.buyers.create_index("email", unique=True)
        db.admins.create_index("email", unique=True)
        db.produceListings.create_index("farmerId")
        db.produceListings.create_index("cropName")
        db.produceListings.create_index("category")
        db.orders.create_index("farmerId")
        db.orders.create_index("buyerId")
        db.orders.create_index("listingId")
        db.orders.create_index("orderStatus")
        db.reviews.create_index("orderId")
        db.reviews.create_index("reviewerId")
        db.reviews.create_index("revieweeId")
    except Exception:
        pass  # Indexes may already exist


def close_db():
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
