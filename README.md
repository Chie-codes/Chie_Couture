# ChieCouture

ChieCouture is a Django-based e-commerce platform designed for vendors to create stores, list products, and manage customer interactions. Customers can browse stores, purchase products, leave reviews, and receive email invoices upon checkout. The platform also integrates with Twitter to automatically announce new stores and products.

---

## Features

### For Vendors
- Create, edit, and delete stores.
- Add, edit, and remove products.
- View all customer reviews on their products.
- Tweet announcements when adding a new store or product.
- Dashboard to manage store inventory and reviews.

### For Buyers
- Browse stores and products.
- Add products to a shopping cart.
- Checkout and receive invoices via email.
- Leave product reviews (verified if purchased).

### Authentication
- Role-based users: Vendor and Buyer.
- User registration and login.
- Password reset via email.

### Other
- Twitter integration for store/product announcements.
- Email notifications for order invoices.
- Admin access for managing users and stores.

---

## Installation

### Prerequisites
- Python 3.13+
- Django 5.2+
- SQLite (default)
- Twitter developer account with API credentials
- Email SMTP configuration for sending invoices
