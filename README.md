# Ethiopian Cultural Store

A full-stack e-commerce platform built using **Flask**, **Supabase**, and **Bootstrap**. This application allows users to browse products, add them to their carts, and manage stock levels in real time.

## Features
- **Product Service**: Fetch, update, and manage products and their inventory.
- **Cart Service**: Add, remove, and update items in the user's cart while ensuring stock availability.
- **Authentication**: User signup and login system secured with password hashing.
- **Real-time Stock Updates**: Ensure seamless product availability tracking.

---

## **Tech Stack**
- **Backend**: Flask, Supabase (PostgreSQL)
- **Frontend**: HTML, Bootstrap, AJAX
- **API Communication**: RESTful APIs using HTTP methods

---

## **Project Structure**
```
ShoppingCart/
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── cart.py
│   │   ├── product.py
│   │   ├── __init__.py
│   ├── static/
│   │   ├── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── log_in.html
│   │   ├── sign_up.html
│   ├── app.py
├── .env
├── requirements.txt
├── run.sh
```

---

## **Installation & Setup**

### **1. Clone the repository**
```sh
git clone https://github.com/your-username/ethiopian-cultural-store.git
cd ethiopian-cultural-store
```

### **2. Set up a virtual environment (optional)**
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### **3. Install dependencies**
```sh
pip install -r requirements.txt
```

### **4. Set up environment variables**
Create a `.env` file in the project root and add your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### **5. Run the services**
Each service should run separately.

#### **Start the Application**
```sh
python app.py
```

---

## **API Endpoints**

### **Authentication Service**
| Method | Endpoint          | Description          |
|--------|------------------|----------------------|
| POST   | `/signup`        | Register new user   |
| POST   | `/login`         | Login user          |

### **Product Service**
| Method | Endpoint            | Description                |
|--------|--------------------|----------------------------|
| GET    | `/products`        | Fetch all products        |
| GET    | `/products/<id>`   | Fetch a single product    |
| PUT    | `/products/<id>`   | Update product quantity   |

### **Cart Service**
| Method | Endpoint                                | Description                         |
|--------|----------------------------------------|-------------------------------------|
| GET    | `/cart/<user_id>`                      | Fetch user's cart                  |
| POST   | `/cart/<user_id>/add/<product_id>`     | Add product to cart                |
| POST   | `/cart/<user_id>/remove/<product_id>`  | Remove product from cart           |

---

## **Contributing**
Feel free to submit issues and pull requests! 🚀

---

## **License**
This project is licensed under the MIT License.

