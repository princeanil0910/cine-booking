"""
Cine Booking — Flask cinema ticket booking system
Run:
    pip install -r requirements.txt
    python app.py
Open: http://127.0.0.1:5000

Admin:
    username: admin
    password: admin123
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from functools import wraps

from flask import (
    Flask, Response, jsonify, redirect, render_template,
    request, session, url_for
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "cine_booking.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "cine-booking-development-secret"
)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

MOVIES = [
    {
        "id": 1, "title": "Midnight Protocol", "genre": "Action • Thriller",
        "language": "English", "duration": "2h 18m", "rating": "U/A 16+",
        "price": 220, "poster": "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=900&q=85",
        "description": "An elite cyber investigator races through one dangerous night to stop a city-wide blackout."
    },
    {
        "id": 2, "title": "Monsoon Hearts", "genre": "Romance • Drama",
        "language": "Kannada", "duration": "2h 06m", "rating": "U",
        "price": 180, "poster": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=900&q=85",
        "description": "Two old friends meet again during Bengaluru's monsoon season and rediscover what they left behind."
    },
    {
        "id": 3, "title": "Galaxy Beyond", "genre": "Sci-Fi • Adventure",
        "language": "English", "duration": "2h 31m", "rating": "U/A 13+",
        "price": 260, "poster": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?auto=format&fit=crop&w=900&q=85",
        "description": "A young pilot joins the first mission beyond the known edge of human space."
    },
    {
        "id": 4, "title": "Laughing Bus Stop", "genre": "Comedy",
        "language": "Hindi", "duration": "1h 54m", "rating": "U",
        "price": 170, "poster": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=85",
        "description": "A chaotic group of strangers discover that a missed bus can lead to an unforgettable day."
    },
    {
        "id": 5, "title": "Kantara: Chapter One", "genre": "Action • Mythology",
        "language": "Kannada", "duration": "2h 35m", "rating": "U/A 16+",
        "price": 240, "poster": "https://images.unsplash.com/photo-1533929736458-ca588d08c8be?auto=format&fit=crop&w=900&q=85",
        "description": "A powerful Kannada legend of courage, tradition and a community protecting its sacred land."
    },
    {
        "id": 6, "title": "Sapta Sagaradaache Ello", "genre": "Romance • Drama",
        "language": "Kannada", "duration": "2h 20m", "rating": "U/A 13+",
        "price": 200, "poster": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=85",
        "description": "A tender story about love, distance and the choices that shape two connected lives."
    },
    {
        "id": 7, "title": "Kantara", "genre": "Action • Mythology",
        "language": "Kannada", "duration": "2h 28m", "rating": "U/A 16+",
        "price": 220, "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=900&q=85",
        "description": "A village, an ancient promise and one man's fight to protect the land he calls home."
    },
    {
        "id": 8, "title": "Vikram Vedha", "genre": "Action • Crime",
        "language": "Tamil", "duration": "2h 40m", "rating": "U/A 16+",
        "price": 230, "poster": "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=900&q=85",
        "description": "A sharp police officer and a clever outlaw face off in a story of truth and perspective."
    },
    {
        "id": 9, "title": "Ala Vaikunthapurramuloo", "genre": "Drama • Musical",
        "language": "Telugu", "duration": "2h 45m", "rating": "U/A 13+",
        "price": 210, "poster": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=900&q=85",
        "description": "A musical family drama about identity, ambition and finding your way back home."
    },
    {
        "id": 10, "title": "Premalu", "genre": "Romance • Comedy",
        "language": "Malayalam", "duration": "2h 36m", "rating": "U/A 13+",
        "price": 190, "poster": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=900&q=85",
        "description": "A warm and funny love story that travels from Kerala to a new city and new possibilities."
    },
]
MOVIE_DETAILS = {
    1: {"cast": "Arjun Mehta, Nisha Rao, Kabir Singh", "director": "Rohan Sen", "update": "Extra IMAX shows added for Bengaluru this week."},
    2: {"cast": "Ananya Shetty, Rishi Varma, Kavya Rao", "director": "Maya Prakash", "update": "Popular evening shows are now open for booking."},
    3: {"cast": "Dev Malhotra, Tara Iyer, Vikram Das", "director": "Aarav Khanna", "update": "3D and IMAX formats are available at select theatres."},
    4: {"cast": "Rohan Kapoor, Meera Joshi, Amit Nair", "director": "Neel Batra", "update": "Family shows added for the weekend."},
    5: {"cast": "Rishab Shetty, Sapthami Gowda, Kishore", "director": "Anil Kumar", "update": "Kannada shows are selling fast across Bengaluru."},
    6: {"cast": "Rakshit Shetty, Rukmini Vasanth, Chaithra J. Achar", "director": "Hemanth M. Rao", "update": "Late-night Kannada screenings now available."},
    7: {"cast": "Rishab Shetty, Kishore, Achyuth Kumar", "director": "Rishab Shetty", "update": "Special Kannada fan screenings are available today."},
    8: {"cast": "Vijay Sethupathi, Madhavan, Shraddha Srinath", "director": "Pushkar-Gayathri", "update": "Tamil 2D shows added at Screen 2."},
    9: {"cast": "Allu Arjun, Pooja Hegde, Tabu", "director": "Trivikram Srinivas", "update": "Telugu evening shows are now booking."},
    10: {"cast": "Naslen, Mamitha Baiju, Sangeeth Prathap", "director": "Girish A. D.", "update": "Malayalam shows added for Bengaluru audiences."},
}

MOVIE_DETAILS[103] = {
    "cast": "Yash, Kiara Advani, Huma Qureshi, Nayanthara, Tara Sutaria, Rukmini Vasanth",
    "director": "Geetu Mohandas",
    "update": "Releasing tomorrow, 26 Aug 2026. Bengaluru bookings open soon.",
    "release_date": "26 Aug 2026",
    "interested": "1.4M+ are interested",
    "cast_members": [
        {"name": "Yash", "role": "as Raya", "image": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=300&q=85"},
        {"name": "Kiara Advani", "role": "as Nadia", "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=85"},
        {"name": "Huma Qureshi", "role": "as Elizabeth", "image": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=85"},
        {"name": "Nayanthara", "role": "as Ganga", "image": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=85"},
        {"name": "Tara Sutaria", "role": "as Rebecca", "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=300&q=85"},
        {"name": "Rukmini Vasanth", "role": "as Melissa", "image": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=300&q=85"},
    ],
}

ACTOR_DETAILS = {
    "Yash": {"role": "Raya", "bio": "A celebrated Kannada performer known for powerful action and dramatic roles.", "image": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=600&q=85"},
    "Kiara Advani": {"role": "Nadia", "bio": "An acclaimed Indian actor whose work spans Hindi, Telugu and Kannada cinema.", "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=600&q=85"},
    "Huma Qureshi": {"role": "Elizabeth", "bio": "Known for versatile performances across drama, crime and thriller films.", "image": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=85"},
    "Nayanthara": {"role": "Ganga", "bio": "A leading South Indian star celebrated for memorable performances in many languages.", "image": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=600&q=85"},
    "Tara Sutaria": {"role": "Rebecca", "bio": "An actor and performer known for her contemporary screen presence.", "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=600&q=85"},
    "Rukmini Vasanth": {"role": "Melissa", "bio": "A popular Kannada actor admired for natural and emotionally rich performances.", "image": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=600&q=85"},
    "Rishab Shetty": {"role": "Lead", "bio": "A Kannada actor, writer and filmmaker known for rooted, high-energy cinema.", "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=600&q=85"},
    "Rakshit Shetty": {"role": "Lead", "bio": "A Kannada actor and producer known for distinctive romantic and dramatic roles.", "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=600&q=85"},
    "Allu Arjun": {"role": "Lead", "bio": "A Telugu cinema star recognised for dance, style and charismatic performances.", "image": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=600&q=85"},
    "Naslen": {"role": "Lead", "bio": "A Malayalam performer known for warm, youthful and comic characters.", "image": "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?auto=format&fit=crop&w=600&q=85"},
    "Vijay Sethupathi": {"role": "Lead", "bio": "A Tamil actor celebrated for expressive and versatile character work.", "image": "https://images.unsplash.com/photo-1504593811423-6dd665756598?auto=format&fit=crop&w=600&q=85"},
}

for movie_id, names in {
    1: ["Arjun Mehta", "Nisha Rao", "Kabir Singh"], 2: ["Ananya Shetty", "Rishi Varma", "Kavya Rao"],
    3: ["Dev Malhotra", "Tara Iyer", "Vikram Das"], 4: ["Rohan Kapoor", "Meera Joshi", "Amit Nair"],
    5: ["Rishab Shetty", "Sapthami Gowda", "Kishore"], 6: ["Rakshit Shetty", "Rukmini Vasanth", "Chaithra J. Achar"],
    7: ["Rishab Shetty", "Kishore", "Achyuth Kumar"], 8: ["Vijay Sethupathi", "Madhavan", "Shraddha Srinath"],
    9: ["Allu Arjun", "Pooja Hegde", "Tabu"], 10: ["Naslen", "Mamitha Baiju", "Sangeeth Prathap"],
}.items():
    MOVIE_DETAILS[movie_id]["cast_members"] = [
        {"name": name, **ACTOR_DETAILS.get(name, {"role": "Cast", "bio": "A talented screen performer.", "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=600&q=85"})}
        for name in names
    ]

for details in MOVIE_DETAILS.values():
    for person in details.get("cast_members", []):
        ACTOR_DETAILS.setdefault(person["name"], {
            "role": person.get("role", "Cast"),
            "bio": "A talented screen performer featured in popular Indian cinema.",
            "image": person.get("image", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=600&q=85"),
        })

for person in MOVIE_DETAILS[103]["cast_members"]:
    person.update(ACTOR_DETAILS.get(person["name"], {}))

SHOWTIMES = [
    {"id": 1, "movie_id": 1, "date": "2026-08-25", "time": "10:30 AM", "screen": "Screen 1", "format": "2D", "price": 220},
    {"id": 2, "movie_id": 1, "date": "2026-08-25", "time": "02:00 PM", "screen": "Screen 1", "format": "2D", "price": 220},
    {"id": 3, "movie_id": 1, "date": "2026-08-25", "time": "07:15 PM", "screen": "Screen 1", "format": "IMAX", "price": 320},
    {"id": 4, "movie_id": 2, "date": "2026-08-25", "time": "11:45 AM", "screen": "Screen 2", "format": "2D", "price": 180},
    {"id": 5, "movie_id": 2, "date": "2026-08-25", "time": "06:30 PM", "screen": "Screen 2", "format": "2D", "price": 180},
    {"id": 6, "movie_id": 3, "date": "2026-08-25", "time": "01:15 PM", "screen": "Screen 3", "format": "3D", "price": 260},
    {"id": 7, "movie_id": 3, "date": "2026-08-25", "time": "09:00 PM", "screen": "Screen 3", "format": "IMAX", "price": 360},
    {"id": 8, "movie_id": 4, "date": "2026-08-25", "time": "04:30 PM", "screen": "Screen 4", "format": "2D", "price": 170},
    {"id": 9, "movie_id": 5, "date": "2026-08-25", "time": "03:30 PM", "screen": "Screen 5", "format": "2D", "price": 240},
    {"id": 10, "movie_id": 6, "date": "2026-08-25", "time": "08:45 PM", "screen": "Screen 6", "format": "2D", "price": 200},
    {"id": 11, "movie_id": 7, "date": "2026-08-25", "time": "12:15 PM", "screen": "Screen 1", "format": "2D", "price": 220},
    {"id": 12, "movie_id": 8, "date": "2026-08-25", "time": "05:45 PM", "screen": "Screen 2", "format": "2D", "price": 230},
    {"id": 13, "movie_id": 9, "date": "2026-08-25", "time": "07:30 PM", "screen": "Screen 3", "format": "2D", "price": 210},
    {"id": 14, "movie_id": 10, "date": "2026-08-25", "time": "09:15 PM", "screen": "Screen 4", "format": "2D", "price": 190},
]

THEATRES = [
    {"name": "Cinepolis Orion Mall", "area": "Rajajinagar", "distance": "2.4 km", "features": "IMAX · Dolby Atmos"},
    {"name": "PVR: Phoenix Marketcity", "area": "Mahadevapura", "distance": "8.1 km", "features": "4DX · Recliner seats"},
    {"name": "INOX: Garuda Mall", "area": "Magrath Road", "distance": "5.7 km", "features": "Dolby Atmos · Food court"},
    {"name": "Gopalan Cinemas", "area": "Bannerghatta Road", "distance": "6.3 km", "features": "2D · Large screens"},
]

UPCOMING_MOVIES = [
    {
        "id": 103, "title": "Toxic", "genre": "Action • Thriller",
        "language": "Kannada", "duration": "2h 40m", "rating": "U/A 16+",
        "release_date": "26 Aug 2026", "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=900&q=85",
        "description": "A stylish Kannada action thriller arriving on the big screen."
    },
    {
        "id": 101, "title": "The Last Horizon", "genre": "Sci-Fi • Mystery",
        "language": "English", "duration": "2h 24m", "rating": "U/A 13+",
        "release_date": "29 Aug 2026", "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=900&q=85",
        "description": "A stranded crew follows a signal from the edge of the galaxy before time runs out."
    },
    {
        "id": 102, "title": "Bengaluru Junction", "genre": "Drama • Family",
        "language": "Kannada", "duration": "2h 10m", "rating": "U",
        "release_date": "05 Sep 2026", "poster": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=900&q=85",
        "description": "Four lives cross paths on one unforgettable day in the city they call home."
    },
]

SEAT_ROWS = ["A", "B", "C", "D", "E", "F", "G"]
SEATS_PER_ROW = 8


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                showtime_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                seats TEXT NOT NULL,
                seat_count INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_status TEXT NOT NULL DEFAULT 'Pending',
                booking_status TEXT NOT NULL DEFAULT 'Confirmed',
                created_at TEXT NOT NULL,
                cancelled_at TEXT,
                updated_at TEXT
            )
        """)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(bookings)")}
        if "updated_at" not in columns:
            conn.execute("ALTER TABLE bookings ADD COLUMN updated_at TEXT")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
                comment TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def movie_by_id(movie_id):
    return next((m for m in MOVIES if m["id"] == int(movie_id)), None)


def showtime_by_id(showtime_id):
    return next((s for s in SHOWTIMES if s["id"] == int(showtime_id)), None)


def reviews_for_movie(movie_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT name, rating, comment, created_at FROM reviews WHERE movie_id = ? ORDER BY id DESC",
            (movie_id,)
        ).fetchall()
    reviews = [dict(row) for row in rows]
    average = round(sum(row["rating"] for row in reviews) / len(reviews), 1) if reviews else 0
    return reviews, average


def all_seats():
    return [f"{row}{num}" for row in SEAT_ROWS for num in range(1, SEATS_PER_ROW + 1)]


def booked_seats(showtime_id):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """SELECT seats FROM bookings
               WHERE showtime_id = ?
               AND booking_status != 'Cancelled'""",
            (showtime_id,)
        ).fetchall()

    result = set()
    for row in rows:
        if row[0]:
            result.update(x.strip() for x in row[0].split(",") if x.strip())
    return sorted(result)


def make_booking_code(booking_id):
    return f"CINE{datetime.now().strftime('%y%m%d')}{booking_id:04d}"


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    q = request.args.get("q", "").strip().lower()
    theatre_name = request.args.get("theatre", "").strip()
    movies = MOVIES
    if q:
        movies = [
            m for m in MOVIES
            if q in m["title"].lower()
            or q in m["genre"].lower()
            or q in m["language"].lower()
        ]
    selected_theatre = next(
        (theatre for theatre in THEATRES if theatre["name"] == theatre_name), None
    )
    recommended = [UPCOMING_MOVIES[2]] + MOVIES[:5]
    theatre_shows = []
    if selected_theatre:
        theatre_shows = [
            dict(show, movie=movie_by_id(show["movie_id"]))
            for show in SHOWTIMES
        ]
    return render_template(
        "index.html", movies=movies, upcoming=UPCOMING_MOVIES,
        theatres=THEATRES, q=q, city="Bengaluru",
        selected_theatre=selected_theatre, theatre_shows=theatre_shows,
        recommended=recommended
    )


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    movie = movie_by_id(movie_id) or next((item for item in UPCOMING_MOVIES if item["id"] == movie_id), None)
    if not movie:
        return "Movie not found", 404
    movie = dict(movie, **MOVIE_DETAILS.get(movie_id, {
        "cast": "Cast details coming soon", "director": "To be announced",
        "update": "Booking updates will appear here."
    }))
    shows = [s for s in SHOWTIMES if s["movie_id"] == movie_id]
    shows = [dict(show, theatre=THEATRES[index % len(THEATRES)]) for index, show in enumerate(shows)]
    reviews, average_rating = reviews_for_movie(movie_id)
    return render_template(
        "movie.html", movie=movie, shows=shows, reviews=reviews,
        average_rating=average_rating, theatres=THEATRES
    )


@app.route("/actor/<path:actor_name>")
def actor_detail(actor_name):
    actor = ACTOR_DETAILS.get(actor_name)
    if not actor:
        return "Actor not found", 404
    filmography = []
    for movie in MOVIES:
        details = MOVIE_DETAILS.get(movie["id"], {})
        if actor_name in details.get("cast", ""):
            filmography.append(movie)
    if actor_name in MOVIE_DETAILS[103]["cast"]:
        filmography.append(UPCOMING_MOVIES[0])
    return render_template("actor.html", actor=dict(actor, name=actor_name), filmography=filmography)


@app.route("/movie/<int:movie_id>/reviews", methods=["POST"])
def add_review(movie_id):
    movie = movie_by_id(movie_id)
    if not movie:
        return jsonify({"ok": False, "error": "Movie not found."}), 404

    name = (request.form.get("name") or "").strip()
    comment = (request.form.get("comment") or "").strip()
    try:
        rating = int(request.form.get("rating", "0"))
    except ValueError:
        rating = 0

    if not name or not comment or rating not in range(1, 6):
        return redirect(url_for("movie_detail", movie_id=movie_id) + "#reviews")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO reviews (movie_id, name, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
            (movie_id, name, rating, comment, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
    return redirect(url_for("movie_detail", movie_id=movie_id) + "#reviews")


@app.route("/show/<int:showtime_id>")
def seat_selection(showtime_id):
    show = showtime_by_id(showtime_id)
    if not show:
        return "Showtime not found", 404
    movie = movie_by_id(show["movie_id"])
    return render_template(
        "seats.html",
        show=show,
        movie=movie,
        seat_rows=SEAT_ROWS,
        seats_per_row=SEATS_PER_ROW,
        booked=booked_seats(showtime_id),
    )


@app.route("/api/show/<int:showtime_id>/seats")
def seats_api(showtime_id):
    show = showtime_by_id(showtime_id)
    if not show:
        return jsonify({"ok": False, "error": "Show not found"}), 404
    return jsonify({"ok": True, "booked": booked_seats(showtime_id)})


@app.route("/book", methods=["POST"])
def book():
    data = request.get_json(silent=True) or request.form
    try:
        showtime_id = int(data.get("showtime_id"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "Invalid showtime."}), 400

    show = showtime_by_id(showtime_id)
    if not show:
        return jsonify({"ok": False, "error": "Showtime not found."}), 404

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    seats_raw = data.get("seats") or ""
    seats = sorted(set(s.strip().upper() for s in seats_raw.split(",") if s.strip()))

    if not name or not phone or not seats:
        return jsonify({"ok": False, "error": "Name, phone and at least one seat are required."}), 400

    valid = set(all_seats())
    invalid = [s for s in seats if s not in valid]
    if invalid:
        return jsonify({"ok": False, "error": f"Invalid seats: {', '.join(invalid)}"}), 400

    with sqlite3.connect(DB_PATH) as conn:
        current = conn.execute(
            """SELECT seats FROM bookings
               WHERE showtime_id = ?
               AND booking_status != 'Cancelled'""",
            (showtime_id,)
        ).fetchall()
        already_booked = set()
        for row in current:
            already_booked.update(x.strip() for x in row[0].split(",") if x.strip())

        conflicts = sorted(set(seats) & already_booked)
        if conflicts:
            return jsonify({
                "ok": False,
                "error": f"Seat(s) already booked: {', '.join(conflicts)}. Please choose again."
            }), 409

        amount = len(seats) * float(show["price"])
        created_at = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """INSERT INTO bookings
               (booking_code, name, phone, email, showtime_id, movie_id, seats,
                                seat_count, amount, payment_status, booking_status, created_at, updated_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("TEMP", name, phone, email, showtime_id, show["movie_id"],
                         ",".join(seats), len(seats), amount, "Paid", "Confirmed", created_at, created_at)
        )
        booking_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        code = make_booking_code(booking_id)
        conn.execute(
            "UPDATE bookings SET booking_code = ? WHERE id = ?",
            (code, booking_id)
        )
        conn.commit()

    return jsonify({
        "ok": True,
        "message": "Booking confirmed!",
        "booking_code": code,
        "tracking_url": url_for("booking_status", booking_code=code)
    })


@app.route("/booking/<booking_code>")
def booking_status(booking_code):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        booking = conn.execute(
            "SELECT * FROM bookings WHERE booking_code = ?",
            (booking_code.upper(),)
        ).fetchone()

    if not booking:
        return render_template("status.html", booking=None), 404

    booking = dict(booking)
    booking["movie"] = movie_by_id(booking["movie_id"])
    booking["show"] = showtime_by_id(booking["showtime_id"])
    return render_template("status.html", booking=booking)


@app.route("/booking/lookup", methods=["GET", "POST"])
def booking_lookup():
    code = request.values.get("booking_code", "").strip().upper()
    if code:
        return redirect(url_for("booking_status", booking_code=code))
    return render_template("booking_lookup.html")


@app.route("/api/booking/<booking_code>")
def booking_api(booking_code):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT booking_status, payment_status, updated_at FROM bookings WHERE booking_code = ?",
            (booking_code.upper(),)
        ).fetchone()
    if not row:
        return jsonify({"ok": False, "error": "Booking not found."}), 404
    return jsonify({"ok": True, "booking_status": row[0], "payment_status": row[1], "updated_at": row[2]})


@app.route("/booking/<booking_code>/cancel", methods=["POST"])
def cancel_booking(booking_code):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT booking_status FROM bookings WHERE booking_code = ?",
            (booking_code.upper(),)
        ).fetchone()
        if not row:
            return jsonify({"ok": False, "error": "Booking not found."}), 404
        if row[0] == "Cancelled":
            return jsonify({"ok": False, "error": "Booking is already cancelled."}), 400
        conn.execute(
            """UPDATE bookings
               SET booking_status='Cancelled', payment_status='Refund pending',
                   cancelled_at=?, updated_at=?
               WHERE booking_code=?""",
            (datetime.now().isoformat(timespec="seconds"), datetime.now().isoformat(timespec="seconds"), booking_code.upper())
        )
        conn.commit()
    return jsonify({"ok": True, "message": "Booking cancelled. Refund is marked as pending."})


def receipt_text(booking):
    movie = movie_by_id(booking["movie_id"])
    show = showtime_by_id(booking["showtime_id"])
    lines = [
        "CINE BOOKING",
        "--------------------------------",
        f"Booking: {booking['booking_code']}",
        f"Customer: {booking['name']}",
        f"Phone: {booking['phone']}",
        f"Movie: {movie['title']}",
        f"Date: {show['date']}",
        f"Time: {show['time']}",
        f"Screen: {show['screen']} ({show['format']})",
        f"Seats: {booking['seats']}",
        f"Tickets: {booking['seat_count']}",
        f"Amount: INR {booking['amount']:,.0f}",
        f"Payment: {booking['payment_status']}",
        f"Status: {booking['booking_status']}",
        "--------------------------------",
        "Thank you for booking with Cine Booking!",
    ]
    return "\n".join(lines)


@app.route("/booking/<booking_code>/receipt")
def booking_receipt(booking_code):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        booking = conn.execute(
            "SELECT * FROM bookings WHERE booking_code = ?",
            (booking_code.upper(),)
        ).fetchone()
    if not booking:
        return "Booking not found", 404

    # Printable receipt rather than a third-party dependency.
    return Response(
        receipt_text(dict(booking)),
        mimetype="text/plain",
        headers={
            "Content-Disposition":
                f"attachment; filename={booking_code.upper()}-receipt.txt"
        },
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (
            request.form.get("username", "").strip() == ADMIN_USERNAME
            and request.form.get("password", "") == ADMIN_PASSWORD
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Invalid username or password.")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        bookings = conn.execute(
            "SELECT * FROM bookings ORDER BY id DESC"
        ).fetchall()
    bookings = [dict(b) for b in bookings]
    for b in bookings:
        b["movie"] = movie_by_id(b["movie_id"])

    stats = {
        "bookings": len(bookings),
        "tickets": sum(b["seat_count"] for b in bookings if b["booking_status"] != "Cancelled"),
        "revenue": sum(b["amount"] for b in bookings if b["payment_status"] == "Paid"),
        "cancelled": sum(1 for b in bookings if b["booking_status"] == "Cancelled"),
    }
    return render_template("admin.html", bookings=bookings, stats=stats)


@app.route("/admin/bookings/<int:booking_id>/update", methods=["POST"])
@admin_required
def admin_update(booking_id):
    status = request.form.get("booking_status", "Confirmed")
    payment = request.form.get("payment_status", "Paid")
    allowed_status = {"Confirmed", "Cancelled"}
    allowed_payment = {"Paid", "Pending", "Refund pending", "Refunded"}

    if status not in allowed_status or payment not in allowed_payment:
        return redirect(url_for("admin_dashboard"))

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
                """UPDATE bookings SET booking_status=?, payment_status=?, updated_at=?
                    WHERE id=?""",
                (status, payment, datetime.now().isoformat(timespec="seconds"), booking_id)
        )
        conn.commit()
    return redirect(url_for("admin_dashboard") + f"#booking-{booking_id}")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
