# 🎬 Movie Store API

A simple **REST API for an online movie store** built with **Python, Flask, and MySQL**.
The API allows users to search movies, manage a shopping cart, and simulate checkout.

This project demonstrates basic backend development concepts including:

* REST API design
* Database integration with MySQL
* CSV fallback data source
* Error handling
* JSON responses

---

# 🚀 Features

* 🔎 Search movies by title, author, or genre
* 🛒 Add movies to a shopping cart
* 📦 View cart contents
* 💳 Simulate checkout process
* 🗄 MySQL database support
* 📄 CSV fallback if the database is unavailable
* 🌐 RESTful API endpoints

---

# 🛠 Tech Stack

| Technology             | Purpose                     |
| ---------------------- | --------------------------- |
| Python                 | Main programming language   |
| Flask                  | Web framework for API       |
| MySQL                  | Database                    |
| mysql-connector-python | MySQL connection            |
| CSV                    | Backup data source          |
| Requests               | Simulated payment API calls |

---

# 📂 Project Structure

```
movieStore/
│
├── app.py            # Flask API application
├── local_app.py      # CLI version of the Movie Store
├── movieStore.csv    # Backup dataset
├── requirements.txt  # Project dependencies
└── README.md
```

---

# ⚙️ Installation

Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/movie-store-api.git
```

Move into the project directory:

```
cd movie-store-api
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# ▶️ Running the API

Start the Flask server:

```
python app.py
```

The API will run at:

```
http://127.0.0.1:5000
```

---

# 📡 API Endpoints

### Home

```
GET /
```

Returns basic API information.

---

### Get all movies

```
GET /movies
```

Returns a list of all movies.

---

### Search movies

```
GET /search?q=keyword
```

Example:

```
/search?q=action
```

---

### View cart

```
GET /cart
```

Returns items currently in the cart.

---

### Add movie to cart

```
POST /cart
```

Example JSON body:

```
{
  "id": 5
}
```

---

### Checkout

```
POST /checkout
```

Simulates a payment request.

---

# 🗄 Database

The API uses a MySQL database:

```
movie_store
```

Table:

```
movies
```

Example schema:

```sql
CREATE TABLE movies (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    genre VARCHAR(100),
    price DECIMAL(10,2),
    availability BOOLEAN
);
```

---

# 📄 CSV Fallback

If MySQL is unavailable, the application automatically loads data from:

```
movieStore.csv
```

This ensures the API continues working even if the database connection fails.

---

# 📌 Future Improvements

Possible enhancements for this project:

* SQL-based search queries
* Docker containerization
* API documentation with Swagger
* User authentication
* Persistent cart storage
* Deployment to cloud platforms

---

# 👩‍💻 Author

Tamuna Gegechkori

Backend development practice project using Flask and MySQL.
