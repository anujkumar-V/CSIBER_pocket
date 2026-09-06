import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "csiber_secret_2026_!@#"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp", "doc", "docx", "txt"}

socketio = SocketIO(app, cors_allowed_origins="*")
DB_PATH = os.path.join(os.path.dirname(__file__), "csiber_one.db")

# Ensure uploads folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS posts 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, category TEXT, 
                        message TEXT, timestamp DATETIME, file_url TEXT, helpful INTEGER DEFAULT 0)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS replies 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, author TEXT, 
                        message TEXT, timestamp DATETIME)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS chat_messages 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, message TEXT, timestamp DATETIME)""")


init_db()

# --- ROUTES ---


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/api/timetable")
def get_timetable():
    path = os.path.join(os.path.dirname(__file__), "data", "timetable.json")
    try:
        with open(path, "r") as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify({"error": "Timetable data unavailable"}), 404


@app.route("/api/posts", methods=["GET", "POST"])
def handle_posts():
    if request.method == "POST":
        author = (
            request.form.get("author", "Anonymous Student").strip()
            or "Anonymous Student"
        )
        category = request.form.get("category", "General")
        message = request.form.get("message", "").strip()

        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400

        file_url = None
        if "file" in request.files:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = secure_filename(
                    f"{datetime.now().timestamp()}_{file.filename}"
                )
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                file_url = f"/uploads/{filename}"

        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO posts (author, category, message, timestamp, file_url) VALUES (?, ?, ?, ?, ?)",
                (
                    author,
                    category,
                    message,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    file_url,
                ),
            )
            post_id = cur.lastrowid
        return jsonify({"id": post_id, "status": "success"})

    # GET Posts
    with get_db() as conn:
        posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
        return jsonify([dict(p) for p in posts])


@app.route("/api/posts/<int:post_id>/helpful", methods=["POST"])
def mark_helpful(post_id):
    with get_db() as conn:
        conn.execute("UPDATE posts SET helpful = helpful + 1 WHERE id = ?", (post_id,))
    return jsonify({"status": "success"})


@app.route("/api/hall_of_fame")
def hall_of_fame():
    # Hall of fame logic: Name required. Post=2 pts, Reply=3 pts, Helpful=1 pt.
    query = """
    SELECT author, 
           SUM(post_score) as score,
           SUM(posts_count) as posts_count,
           SUM(helpful_votes) as helpful_votes
    FROM (
        SELECT author, count(*) * 2 as post_score, count(*) as posts_count, sum(helpful) as helpful_votes 
        FROM posts WHERE author != 'Anonymous Student' GROUP BY author
        UNION ALL
        SELECT author, count(*) * 3 as post_score, 0 as posts_count, 0 as helpful_votes 
        FROM replies WHERE author != 'Anonymous Student' GROUP BY author
    )
    GROUP BY author ORDER BY score DESC LIMIT 3
    """
    with get_db() as conn:
        leaders = conn.execute(query).fetchall()
        return jsonify([dict(l) for l in leaders])


@app.route("/api/assistant", methods=["POST"])
def assistant():
    data = request.json
    query = data.get("query", "").lower()
    path = os.path.join(os.path.dirname(__file__), "data", "knowledge.json")

    try:
        with open(path, "r") as f:
            kb = json.load(f)
            for item in kb:
                if any(kw in query for kw in item["keywords"]):
                    return jsonify({"response": item["answer"]})
    except:
        pass

    return jsonify(
        {
            "response": "I’m CSIBER Assistant. I only answer CSIBER-related questions. Please rephrase or ask about admissions, timetable, or BCA/MCA structure."
        }
    )


# --- SOCKET.IO CHAT ---


@socketio.on("connect")
def handle_connect():
    with get_db() as conn:
        messages = conn.execute(
            "SELECT * FROM chat_messages ORDER BY id DESC LIMIT 50"
        ).fetchall()
        emit("chat_history", [dict(m) for m in reversed(messages)])


@socketio.on("send_message")
def handle_message(data):
    author = data.get("author", "Anonymous").strip() or "Anonymous"
    message = data.get("message", "").strip()
    if message:
        timestamp = datetime.now().strftime("%I:%M %p")
        with get_db() as conn:
            conn.execute(
                "INSERT INTO chat_messages (author, message, timestamp) VALUES (?, ?, ?)",
                (author, message, timestamp),
            )
        emit(
            "new_message",
            {"author": author, "message": message, "timestamp": timestamp},
            broadcast=True,
        )


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
