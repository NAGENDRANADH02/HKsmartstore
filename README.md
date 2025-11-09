# 🛍️ HK SmartStore
> **A full-stack e-commerce web application built using Django, MySQL, HTML, CSS, and Bootstrap.**

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/0ed8c2d6-4b6b-4e9c-b09a-8b6b28dd8504" />


---

## 🌟 Overview

**HK SmartStore** is a modern, full-featured e-commerce platform — built entirely from scratch using **Python (Django)** and **MySQL**.

It provides a seamless shopping experience with **separate dashboards for Admin, Vendor, and Customer**, an integrated **referral wallet system**, **email verification**, and a **Prime subscription module** — all deployed live on **PythonAnywhere**.

🌐 **Live Demo:** [https://nagendranadhh.pythonanywhere.com](https://nagendranadhh.pythonanywhere.com)

---

## 🧠 Table of Contents
- [Tech Stack](#-tech-stack)
- [Key Features](#-key-features)
- [Architecture Overview](#-architecture-overview)
- [Module-wise Explanation](#-module-wise-explanation)
- [Setup Instructions](#-setup-instructions)
- [Database Structure](#-database-structure)
- [Future Improvements](#-future-improvements)
- [Screenshots](#-screenshots)
- [Contact](#-contact)

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Django 4.2, Python 3.11 |
| **Database** | MySQL |
| **Frontend** | HTML, CSS, Bootstrap 5 |
| **Authentication** | Django Auth + Custom MultiUser Backend |
| **Email Services** | Gmail SMTP |
| **Deployment** | PythonAnywhere |

---

## 🚀 Key Features

✅ **Multi-Role Authentication**  
- Separate login systems for **Customers**, **Vendors**, and **Admins**  
- Token-based **email verification** and **OTP-based login**

✅ **Customer Portal**  
- Browse, search, wishlist, and order products  
- Manage cart, addresses, and payment modes  
- Referral wallet integration  

✅ **Vendor Dashboard**  
- Add, edit, and delete products  
- Manage orders and earnings  
- Auto-generate product slugs and upload images  

✅ **Admin Panel**  
- Approve vendors, manage users, orders, products, and categories  
- Dashboard analytics view  

✅ **Prime Subscription System**  
- Customers can subscribe for exclusive discounts and benefits  

✅ **Referral & Wallet System**  
- Earn wallet balance when users register using referral code  

✅ **Notifications & Email Integration**  
- Email alerts for verification, OTP, and updates  

✅ **Responsive UI**  
- Flipkart-inspired layout with custom CSS and mobile-optimized design  

---

## 🧩 Architecture Overview
hksmartstore/
├── accounts/ → Handles authentication, referrals, and wallet logic
├── products/ → Product, category, banner, and wishlist management
├── orders/ → Cart, checkout, order tracking, and payments
├── dashboard/ → Vendor and admin dashboards
├── core/ → Homepage, subscriptions, and notification logic
├── media/ → User and product uploaded files
├── templates/ → Modular HTML templates
└── static/ → Custom CSS, JS, and images


---

## 🧱 Module-wise Explanation

### 🔹 1. Accounts Module
Handles all authentication flows, including **email verification**, **OTP login**, **referral tracking**, and **wallet management**.

**Key Models:**
- `Customer`
- `Vendor`
- `UserProfile`
- `WalletTransaction`

**Highlights:**
- Unique referral code generation  
- Email token verification system  
- Wallet balance credit/debit tracking  

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/f0c8228e-713f-476a-9a4b-163e86e485bf" />


---

### 🔹 2. Products Module
Manages categories, product details, banners, and images.

**Key Models:**
- `Category`
- `Product`
- `ProductImage`
- `Banner`

**Highlights:**
- Vendor-linked product uploads  
- Category-wise product display  
  

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/8b944e53-4878-41a9-bc80-25f357fa6f9e" />


---

### 🔹 3. Orders Module
Handles the entire checkout and order lifecycle.

**Features:**
- Add-to-cart and wishlist  
- Address management  
- Checkout and order confirmation  
- Order status tracking  

📸  
<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/0b778410-30a3-4ec9-b786-6ad37fc19648" />


---

### 🔹 4. Dashboard Module
Separate dashboards for both **Admin** and **Vendor**.

**Admin Capabilities:**
- Manage users, vendors, and products  
- Approve pending vendor items  
- Monitor overall revenue and sales stats  

**Vendor Capabilities:**
- Track orders  
- Manage product inventory  
- Wallet and earning statistics  

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/5194a8e5-dd40-4361-882d-673ab1582bb1" />


---

### 🔹 5. Core Module
Includes homepage UI, notification logic, and subscription management.

**Highlights:**
- Dynamic homepage banner  
- Notifications for new orders and messages  
- Prime subscription flow  

📸  
![Homepage](images/homepage.png)

---

## 💎 Prime Membership Logic

**Goal:** reward loyal users with premium benefits.  

**Implementation:**
- `PrimeSubscription` model stores start & end dates, amount, and active status.  
- When a user subscribes:
  - `is_prime_member = True`
  - Expiry date is automatically set  
- Prime users get:
  - Exclusive product discounts  
  - Priority notifications  
  - Special coupons  

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/33e3849c-77f1-49c7-8bc0-02d57ef5525a" />


---

## 🔗 MLM Referral Wallet System

**Concept:** A 3-Level referral chain where each referrer benefits when a new user joins through their code.

**Flow Example:**
A → B → C
C registers using B’s referral
→ B gets ₹20 in wallet
→ A (B’s referrer) gets ₹10 in wallet

**Implementation Details:**
- Every user gets a unique referral code in `UserProfile`.
- When a new user registers with a referral:
  - System identifies the referring chain recursively.
  - Updates wallet balances through `WalletTransaction`.
- Wallet can be used for purchases or Prime renewals.

<img width="1920" height="1020" alt="image" src="https://github.com/user-attachments/assets/3a9f6da4-7037-4329-9241-b077c03ee6c4" />


---

## ⚙️ Setup Instructions

### 🪜 Clone Repository
```bash
git clone https://github.com/yourusername/hksmartstore.git
cd hksmartstore
🧱 Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

📦 Install Dependencies
pip install -r requirements.txt

🔧 Configure Database

Edit the DATABASES section in hksmartstore/settings.py with your MySQL credentials.

🗄️ Migrate Database
python manage.py makemigrations
python manage.py migrate

🧑‍💻 Create Admin
python manage.py createsuperuser

▶️ Run Server
python manage.py runserver


Then visit
👉 http://127.0.0.1:8000/

🗄️ Database Schema Overview
Table	Description
Customer	Customer details and login info
Vendor	Vendor business details
UserProfile	Wallet and referral code info
WalletTransaction	Records credit/debit entries
Product	Product info and stock
Category	Product categorization
Order	Order and payment details
PrimeSubscription	Subscription details
Notification	App notifications
🔮 Future Enhancements

💳 Razorpay / Stripe Payment Gateway

🚚 Live Order Tracking

🧾 Invoice Generation

📱 Flutter Mobile App Integration

🤖 AI-Based Recommendation Engine

