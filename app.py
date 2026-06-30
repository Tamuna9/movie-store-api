import csv
import os
import traceback
from pathlib import Path

import mysql.connector
import requests
from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "movieStore .csv"

app = Flask(__name__)

movies = []
cart = []

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "movie_store",
    "port": 3306,
    "use_pure": True,
}

UNAVAILABLE_STATUSES = (
    {
        "code": "licensing",
        "label": "Licensing pause",
        "message": "Temporarily unavailable while the license is renewed.",
    },
    {
        "code": "coming_soon",
        "label": "Coming soon",
        "message": "This title has been announced and will be available soon.",
    },
    {
        "code": "sold_out",
        "label": "Disc sold out",
        "message": "The physical edition is currently out of stock.",
    },
)


@app.after_request
def prevent_stale_development_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Database / file loading

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def normalize_movie(movie):
    """Return the same predictable shape for MySQL and CSV records."""
    raw_availability = movie.get("availability", movie.get("aviability", False))
    if isinstance(raw_availability, str):
        is_available = raw_availability.strip().lower() in {"1", "true", "yes"}
    else:
        is_available = bool(raw_availability)

    try:
        movie_id = int(movie.get("id", 0))
    except (TypeError, ValueError):
        movie_id = 0

    try:
        price = float(movie.get("price", 0))
    except (TypeError, ValueError):
        price = 0.0

    if is_available:
        status = {
            "code": "available",
            "label": "Available",
            "message": "Available to add to your bag.",
        }
    else:
        status = UNAVAILABLE_STATUSES[movie_id % len(UNAVAILABLE_STATUSES)]

    return {
        "id": movie_id,
        "title": str(movie.get("title", "")).strip(),
        "author": str(movie.get("author", "")).strip(),
        "genre": str(movie.get("genre", "")).strip(),
        "price": price,
        "availability": is_available,
        "availability_status": status,
    }


def load_movies_from_mysql():
    global movies

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, title, author, genre, price, availability
            FROM movies
            """
        )
        database_rows = cursor.fetchall()
        valid_rows = [
            movie
            for movie in database_rows
            if movie.get("id") and str(movie.get("title", "")).strip().lower() != "title"
        ]
        if not valid_rows:
            raise ValueError("The movies table does not contain valid records")
        if all(movie.get("availability") is None for movie in valid_rows):
            raise ValueError("The movies table has no availability data")

        movies = [normalize_movie(movie) for movie in valid_rows]
    finally:
        cursor.close()
        conn.close()


def load_movies_from_csv():
    global movies

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        movies = [normalize_movie(row) for row in csv.DictReader(file)]


def initialize_movies():
    try:
        load_movies_from_mysql()
        available_count = sum(movie["availability"] for movie in movies)
        print(
            "Movies loaded from MySQL successfully "
            f"({len(movies)} total, {available_count} available)"
        )
    except Exception:
        print("MySQL load failed. Loading from CSV instead.")
        if app.debug:
            traceback.print_exc()
        load_movies_from_csv()
        available_count = sum(movie["availability"] for movie in movies)
        print(
            f"Movies loaded from CSV ({len(movies)} total, "
            f"{available_count} available)"
        )


# Helper functions

def search_movie(keyword):
    normalized_keyword = keyword.lower().strip()
    if not normalized_keyword:
        return movies

    return [
        movie
        for movie in movies
        if normalized_keyword in movie["title"].lower()
        or normalized_keyword in movie["author"].lower()
        or normalized_keyword in movie["genre"].lower()
    ]


def add_movie_to_cart(movie_id):
    for movie in movies:
        if movie["id"] != movie_id:
            continue
        if not movie["availability"]:
            return "unavailable"
        if any(item["id"] == movie_id for item in cart):
            return "already_added"

        cart.append(movie)
        return "added"

    return "not_found"


def checkout(cart_items):
    """Use a real gateway when configured; otherwise complete a safe demo checkout."""
    if not cart_items:
        return False

    gateway_url = os.getenv("PAYMENT_GATEWAY_URL")
    if not gateway_url:
        return True

    total = sum(movie["price"] for movie in cart_items)
    try:
        response = requests.post(gateway_url, data={"total": total}, timeout=10)
        return response.ok
    except requests.exceptions.RequestException as error:
        app.logger.warning("Payment request failed: %s", error)
        return False


# Routes

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/api", methods=["GET"])
def api_info():
    return jsonify(
        {
            "message": "Movie Store API is running",
            "data_source": "MySQL or CSV fallback",
            "routes": ["/movies", "/search?q=action", "/cart", "/checkout"],
        }
    )


@app.route("/movies", methods=["GET"])
def get_movies():
    return jsonify(movies)


@app.route("/search", methods=["GET"])
def search():
    return jsonify(search_movie(request.args.get("q", "")))


@app.route("/cart", methods=["GET"])
def view_cart():
    return jsonify(cart)


@app.route("/cart", methods=["POST"])
def add_to_cart_route():
    data = request.get_json(silent=True)
    if not data or "id" not in data:
        return jsonify({"error": "Missing movie id"}), 400

    try:
        movie_id = int(data["id"])
    except (TypeError, ValueError):
        return jsonify({"error": "Movie id must be a number"}), 400

    result = add_movie_to_cart(movie_id)
    if result == "added":
        return jsonify({"message": "Movie added to cart"}), 201
    if result == "unavailable":
        return jsonify({"error": "This movie is currently unavailable"}), 409
    if result == "already_added":
        return jsonify({"error": "Movie is already in your cart"}), 409
    return jsonify({"error": "Movie not found"}), 404


@app.route("/cart/<int:movie_id>", methods=["DELETE"])
def remove_from_cart(movie_id):
    for index, movie in enumerate(cart):
        if movie["id"] == movie_id:
            cart.pop(index)
            return jsonify({"message": "Movie removed from cart"})

    return jsonify({"error": "Movie not found in cart"}), 404


@app.route("/checkout", methods=["POST"])
def checkout_cart():
    if not cart:
        return jsonify({"error": "Your cart is empty"}), 400

    if checkout(cart):
        cart.clear()
        return jsonify({"message": "Payment processed successfully"})

    return jsonify({"error": "Payment failed, please try again"}), 502


if __name__ == "__main__":
    initialize_movies()
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"},
    )
