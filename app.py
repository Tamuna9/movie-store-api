import csv
import traceback
import requests
import mysql.connector

from flask import Flask, request, jsonify

app = Flask(__name__)

movies = []
cart = []

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",   
    "database": "movie_store",
    "port": 3306,
    "use_pure": True
}


# Database / File loading

def get_db_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG["port"],
        use_pure=DB_CONFIG["use_pure"]
    )

def load_movies_from_mysql():
    global movies

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT id, title, author, genre, price, availability
    FROM movies
""")
    movies = cursor.fetchall()

    cursor.close()
    conn.close()


def load_movies_from_csv():
    global movies

    with open(
        r"D:\Desktop\Success college\Python home work\movieStore\movieStore .csv",
        "r",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)
        movies = [row for row in reader]

# Helper functions

def search_movie(keyword):
    keyword = keyword.lower().strip()

    if not keyword:
        return movies

    matches = []

    for movie in movies:
        title = str(movie.get("title", "")).lower()
        author = str(movie.get("author", "")).lower()
        genre = str(movie.get("genre", "")).lower()

        if keyword in title or keyword in author or keyword in genre:
            matches.append(movie)

    return matches

def add_movie_to_cart(movie_id):
    for movie in movies:
        try:
            if int(movie["id"]) == int(movie_id):
                cart.append(movie)
                return True
        except (ValueError, TypeError, KeyError):
            continue

    return False

def checkout(cart_items):
    total = sum(float(movie["price"]) for movie in cart_items)

    try:
        response = requests.post(
            "https://paymentgateway.com/process",
            data={"total": total},
            timeout=10
        )

        return response.status_code == 200

    except requests.exceptions.Timeout:
        print("Timeout while processing payment")
        return False

    except requests.exceptions.RequestException as e:
        print(f"Payment request error: {e}")
        return False

# Routes

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Movie Store API is running",
        "data_source": "MySQL or CSV fallback",
        "routes": [
            "/movies",
            "/search?q=action",
            "/cart",
            "/checkout"
        ]
    })

@app.route("/movies", methods=["GET"])
def get_movies():
    return jsonify(movies)

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("q", "")
    result = search_movie(keyword)
    return jsonify(result)

@app.route("/cart", methods=["GET"])
def view_cart():
    return jsonify(cart)

@app.route("/cart", methods=["POST"])
def add_to_cart_route():
    data = request.get_json(silent=True)

    if not data or "id" not in data:
        return jsonify({"error": "Missing movie id"}), 400

    movie_id = data["id"]

    if add_movie_to_cart(movie_id):
        return jsonify({"message": "Movie added to cart"})
    else:
        return jsonify({"error": "Movie not found"}), 404

@app.route("/checkout", methods=["POST"])
def checkout_cart():
    if not cart:
        return jsonify({"error": "Your cart is empty"}), 400

    if checkout(cart):
        cart.clear()
        return jsonify({"message": "Payment processed successfully"})
    else:
        return jsonify({"error": "Payment failed, please try again"}), 500

# Main

if __name__ == "__main__":
    try:
        load_movies_from_mysql()
        print("Movies loaded from MySQL successfully")
    except Exception:
        print("MySQL load failed:")
        traceback.print_exc()
        print("Loading from CSV instead...")
        load_movies_from_csv()

    app.run(host="0.0.0.0", port=5000, debug=True)