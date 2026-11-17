# FARM_LINKER Platform

## Overview
FARM_LINKER is a social marketplace platform that connects smallholder farmers directly to buyers without middlemen.

## Technology Stack
- **Backend:** Python (Flask Framework)
- **Database:** MongoDB Atlas (PyMongo driver)
- **Frontend:** HTML5, CSS3, JavaScript (mobile-first, responsive)
- **Authentication:** Secure login/registration with password hashing and session management

## Project Structure
```
/farm_linker
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── orders.html
│   ├── farmers/
│   │   ├── dashboard.html
│   │   ├── listings.html
│   │   ├── add_listing.html
│   │   ├── edit_listing.html
│   │   ├── buyers.html
│   │   ├── orders.html
│   │   └── profile.html
│   ├── buyers/
│   │   ├── dashboard.html
│   │   ├── listings.html
│   │   ├── farmers.html
│   │   ├── create_order.html
│   │   ├── edit_order.html
│   │   ├── orders.html
│   │   └── profile.html
│   └── admin/
│       ├── dashboard.html
│       ├── farmers.html
│       ├── buyers.html
│       ├── listings.html
│       ├── orders.html
│       └── reviews.html
├── models/__init__.py
├── routes/
│   ├── auth.py
│   ├── farmer.py
│   ├── buyer.py
│   ├── admin.py
│   └── orders.py
├── services/db.py
└── README.md
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and update the MongoDB Atlas URI:
```
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/farm_linker?retryWrites=true&w=majority
SECRET_KEY=your-random-secret-key
```

### 3. Run the Application
```bash
python app.py
```

The app will run on `http://localhost:5000`.

## MongoDB Collections

### farmers
- _id, fullName, phone, password, email, district, village, farmSizeAcres, mainCrops, location, isVerified, profilePhoto, rating, reviewsCount, createdAt

### buyers
- _id, businessName, contactPerson, phone, password, email, buyerType, preferredProduce, location, rating, reviewsCount, createdAt

### produceListings
- _id, farmerId, cropName, category, quantity, unit, pricePerUnit, harvestDate, expiryDate, images, description, createdAt

### orders
- _id, listingId, farmerId, buyerId, quantityOrdered, totalPrice, unitPriceSnapshot, cropNameSnapshot, orderStatus, paymentStatus, paymentMethod, paymentDate, deliveryMethod, deliveryNotified, deliveryConfirmed, deliveryNotes, deliveryPlace, deliveryTime, createdAt

### reviews
- _id, orderId, reviewerId, revieweeId, rating, comment, reviewDate

## Order Workflow
1. Buyer views produce listing → fills order form → submits order (status: Pending)
2. Farmer receives order → approves or rejects (status: Approved/Rejected)
3. Buyer receives approval notification → can contact farmer by phone
4. Farmer notifies delivery with date, place, time (status: In Transit)
5. Buyer confirms delivery (status: Completed)
6. Completed orders no longer appear in active lists

## User Roles
- **Farmer:** Register, login, manage profile, add/edit/delete listings, view buyers, receive/approve/reject orders, contact buyers by phone, view order history, mark orders completed, receive ratings
- **Buyer:** Register, login, manage profile, browse/search/filter listings, create/edit/cancel orders, select preferred farmer, contact farmer by phone, confirm delivery, submit reviews, view order history
- **Admin:** Dashboard, view/manage farmers/buyers/listings/orders/reviews, verify farmers, reports

## Features
- Role-based authentication and authorization
- CSRF protection
- Flash messages
- Mobile-first responsive design
- Green agricultural theme
- Phone contact integration
- Rating and review system
- Order status workflow
- Search and filter functionality
- Admin verification of farmers
