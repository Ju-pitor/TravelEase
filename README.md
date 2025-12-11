# 🌍 TravelEase – Travel Booking & Management Platform

TravelMate is a full-featured travel booking web application built using **Django 5**, featuring destination management, package booking, traveler dashboard, agency admin panel, and secure online payments using **Razorpay**.

---

## 🚀 Features

### 👤 User & Traveler Module
- Browse travel destinations & packages  
- View package details  
- Book packages online  
- Manage bookings  
- Make secure online payments (Razorpay)

### 🏢 Agency / Admin Module
- Add, edit & delete destinations  
- Create and manage travel packages  
- Upload images  
- View and manage customer bookings  
- Track payments and booking status  

### 💳 Payment System (Razorpay Integration)
- Secure online payment via Razorpay  
- Auto-update booking status after payment  
- Razorpay order creation & webhook support  
- Payment receipt generation (PDF)

### 🧾 Receipts & PDF Generation
- Stylish PDF receipt using **ReportLab / wkhtmltopdf**  
- Sent to user after successful booking

### 🗂 Tech Stack
**Frontend:** HTML, CSS, Bootstrap  
**Backend:** Django 5  
**Database:** SQLite (Development)  
**Payments:** Razorpay API  
**PDF Engine:** ReportLab, wkhtmltopdf  
**Other Tools:** Pillow, Requests  

---

## 📁 Project Structure

```
myproject/
│── agency/
│── app_admin/
│── travelers/
│── packages/
│── templates/
│── media/
│── myproject/        # Main Django settings
│── manage.py
│── requirements.txt
│── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/travelmate.git
cd travelmate
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv env
env\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations
```bash
python manage.py migrate
```

### 5️⃣ Run the Development Server
```bash
python manage.py runserver
```

---

## 💳 Payment Integration Setup (Razorpay)

Go to https://dashboard.razorpay.com → Developers → API Keys  
Copy:

- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`

Add them to your `settings.py`:

```python
RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"
```

---

## 📜 Environment Variables

Create a `.env` file (optional):

```
RAZORPAY_KEY_ID=xxxx
RAZORPAY_KEY_SECRET=xxxx
```

---

## 📄 Generate Requirements File

```bash
pip freeze > requirements.txt
```

---

## 🧪 Testing Payments  
Use Razorpay test mode keys in development.

---

## 📬 Contributions  
Pull requests are welcome. For significant changes, please open an issue first.

---

## 📑 License  
This project is licensed under the MIT License.

---

##  Acknowledgements  
- Django Documentation  
- Razorpay Developer API  
  

