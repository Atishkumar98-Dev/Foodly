# 🍽️ Food Ordering Django App

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.1.2-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blueviolet)
![Razorpay](https://img.shields.io/badge/Razorpay-Payment-orange)

A full-featured **Food Ordering Web Application** built with **Django** and **Bootstrap**.  
Allows users to browse foods, place orders, pay via **Razorpay**, and track orders.  
Admins can manage foods, ingredients, tags, discounts, stock, orders, and more via a dashboard.

---

## 🌟 Features

| Section | User Features | Admin Features |
|---------|---------------|----------------|
| **Foods** | Browse foods, view nutrition, ingredients & recipes | Add/Edit/Delete foods, image upload, nutrition info |
| **Ingredients** | View ingredients per food | Add/Edit/Delete ingredients, mark allergens |
| **Tags** | See tags (Vegan, Gluten-Free, Spicy) | Add/Edit/Delete tags and assign to foods |
| **Discounts** | Apply coupon codes | Add/Edit/Delete discounts with date ranges & percentages |
| **Orders** | Place orders, choose quantity, pay with Razorpay | View all orders, update status, delivered_at |
| **Stock** | – | Manage inventory quantity per food |
| **Allergies** | View allergens per food | Add/Edit/Delete allergy types |
| **Restaurants & Chefs** | View restaurants & chef specialties | Add/Edit/Delete restaurants & chefs |

---

## 🛠️ Technologies Used
- **Backend:** Django 5.x, Python 3.12  
- **Frontend:** HTML5, CSS3, Bootstrap 5, JS  
- **Database:** PostgreSQL  
- **Payment Gateway:** Razorpay  
- **Docker:** Containerization for easy deployment  

---

## ⚙️ Setup & Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/food-ordering.git
cd food-ordering
````

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:

```bash
python manage.py createsuperuser
```

6. Run the server:

```bash
python manage.py runserver
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
RAZORPAY_KEY_ID=rzp_test_RMiHiWbJTpiKLz
RAZORPAY_KEY_SECRET=cX1BYL2Bkan9tyWIKmcfB42c
DATABASE_NAME=Foodly_DB
DATABASE_USER=postgres
DATABASE_PASSWORD=newpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_ENGINE=django.db.backends.postgresql
```

---

## 🐳 Docker Setup

1. Build and run containers:

```bash
docker-compose up --build
```

2. Exposes app at `http://localhost:8000`
3. Uses PostgreSQL container configured from `.env`.

---

## 💳 Razorpay Integration

* Payment handled via Razorpay checkout.
* Prefills user details (name, email).
* Success and failure URLs:

```python
path('order-success/<int:order_id>/', views.order_success, name='order_success'),
path('order-failure/<int:order_id>/', views.order_failure, name='order_failure'),
```

---

## 👤 User Authentication

* Register, login, and logout functionality
* Users can track their orders, view order history, and check order status.

---

## 🔗 Useful Links

* [Django Documentation](https://docs.djangoproject.com/)
* [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/)
* [Razorpay Docs](https://razorpay.com/docs/)

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push: `git push origin feature/new-feature`
5. Create a Pull Request

---

