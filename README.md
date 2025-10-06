# ChieCouture Django E-Commerce Platform

ChieCouture is a Django-based e-commerce platform where vendors can create stores, manage products, and interact with customers, while buyers can browse products, checkout, and leave reviews. The platform also integrates with Twitter for store and product announcements and sends email invoices to buyers.

---

## Features

### Vendor
- Create, edit, and delete stores
- Add, edit, and remove products
- View customer reviews
- Dashboard for managing store inventory and reviews
- Automatic Twitter announcements for new stores/products

### Buyer
- Browse stores and products
- Add products to cart and checkout
- Leave reviews (verified if purchased)
- Receive invoice via email

### General
- Role-based authentication (Vendor / Buyer)
- Password reset via email
- Admin management

---

## Installation

```bash
git clone https://github.com/yourusername/chiecouture.git
cd chiecouture
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000 in your browser to see the platform.

Running Tests
```
python manage.py test
```
