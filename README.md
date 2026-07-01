# MovieStar

A light, editorial-style online movie store built with Python, Flask, MySQL,
vanilla JavaScript, and CSS.

MovieStar combines a REST API with a responsive storefront where visitors can
search and filter movies, check availability, add titles to a shopping bag,
and complete a safe demo checkout.

## Live demo

[Open MovieStar on GitHub Pages](https://tamuna9.github.io/movie-store-api/)

The public demo is a static GitHub Pages edition. Its shopping bag is saved in
the browser, and checkout remains a safe simulation with no real payments.

## Features

- Responsive light-themed storefront
- 100-film catalogue
- Search by title, author, or genre
- Genre filters
- Shopping bag with add and remove actions
- Demo checkout without real payments
- Availability and unavailability reasons:
  - licensing pause
  - coming soon
  - physical edition sold out
- MySQL as the primary data source
- Automatic CSV fallback when MySQL is unavailable or incomplete
- REST API endpoints

## Tech stack

| Technology | Purpose |
| --- | --- |
| Python | Application logic |
| Flask | Web server and REST API |
| MySQL | Primary movie database |
| CSV | Offline fallback catalogue |
| JavaScript | Search, filters, and shopping bag |
| CSS | Responsive storefront design |
| Requests | Optional external payment-gateway integration |

## Project structure

```text
movieStore/
├── app.py
├── local_app.py
├── movieStore .csv
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/Tamuna9/movie-store-api.git
cd movie-store-api
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the storefront

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000/
```

The terminal reports which source was loaded and how many films are available.

## Data sources

The app first tries to load the `movies` table from the `movie_store` MySQL
database. If MySQL is unavailable or its availability data is incomplete, the
app automatically loads `movieStore .csv`.

Expected MySQL schema:

```sql
CREATE TABLE movies (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    availability BOOLEAN
);
```

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api` | API information |
| GET | `/movies` | All movies |
| GET | `/search?q=action` | Search movies |
| GET | `/cart` | Shopping-bag contents |
| POST | `/cart` | Add a movie using `{"id": 5}` |
| DELETE | `/cart/<id>` | Remove a movie |
| POST | `/checkout` | Complete demo checkout |

## Payment note

Checkout is simulated by default. It does not request payment details or charge
real money. A real gateway can be enabled later by setting
`PAYMENT_GATEWAY_URL` and implementing the provider's secure server-side flow.

## Author

Tamuna Gegechkori
