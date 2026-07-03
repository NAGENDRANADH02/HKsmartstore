🛍️ HK SmartStore

A scalable full-stack e-commerce platform built using React.js, Django, MySQL, Redis, HTML, CSS, and Bootstrap.

🌟 Overview

HK SmartStore is a production-ready full-stack e-commerce platform built from scratch using React.js for the frontend and Django for the backend. The platform provides a seamless shopping experience with dedicated dashboards for Customers, Vendors, and Administrators, along with Prime Membership, Referral Wallet System, Email Verification, and scalable backend optimizations.

The backend is designed with scalability in mind by incorporating Redis-based caching, modular architecture, optimized database access, and production-ready deployment practices.

🌐 Live Demo

https://nagendranadhh.pythonanywhere.com

🧠 Table of Contents
Overview
Tech Stack
Key Features
System Architecture
Module-wise Explanation
Prime Membership
Referral & Wallet System
Performance Optimizations
Setup Instructions
Database Design
Future Enhancements
Screenshots
Contact
⚙️ Tech Stack
Layer	Technology
Frontend	React.js, HTML5, CSS3, Bootstrap 5, JavaScript
Backend	Django 4.2, Python 3.11
Database	MySQL
Cache	Redis
Authentication	Django Authentication + Custom Multi-User Authentication
Email Service	Gmail SMTP
Deployment	PythonAnywhere
Version Control	Git & GitHub
🚀 Key Features
✅ Multi-Role Authentication
Separate login systems for Customers, Vendors, and Admin
Email verification using secure token links
OTP-based authentication
Role-based authorization
✅ React Frontend
Modern React.js frontend
Component-based architecture
Responsive UI
REST API integration with Django backend
Dynamic product rendering
Optimized client-side navigation
✅ Customer Portal
Product browsing and search
Category filters
Wishlist
Shopping cart
Address management
Order placement
Wallet integration
Order history
✅ Vendor Dashboard
Product management
Inventory management
Product image uploads
Order management
Earnings dashboard
Automatic product slug generation
✅ Admin Dashboard
Vendor approval
User management
Product moderation
Category management
Order management
Dashboard analytics
✅ Prime Membership System

Customers can subscribe to Prime Membership and enjoy premium benefits.

✅ Referral Wallet System
Referral codes
Wallet balance
Multi-level referral rewards
Wallet transaction history
✅ Notifications
Email verification
OTP emails
Order updates
Registration confirmation
✅ Responsive Design
Mobile-first layout
Bootstrap responsive components
Flipkart-inspired design
⚡ System Design & Performance Optimizations

The application includes backend optimizations inspired by real-world e-commerce systems.

🔹 Redis Cache-Aside Strategy

Implemented Redis caching for frequently accessed product data.

Cache Flow
Client

↓

React Frontend

↓

Django API

↓

Redis Cache

↓

MySQL Database
Implementation
Cache product detail pages
Cache related products
TTL-based cache expiration
Automatic database fallback on cache miss
Graceful degradation when Redis is unavailable
🔹 Scalability Decisions

Cached:

Product details
Categories
Related products
Homepage data

Not Cached:

Cart
Orders
Wallet
Authentication
Payments

Reason:

Maintain strong consistency for user-specific data
Reduce stale data issues
🧩 System Architecture
                React Frontend
                      │
                      │ REST APIs
                      ▼
                Django Backend
                      │
      ┌───────────────┼───────────────┐
      │               │               │
 Accounts        Products        Orders
      │               │               │
 Dashboard        Core         Notifications
                      │
             Redis Cache Layer
                      │
                  MySQL Database

The application follows a modular monolithic architecture with clean separation of business domains while leveraging Redis as a caching layer for improved read performance.

🧱 Module-wise Explanation
🔹 Accounts Module

Responsible for:

Authentication
Authorization
Email verification
OTP login
Referral management
Wallet system
Models
Customer
Vendor
UserProfile
WalletTransaction
Highlights
Referral code generation
Email verification
Wallet tracking
🔹 Products Module

Responsible for product management.

Models
Product
Category
Banner
ProductImage
Features
Vendor product uploads
Product categories
Search
Filtering
Redis caching for product details
🔹 Orders Module

Handles complete order lifecycle.

Features
Shopping cart
Wishlist
Checkout
Address management
Order tracking
Payment workflow
🔹 Dashboard Module

Separate dashboards for:

Admin
User management
Vendor approval
Analytics
Product moderation
Vendor
Inventory
Orders
Earnings
Products
🔹 Core Module

Contains

Homepage
Banner management
Prime subscription
Notifications
💎 Prime Membership

Prime Membership rewards loyal customers with premium benefits.

Features
PrimeSubscription model
Automatic expiry
Membership activation
Renewal support

Benefits include

Exclusive discounts
Priority notifications
Special coupons
🔗 Referral Wallet System

A multi-level referral reward system.

Example
A
│
B
│
C

When C joins using B's referral

B receives ₹20
A receives ₹10
Implementation
Unique referral codes
Recursive referral chain
WalletTransaction history
Wallet payments for purchases and Prime renewals
⚡ Backend Optimizations

Implemented several production-oriented optimizations:

Redis Cache-Aside Pattern
Database fallback strategy
Optimized ORM queries using select_related() and prefetch_related()
Lazy loading where applicable
Slug generation
Modular app structure
Static & media file separation
Production-ready settings configuration
⚙️ Setup Instructions
Clone Repository
git clone https://github.com/yourusername/hksmartstore.git

cd hksmartstore
Create Virtual Environment

Windows

python -m venv venv

venv\Scripts\activate

Linux / macOS

python -m venv venv

source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Configure Database

Update the DATABASES section inside

settings.py

with your MySQL credentials.

Apply Migrations
python manage.py makemigrations

python manage.py migrate
Create Admin User
python manage.py createsuperuser
Run Backend
python manage.py runserver
Run React Frontend
npm install

npm run dev

Visit

Backend:
http://127.0.0.1:8000

Frontend:
http://localhost:5173
🗄 Database Design
Table	Description
Customer	Customer details
Vendor	Vendor information
UserProfile	Referral & wallet
WalletTransaction	Wallet ledger
Product	Product catalog
ProductImage	Product images
Category	Product categories
Order	Customer orders
PrimeSubscription	Prime membership
Notification	Notifications
🚀 Performance Highlights
Redis-powered caching for frequently accessed product data
Cache-Aside strategy with graceful database fallback
Optimized database queries using Django ORM
Modular architecture for easier maintenance and scalability
Responsive React frontend consuming Django REST APIs
Production deployment on PythonAnywhere
Secure authentication with email verification and OTP support
