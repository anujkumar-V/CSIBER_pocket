from flask import Flask, request, jsonify, render_template_string, session
import sqlite3
import os
import uuid
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename

# =========================================================
# CSIBER//ONE
# Single-file premium student utility platform
# Architected by Anuj Gupta — BCA • CSIBER
# =========================================================

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_CSIBER_ONE_SECRET"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "csiber_one.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp", "doc", "docx", "txt"}


# =========================================================
# DATABASE
# =========================================================


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    con = db()

    con.executescript("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'General',
            message TEXT NOT NULL,
            attachment TEXT,
            helpful INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            message TEXT NOT NULL,
            helpful INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_id INTEGER NOT NULL,
            UNIQUE(visitor_id, target_type, target_id)
        );
    """)

    con.commit()
    con.close()


init_db()


# =========================================================
# HELPERS
# =========================================================


def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def visitor_id():
    if "visitor_id" not in session:
        session["visitor_id"] = str(uuid.uuid4())
    return session["visitor_id"]


def clean_name(name):
    name = (name or "").strip()
    return name[:60] if name else "Anonymous Student"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def fmt_time(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime(
            "%d %b %Y • %I:%M %p"
        )
    except Exception:
        return value


# =========================================================
# PREMIUM FRONTEND
# =========================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>CSIBER//ONE — Student OS</title>

<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap'
);

:root{
    --bg:#030409;
    --panel:rgba(255,255,255,.055);
    --panel2:rgba(255,255,255,.085);
    --border:rgba(255,255,255,.11);
    --text:#f7f9ff;
    --muted:#8993a7;
    --blue:#6e8cff;
    --cyan:#5ee7ff;
    --green:#55e6a5;
    --yellow:#ffd66b;
    --red:#ff7187;
    --purple:#a678ff;
}

*{
    box-sizing:border-box;
}

html{
    scroll-behavior:smooth;
}

body{
    margin:0;
    color:var(--text);
    background:
        radial-gradient(
            circle at 15% 0%,
            rgba(89,112,255,.20),
            transparent 27%
        ),
        radial-gradient(
            circle at 85% 8%,
            rgba(60,218,255,.13),
            transparent 25%
        ),
        radial-gradient(
            circle at 50% 65%,
            rgba(146,83,255,.08),
            transparent 32%
        ),
        var(--bg);
    font-family:Inter,sans-serif;
    min-height:100vh;
    overflow-x:hidden;
}

body:before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    background-image:
        linear-gradient(
            rgba(255,255,255,.022) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,.022) 1px,
            transparent 1px
        );
    background-size:70px 70px;
    mask-image:linear-gradient(
        to bottom,
        black,
        transparent 85%
    );
}

/* 3D ORB */

.orb{
    position:fixed;
    width:420px;
    height:420px;
    border-radius:50%;
    right:-180px;
    top:130px;
    pointer-events:none;
    opacity:.45;
    background:
        radial-gradient(
            circle at 35% 30%,
            rgba(110,145,255,.30),
            transparent 28%
        ),
        radial-gradient(
            circle at 70% 65%,
            rgba(75,225,255,.22),
            transparent 30%
        ),
        rgba(80,100,255,.03);
    filter:blur(1px);
    box-shadow:
        inset -30px -30px 80px rgba(0,0,0,.6),
        0 0 120px rgba(90,110,255,.10);
    animation:floatOrb 8s ease-in-out infinite;
}

@keyframes floatOrb{
    0%,100%{
        transform:translateY(0) rotate(0deg);
    }
    50%{
        transform:translateY(-25px) rotate(8deg);
    }
}

/* NAV */

nav{
    position:sticky;
    top:0;
    z-index:100;
    backdrop-filter:blur(22px);
    background:rgba(3,4,9,.72);
    border-bottom:1px solid rgba(255,255,255,.07);
}

.nav{
    width:min(1200px,calc(100% - 30px));
    margin:auto;
    height:72px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.brand{
    display:flex;
    align-items:center;
    gap:11px;
    font-family:"Plus Jakarta Sans";
    font-weight:800;
}

.logo{
    width:38px;
    height:38px;
    display:grid;
    place-items:center;
    border-radius:12px;
    color:#020308;
    background:
        linear-gradient(
            135deg,
            white,
            #8eb4ff
        );
    box-shadow:
        0 0 35px rgba(110,150,255,.25);
    font-size:11px;
}

.brand span{
    color:#8893a7;
}

.nav-credit{
    font-size:10px;
    letter-spacing:1px;
    color:#9ba5b8;
    border:1px solid var(--border);
    background:rgba(255,255,255,.035);
    padding:9px 13px;
    border-radius:999px;
}

.nav-credit b{
    color:#fff;
}

/* HERO */

.hero{
    width:min(1200px,calc(100% - 30px));
    margin:auto;
    min-height:650px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    position:relative;
}

.hero-content{
    max-width:900px;
}

.eyebrow{
    display:inline-flex;
    gap:8px;
    align-items:center;
    border:1px solid var(--border);
    background:rgba(255,255,255,.035);
    padding:9px 14px;
    border-radius:999px;
    font-size:10px;
    font-weight:800;
    letter-spacing:1.5px;
    color:#aeb7c9;
}

.green-dot{
    width:7px;
    height:7px;
    border-radius:50%;
    background:var(--green);
    box-shadow:0 0 14px var(--green);
}

.hero h1{
    margin:25px 0 18px;
    font-family:"Plus Jakarta Sans";
    font-size:clamp(48px,8vw,100px);
    line-height:.92;
    letter-spacing:-6px;
}

.gradient{
    background:
        linear-gradient(
            110deg,
            #ffffff 10%,
            #a8c8ff 50%,
            #5fe4ff 90%
        );
    color:transparent;
    -webkit-background-clip:text;
    background-clip:text;
}

.hero p{
    color:var(--muted);
    max-width:680px;
    margin:auto;
    line-height:1.8;
    font-size:16px;
}

.builder{
    margin-top:30px;
    display:inline-flex;
    flex-direction:column;
    gap:5px;
    padding:15px 20px;
    border-radius:16px;
    background:rgba(255,255,255,.035);
    border:1px solid var(--border);
    box-shadow:
        0 20px 70px rgba(0,0,0,.25);
}

.builder small{
    font-size:8px;
    letter-spacing:2px;
    color:#6e788b;
    font-weight:800;
}

.builder strong{
    font-size:14px;
}

/* CONTAINER */

.container{
    width:min(1200px,calc(100% - 30px));
    margin:auto;
}

.section{
    padding:75px 0;
}

.section-title{
    margin-bottom:27px;
}

.section-title h2{
    margin:0;
    font-family:"Plus Jakarta Sans";
    font-size:32px;
    letter-spacing:-1.4px;
}

.section-title p{
    color:var(--muted);
    font-size:13px;
    margin:8px 0 0;
}

/* GRID */

.grid{
    display:grid;
    grid-template-columns:repeat(12,1fr);
    gap:18px;
}

.col6{
    grid-column:span 6;
}

.col12{
    grid-column:span 12;
}

/* CARD */

.card{
    position:relative;
    overflow:hidden;
    padding:27px;
    border-radius:25px;
    border:1px solid var(--border);
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.075),
            rgba(255,255,255,.025)
        );
    backdrop-filter:blur(20px);
    box-shadow:
        0 25px 80px rgba(0,0,0,.35);
    transition:
        transform .3s,
        border .3s,
        box-shadow .3s;
}

.card:hover{
    transform:translateY(-3px);
    border-color:rgba(255,255,255,.17);
    box-shadow:
        0 30px 100px rgba(0,0,0,.45),
        0 0 50px rgba(90,120,255,.035);
}

.card:after{
    content:"";
    position:absolute;
    width:200px;
    height:200px;
    top:-110px;
    right:-90px;
    border-radius:50%;
    background:radial-gradient(
        circle,
        rgba(110,145,255,.14),
        transparent 70%
    );
    pointer-events:none;
}

.icon{
    width:45px;
    height:45px;
    display:grid;
    place-items:center;
    border-radius:14px;
    border:1px solid var(--border);
    background:rgba(255,255,255,.055);
    margin-bottom:18px;
    font-weight:800;
}

.card h3{
    font-family:"Plus Jakarta Sans";
    margin:0 0 8px;
    font-size:20px;
}

.desc{
    color:var(--muted);
    font-size:13px;
    line-height:1.65;
    margin-bottom:21px;
}

/* INPUTS */

input,
textarea,
select{
    width:100%;
    color:#fff;
    background:rgba(0,0,0,.25);
    border:1px solid rgba(255,255,255,.09);
    border-radius:13px;
    outline:none;
    padding:13px 14px;
    transition:.2s;
}

input:focus,
textarea:focus,
select:focus{
    border-color:rgba(105,145,255,.65);
    box-shadow:0 0 0 4px rgba(105,145,255,.07);
}

select option{
    background:#080a10;
}

textarea{
    min-height:110px;
    resize:vertical;
}

.form{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
}

.full{
    grid-column:1/-1;
}

button{
    font-family:Inter;
}

.btn{
    border:0;
    cursor:pointer;
    border-radius:13px;
    padding:13px 17px;
    font-weight:800;
    transition:.2s;
}

.btn:hover{
    transform:translateY(-2px);
}

.primary{
    color:#05060a;
    background:
        linear-gradient(
            135deg,
            #ffffff,
            #a9c8ff
        );
    box-shadow:0 10px 35px rgba(110,150,255,.12);
}

.secondary{
    color:white;
    background:rgba(255,255,255,.055);
    border:1px solid var(--border);
}

/* ATTENDANCE */

.attendance-box{
    margin-top:15px;
    padding:20px;
    border-radius:18px;
    background:rgba(255,255,255,.04);
    border:1px solid var(--border);
}

.big{
    font-size:34px;
    font-weight:800;
    font-family:"Plus Jakarta Sans";
}

.status{
    display:inline-flex;
    padding:7px 10px;
    border-radius:999px;
    margin-top:9px;
    font-size:10px;
    font-weight:900;
    letter-spacing:1px;
}

.safe{
    background:rgba(85,230,165,.1);
    color:var(--green);
    border:1px solid rgba(85,230,165,.18);
}

.caution{
    background:rgba(255,214,107,.1);
    color:var(--yellow);
    border:1px solid rgba(255,214,107,.18);
}

.danger{
    background:rgba(255,113,135,.1);
    color:var(--red);
    border:1px solid rgba(255,113,135,.18);
}

.stat-grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:9px;
    margin-top:17px;
}

.stat{
    padding:13px;
    border-radius:13px;
    background:rgba(255,255,255,.035);
}

.stat b{
    display:block;
    font-size:18px;
}

.stat span{
    display:block;
    color:#737e91;
    font-size:9px;
    margin-top:4px;
}

/* ALERT */

.alert{
    margin-top:12px;
    padding:12px;
    border-radius:12px;
    font-size:12px;
    line-height:1.5;
}

/* GPA */

.subjects{
    display:grid;
    gap:8px;
}

.subject-row{
    display:grid;
    grid-template-columns:1fr 1fr 42px;
    gap:7px;
}

.remove{
    cursor:pointer;
    border:1px solid rgba(255,255,255,.08);
    border-radius:12px;
    color:#aab3c2;
    background:rgba(255,255,255,.035);
}

.gpa-result{
    margin-top:15px;
    padding:18px;
    border:1px solid var(--border);
    border-radius:17px;
    background:rgba(255,255,255,.04);
}

/* AI */

.ai-shell{
    position:relative;
}

.ai-glow{
    position:absolute;
    inset:-100px;
    background:radial-gradient(
        circle at center,
        rgba(105,125,255,.10),
        transparent 50%
    );
    pointer-events:none;
}

.chat{
    height:420px;
    overflow-y:auto;
    display:flex;
    flex-direction:column;
    gap:11px;
    padding:5px;
}

.msg{
    max-width:82%;
    padding:13px 15px;
    border-radius:16px;
    font-size:13px;
    line-height:1.6;
}

.bot{
    align-self:flex-start;
    background:rgba(255,255,255,.055);
    border:1px solid var(--border);
}

.user{
    align-self:flex-end;
    background:
        linear-gradient(
            135deg,
            rgba(96,126,255,.35),
            rgba(68,210,255,.16)
        );
    border:1px solid rgba(115,150,255,.2);
}

.chat-input{
    display:grid;
    grid-template-columns:1fr auto;
    gap:8px;
    margin-top:10px;
}

/* PYQ */

.coming{
    min-height:210px;
    display:grid;
    place-items:center;
    text-align:center;
}

.lock{
    font-size:38px;
}

.pill{
    display:inline-block;
    margin-top:10px;
    padding:7px 11px;
    border:1px solid var(--border);
    border-radius:999px;
    font-size:9px;
    letter-spacing:1.5px;
    font-weight:900;
    color:#9ca6b9;
}

/* CONNECT */

.post-list{
    display:grid;
    gap:13px;
}

.post{
    padding:21px;
    border:1px solid var(--border);
    border-radius:20px;
    background:rgba(255,255,255,.035);
}

.post-head{
    display:flex;
    justify-content:space-between;
    gap:10px;
}

.author{
    display:flex;
    gap:10px;
    align-items:center;
}

.avatar{
    width:38px;
    height:38px;
    display:grid;
    place-items:center;
    border-radius:12px;
    color:#05060a;
    font-weight:900;
    background:
        linear-gradient(
            135deg,
            #7186ff,
            #62e4ff
        );
}

.author b{
    display:block;
    font-size:12px;
}

.time{
    color:#6d7789;
    font-size:9px;
    margin-top:3px;
}

.category{
    height:max-content;
    padding:6px 9px;
    border:1px solid var(--border);
    border-radius:999px;
    color:#9fa9bc;
    font-size:9px;
}

.message{
    white-space:pre-wrap;
    line-height:1.7;
    color:#d8deea;
    font-size:13px;
    margin:16px 0;
}

.file{
    display:inline-block;
    padding:9px 11px;
    border-radius:10px;
    background:rgba(255,255,255,.05);
    border:1px solid var(--border);
    font-size:10px;
    color:#bcd1ff;
    margin-bottom:12px;
}

.actions{
    display:flex;
    gap:7px;
}

.small{
    cursor:pointer;
    color:#aeb8ca;
    background:rgba(255,255,255,.035);
    border:1px solid var(--border);
    border-radius:10px;
    padding:8px 10px;
    font-size:10px;
}

.replies{
    margin-top:15px;
    margin-left:20px;
    padding-left:16px;
    border-left:1px solid rgba(255,255,255,.09);
    display:grid;
    gap:8px;
}

.reply{
    padding:11px;
    border-radius:12px;
    background:rgba(255,255,255,.025);
}

.reply b{
    font-size:10px;
}

.reply p{
    color:#aeb8c9;
    font-size:11px;
    white-space:pre-wrap;
}

.reply-form{
    display:grid;
    grid-template-columns:160px 1fr auto;
    gap:7px;
    margin-top:8px;
}

/* HALL */

.hall{
    display:grid;
    grid-template-columns:1.4fr 1fr 1fr;
    gap:14px;
}

.hall-card{
    min-height:190px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}

.hall-card:first-child{
    background:
        radial-gradient(
            circle at 80% 20%,
            rgba(255,214,107,.14),
            transparent 35%
        ),
        rgba(255,255,255,.045);
}

.rank{
    color:#737e91;
    font-size:9px;
    font-weight:900;
    letter-spacing:1.5px;
}

.hall-name{
    font-family:"Plus Jakarta Sans";
    font-size:23px;
    font-weight:800;
}

.score{
    color:#8d98ab;
    font-size:11px;
    margin-top:5px;
}

/* FOOTER */

footer{
    margin-top:50px;
    padding:80px 0 40px;
    border-top:1px solid rgba(255,255,255,.07);
}

.footer-logo{
    font-family:"Plus Jakarta Sans";
    font-size:32px;
    font-weight:800;
}

.footer-sub{
    color:#697488;
    font-size:12px;
    margin:7px 0 32px;
}

.creator{
    display:inline-flex;
    flex-direction:column;
    gap:5px;
    padding:20px 24px;
    border:1px solid var(--border);
    border-radius:17px;
    background:rgba(255,255,255,.025);
}

.creator span{
    color:#626d80;
    font-size:8px;
    letter-spacing:2px;
    font-weight:900;
}

.creator strong{
    font-size:17px;
}

.copy{
    margin-top:32px;
    color:#4e586a;
    font-size:10px;
}

/* TOAST */

#toast{
    position:fixed;
    bottom:20px;
    right:20px;
    z-index:999;
    padding:13px 17px;
    border-radius:13px;
    border:1px solid var(--border);
    background:rgba(12,15,22,.94);
    box-shadow:0 20px 70px rgba(0,0,0,.45);
    font-size:11px;
    transform:translateY(100px);
    opacity:0;
    transition:.3s;
}

#toast.show{
    transform:translateY(0);
    opacity:1;
}

/* MOBILE */

@media(max-width:800px){

    .nav-credit{
        display:none;
    }

    .hero{
        min-height:570px;
    }

    .hero h1{
        letter-spacing:-3px;
    }

    .col6,
    .col12{
        grid-column:span 12;
    }

    .form{
        grid-template-columns:1fr;
    }

    .full{
        grid-column:auto;
    }

    .stat-grid{
        grid-template-columns:1fr;
    }

    .hall{
        grid-template-columns:1fr;
    }

    .reply-form{
        grid-template-columns:1fr;
    }

    .subject-row{
        grid-template-columns:1fr 1fr;
    }

    .remove{
        grid-column:1/-1;
        padding:9px;
    }
}

</style>

</head>


<body>

<div class="orb"></div>


<!-- =====================================================
     NAV
====================================================== -->

<nav>

<div class="nav">

    <a class="brand" href="#top">

        <div class="logo">
            AG
        </div>

        <div>
            CSIBER<span>//ONE</span>
        </div>

    </a>

    <div class="nav-credit">
        ARCHITECTED BY <b>ANUJ GUPTA</b>
    </div>

</div>

</nav>


<!-- =====================================================
     HERO
====================================================== -->

<header class="hero" id="top">

<div class="hero-content">

    <div class="eyebrow">
        <span class="green-dot"></span>
        CSIBER STUDENT OS • 2026
    </div>

    <h1>
        Your college.<br>
        <span class="gradient">
            One intelligent layer.
        </span>
    </h1>

    <p>
        Attendance intelligence, SGPA/CGPA tools,
        CSIBER Assistant, student conversations,
        academic resources and more — in one premium space.
    </p>

    <div class="builder">

        <small>✦ ARCHITECTED BY</small>

        <strong>
            ANUJ GUPTA — BCA • CSIBER
        </strong>

    </div>

</div>

</header>


<main class="container">


<!-- =====================================================
     ATTENDANCE + GPA
====================================================== -->

<section class="section">

<div class="section-title">

    <h2>Academic Intelligence</h2>

    <p>
        Don't calculate manually. Let CSIBER//ONE do the math.
    </p>

</div>


<div class="grid">


<!-- ATTENDANCE -->

<div class="card col6">

    <div class="icon">◒</div>

    <h3>Leave & Attendance Guard</h3>

    <p class="desc">
        Student ko lectures count karne ki zarurat nahi.
        Working days, holidays aur apni leave enter karo.
        System 80% safety aur 75% minimum threshold dono check karega.
    </p>


    <div class="form">

        <input
            id="calendarDays"
            type="number"
            min="1"
            placeholder="Total calendar days"
        >

        <input
            id="weeklyOffs"
            type="number"
            min="0"
            placeholder="Weekly-off days"
        >

        <input
            id="holidays"
            type="number"
            min="0"
            placeholder="College holidays"
        >

        <input
            id="leaves"
            type="number"
            min="0"
            placeholder="Your leave days"
        >

        <button
            class="btn primary full"
            onclick="calculateLeave()"
        >
            Check My Attendance
        </button>

    </div>


    <div id="attendanceOutput"></div>

</div>


<!-- GPA -->

<div class="card col6">

    <div class="icon">Σ</div>

    <h3>SGPA / CGPA Engine</h3>

    <p class="desc">
        Subject credits + grade points se SGPA.
        Multiple semester SGPA + semester credits se CGPA.
    </p>


    <div class="subjects" id="subjects">

        <div class="subject-row">

            <input
                class="credit"
                type="number"
                step=".5"
                placeholder="Credits"
            >

            <input
                class="grade"
                type="number"
                step=".1"
                min="0"
                max="10"
                placeholder="Grade point"
            >

            <button
                class="remove"
                onclick="this.parentElement.remove()"
            >
                ×
            </button>

        </div>

    </div>


    <div style="display:flex;gap:8px;margin-top:10px">

        <button
            class="btn secondary"
            onclick="addSubject()"
        >
            + Subject
        </button>

        <button
            class="btn primary"
            onclick="calculateSGPA()"
        >
            SGPA
        </button>

    </div>


    <div id="gpaOutput"></div>


    <hr style="
        border:0;
        border-top:1px solid rgba(255,255,255,.07);
        margin:24px 0;
    ">


    <h3 style="font-size:15px">
        CGPA Calculator
    </h3>

    <p class="desc">
        Har semester ka SGPA aur uske total credits enter karo.
    </p>


    <div id="semesters">

        <div class="subject-row">

            <input
                class="semCredit"
                type="number"
                step=".5"
                placeholder="Semester credits"
            >

            <input
                class="semSGPA"
                type="number"
                step=".01"
                min="0"
                max="10"
                placeholder="SGPA"
            >

            <button
                class="remove"
                onclick="this.parentElement.remove()"
            >
                ×
            </button>

        </div>

    </div>


    <div style="display:flex;gap:8px;margin-top:10px">

        <button
            class="btn secondary"
            onclick="addSemester()"
        >
            + Semester
        </button>

        <button
            class="btn primary"
            onclick="calculateCGPA()"
        >
            CGPA
        </button>

    </div>


    <div id="cgpaOutput"></div>

</div>

</div>

</section>


<!-- =====================================================
     AI ASSISTANT
====================================================== -->

<section class="section">

<div class="section-title">

    <h2>CSIBER Assistant</h2>

    <p>
        A focused assistant designed to answer CSIBER-related questions.
    </p>

</div>


<div class="card ai-shell">

<div class="ai-glow"></div>


<div class="chat" id="chat">

    <div class="msg bot">

        👋 Hi! I'm <b>CSIBER Assistant</b>.<br><br>

        I can help with CSIBER-specific information,
        BCA basics, programme structure, admission-related
        information and this student utility platform.

        <br><br>

        <b>Try:</b><br>
        • BCA kitne years ka hai?<br>
        • CSIBER BCA kya hai?<br>
        • Admission eligibility kya hai?<br>
        • SGPA kaise calculate hota hai?

    </div>

</div>


<div class="chat-input">

    <input
        id="aiQuestion"
        placeholder="Ask a CSIBER question..."
        onkeydown="if(event.key==='Enter') askAI()"
    >

    <button
        class="btn primary"
        onclick="askAI()"
    >
        Ask
    </button>

</div>

</div>

</section>


<!-- =====================================================
     PYQ
====================================================== -->

<section class="section">

<div class="section-title">

    <h2>Academic Vault</h2>

    <p>
        More academic tools are being added.
    </p>

</div>


<div class="grid">

<div class="card col6 coming">

    <div>

        <div class="lock">⌁</div>

        <h3>PYQ Vault</h3>

        <p class="desc">
            Subject-wise previous year papers,
            searchable and organised.
        </p>

        <span class="pill">
            COMING SOON
        </span>

    </div>

</div>


<div class="card col6 coming">

    <div>

        <div class="lock">◈</div>

        <h3>Smart Timetable</h3>

        <p class="desc">
            Daily classes, room information,
            reminders and quick navigation.
        </p>

        <span class="pill">
            COMING SOON
        </span>

    </div>

</div>

</div>

</section>


<!-- =====================================================
     CLASS CONNECT
====================================================== -->

<section class="section">

<div class="section-title">

    <h2>Class Connect</h2>

    <p>
        Name optional. If entered, everyone can see it.
        Students can post multiple times and reply.
    </p>

</div>


<div class="card">

    <div class="form">

        <input
            id="postName"
            placeholder="Your name (optional)"
            maxlength="60"
        >

        <select id="postCategory">

            <option>General</option>
            <option>Academic</option>
            <option>Exam</option>
            <option>Attendance</option>
            <option>Notes</option>
            <option>Help</option>
            <option>Notice</option>

        </select>

        <textarea
            id="postMessage"
            class="full"
            maxlength="2000"
            placeholder="Ask a question, share something useful, or help another student..."
        ></textarea>

        <input
            id="postFile"
            class="full"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.webp,.doc,.docx,.txt"
        >

    </div>


    <button
        class="btn primary"
        style="margin-top:10px"
        onclick="createPost()"
    >
        Publish
    </button>

</div>


<div
    id="posts"
    class="post-list"
    style="margin-top:17px"
>
</div>

</section>


<!-- =====================================================
     HALL OF FAME
====================================================== -->

<section class="section">

<div class="section-title">

    <h2>Hall of Fame</h2>

    <p>
        Automatic weekly ranking based on contributions + helpful votes.
    </p>

</div>


<div
    id="hall"
    class="hall"
>
</div>

</section>


</main>


<!-- =====================================================
     FOOTER
====================================================== -->

<footer>

<div class="container">

    <div class="footer-logo">
        CSIBER//ONE
    </div>

    <div class="footer-sub">
        A student-built digital utility layer for CSIBER.
    </div>

    <div class="creator">

        <span>ARCHITECTED BY</span>

        <strong>ANUJ GUPTA</strong>

        <span>BCA • CSIBER</span>

    </div>

    <div class="copy">
        © 2026 CSIBER//ONE • Built for students.
    </div>

</div>

</footer>


<div id="toast"></div>


<script>

/* ========================================================
   TOAST
======================================================== */

function toast(text){

    const t=document.getElementById("toast");

    t.innerText=text;

    t.classList.add("show");

    setTimeout(()=>{
        t.classList.remove("show");
    },2500);
}


/* ========================================================
   ATTENDANCE / LEAVE ENGINE
======================================================== */

function calculateLeave(){

    const calendar=
        Number(document.getElementById("calendarDays").value);

    const weekly=
        Number(document.getElementById("weeklyOffs").value);

    const holidays=
        Number(document.getElementById("holidays").value);

    const leaves=
        Number(document.getElementById("leaves").value);


    const output=
        document.getElementById("attendanceOutput");


    if(calendar<=0){

        output.innerHTML=`
            <div class="attendance-box">
                Enter total calendar days.
            </div>
        `;

        return;
    }


    if(weekly<0 || holidays<0 || leaves<0){

        output.innerHTML=`
            <div class="attendance-box">
                Values cannot be negative.
            </div>
        `;

        return;
    }


    const working=
        calendar-weekly-holidays;


    if(working<=0){

        output.innerHTML=`
            <div class="attendance-box">
                Working days must be greater than zero.
            </div>
        `;

        return;
    }


    if(leaves>working){

        output.innerHTML=`
            <div class="attendance-box">
                Leave days cannot be greater than working days.
            </div>
        `;

        return;
    }


    const present=
        working-leaves;


    const percentage=
        (present/working)*100;


    /*
       Two important thresholds:

       80% = safe zone
       75% = minimum warning zone
    */


    let status="";
    let statusClass="";
    let message="";


    if(percentage>=80){

        status="SAFE";
        statusClass="safe";

        const safeLeaves=
            Math.floor(
                (present-(0.80*working))/0.80
            );

        message=
            `You can still take approximately
             <b>${Math.max(0,safeLeaves)}</b>
             more working-day leave(s) and stay at 80%+.`;

    }
    else if(percentage>=75){

        status="CAUTION";
        statusClass="caution";

        const reach80=
            Math.ceil(
                (0.80*working-present)/0.20
            );

        message=
            `⚠ You are below the 80% safe zone.
             Attend approximately
             <b>${Math.max(0,reach80)}</b>
             consecutive working day(s)
             to reach 80%.`;

    }
    else{

        status="DANGER";
        statusClass="danger";

        const reach75=
            Math.ceil(
                (0.75*working-present)/0.25
            );

        message=
            `🚨 Attendance is below 75%.
             You need approximately
             <b>${Math.max(0,reach75)}</b>
             consecutive working day(s)
             to reach 75%.`;
    }


    output.innerHTML=`

        <div class="attendance-box">

            <div class="big">
                ${percentage.toFixed(2)}%
            </div>

            <div class="status ${statusClass}">
                ${status}
            </div>


            <div class="stat-grid">

                <div class="stat">
                    <b>${working}</b>
                    <span>WORKING DAYS</span>
                </div>

                <div class="stat">
                    <b>${present}</b>
                    <span>PRESENT</span>
                </div>

                <div class="stat">
                    <b>${leaves}</b>
                    <span>LEAVE</span>
                </div>

            </div>


            <div
                class="alert ${statusClass}"
                style="margin-top:15px"
            >
                ${message}
            </div>

        </div>
    `;
}


/* ========================================================
   SGPA
======================================================== */

function addSubject(){

    const box=document.getElementById("subjects");

    const row=document.createElement("div");

    row.className="subject-row";

    row.innerHTML=`

        <input
            class="credit"
            type="number"
            step=".5"
            placeholder="Credits"
        >

        <input
            class="grade"
            type="number"
            step=".1"
            min="0"
            max="10"
            placeholder="Grade point"
        >

        <button
            class="remove"
            onclick="this.parentElement.remove()"
        >
            ×
        </button>

    `;

    box.appendChild(row);
}


async function calculateSGPA(){

    const credits=[
        ...document.querySelectorAll(".credit")
    ].map(x=>Number(x.value));


    const grades=[
        ...document.querySelectorAll(".grade")
    ].map(x=>Number(x.value));


    try{

        const r=await fetch(
            "/api/sgpa",
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    credits,
                    grades
                })
            }
        );


        const data=await r.json();


        if(!r.ok){
            throw new Error(data.error);
        }


        document.getElementById("gpaOutput").innerHTML=`

            <div class="gpa-result">

                <div class="big">
                    ${data.sgpa}
                </div>

                <div style="
                    color:#7e899c;
                    font-size:10px;
                    margin-top:5px
                ">
                    SEMESTER GRADE POINT AVERAGE
                </div>

            </div>
        `;

    }
    catch(e){

        toast(e.message);
    }
}


/* ========================================================
   CGPA
======================================================== */

function addSemester(){

    const box=document.getElementById("semesters");

    const row=document.createElement("div");

    row.className="subject-row";

    row.innerHTML=`

        <input
            class="semCredit"
            type="number"
            step=".5"
            placeholder="Semester credits"
        >

        <input
            class="semSGPA"
            type="number"
            step=".01"
            min="0"
            max="10"
            placeholder="SGPA"
        >

        <button
            class="remove"
            onclick="this.parentElement.remove()"
        >
            ×
        </button>

    `;

    box.appendChild(row);
}


async function calculateCGPA(){

    const credits=[
        ...document.querySelectorAll(".semCredit")
    ].map(x=>Number(x.value));


    const sgpas=[
        ...document.querySelectorAll(".semSGPA")
    ].map(x=>Number(x.value));


    try{

        const r=await fetch(
            "/api/cgpa",
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    credits,
                    sgpas
                })
            }
        );


        const data=await r.json();


        if(!r.ok){
            throw new Error(data.error);
        }


        document.getElementById("cgpaOutput").innerHTML=`

            <div class="gpa-result">

                <div class="big">
                    ${data.cgpa}
                </div>

                <div style="
                    color:#7e899c;
                    font-size:10px;
                    margin-top:5px
                ">
                    CUMULATIVE GRADE POINT AVERAGE
                </div>

                <div style="
                    margin-top:12px;
                    color:#aab4c6;
                    font-size:11px
                ">
                    Grade band:
                    <b>${data.grade_band}</b>
                </div>

            </div>

        `;

    }
    catch(e){

        toast(e.message);
    }
}


/* ========================================================
   CSIBER ASSISTANT
======================================================== */

async function askAI(){

    const input=document.getElementById("aiQuestion");

    const question=input.value.trim();

    if(!question) return;


    addChat(question,"user");

    input.value="";


    const thinking=addChat(
        "Thinking about CSIBER information…",
        "bot"
    );


    try{

        const r=await fetch(
            "/api/csiber-assistant",
            {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    question
                })
            }
        );


        const data=await r.json();


        thinking.remove();

        addChat(
            data.answer,
            "bot"
        );

    }
    catch(e){

        thinking.remove();

        addChat(
            "I could not process that right now.",
            "bot"
        );
    }
}


function addChat(text,type){

    const chat=document.getElementById("chat");

    const msg=document.createElement("div");

    msg.className="msg "+type;

    msg.innerHTML=escapeHTML(text)
        .replace(/\n/g,"<br>");

    chat.appendChild(msg);

    chat.scrollTop=chat.scrollHeight;

    return msg;
}


/* ========================================================
   CLASS CONNECT
======================================================== */

async function createPost(){

    const name=
        document.getElementById("postName").value.trim();

    const category=
        document.getElementById("postCategory").value;

    const message=
        document.getElementById("postMessage").value.trim();

    const file=
        document.getElementById("postFile").files[0];


    if(!message){

        toast("Write something first.");

        return;
    }


    const form=new FormData();

    form.append("name",name);
    form.append("category",category);
    form.append("message",message);

    if(file){
        form.append("file",file);
    }


    const r=await fetch(
        "/api/posts",
        {
            method:"POST",
            body:form
        }
    );


    const data=await r.json();


    if(!r.ok){

        toast(data.error);

        return;
    }


    document.getElementById("postName").value="";
    document.getElementById("postMessage").value="";
    document.getElementById("postFile").value="";


    toast("Published.");

    loadPosts();
    loadHall();
}


async function loadPosts(){

    const box=document.getElementById("posts");

    try{

        const r=await fetch("/api/posts");

        const data=await r.json();


        if(!data.posts.length){

            box.innerHTML=`
                <div class="card">
                    No conversations yet.
                    Be the first student to start one.
                </div>
            `;

            return;
        }


        box.innerHTML=
            data.posts.map(renderPost).join("");

    }
    catch(e){

        box.innerHTML=`
            <div class="card">
                Could not load Class Connect.
            </div>
        `;
    }
}


function renderPost(post){

    const letter=
        post.name.charAt(0).toUpperCase();


    const file=post.attachment
        ? `
            <a
                class="file"
                href="${post.attachment}"
                target="_blank"
            >
                ↗ ${escapeHTML(post.attachment_name)}
            </a>
        `
        : "";


    const replies=(post.replies||[])
        .map(reply=>`

            <div class="reply">

                <b>
                    ${escapeHTML(reply.name)}
                </b>

                <p>
                    ${escapeHTML(reply.message)}
                </p>

                <button
                    class="small"
                    onclick="helpful('reply',${reply.id})"
                >
                    ♥ ${reply.helpful}
                </button>

            </div>

        `)
        .join("");


    return `

        <article class="post">

            <div class="post-head">

                <div class="author">

                    <div class="avatar">
                        ${escapeHTML(letter)}
                    </div>

                    <div>

                        <b>
                            ${escapeHTML(post.name)}
                        </b>

                        <div class="time">
                            ${escapeHTML(post.created_at)}
                        </div>

                    </div>

                </div>


                <div class="category">
                    ${escapeHTML(post.category)}
                </div>

            </div>


            <div class="message">
                ${escapeHTML(post.message)}
            </div>


            ${file}


            <div class="actions">

                <button
                    class="small"
                    onclick="helpful('post',${post.id})"
                >
                    ♥ Helpful ${post.helpful}
                </button>

            </div>


            <div class="replies">

                ${replies}


                <div class="reply-form">

                    <input
                        id="replyName${post.id}"
                        placeholder="Your name (optional)"
                        maxlength="60"
                    >

                    <input
                        id="replyMsg${post.id}"
                        placeholder="Write a reply..."
                        maxlength="1000"
                    >

                    <button
                        class="btn secondary"
                        onclick="replyPost(${post.id})"
                    >
                        Reply
                    </button>

                </div>

            </div>

        </article>

    `;
}


async function replyPost(id){

    const name=
        document.getElementById(
            "replyName"+id
        ).value.trim();


    const message=
        document.getElementById(
            "replyMsg"+id
        ).value.trim();


    if(!message){

        toast("Write a reply.");

        return;
    }


    const r=await fetch(
        "/api/posts/"+id+"/replies",
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                name,
                message
            })
        }
    );


    const data=await r.json();


    if(!r.ok){

        toast(data.error);

        return;
    }


    toast("Reply added.");

    loadPosts();
    loadHall();
}


async function helpful(type,id){

    const r=await fetch(
        "/api/helpful",
        {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                type,
                id
            })
        }
    );


    const data=await r.json();


    if(!r.ok){

        toast(data.error);

        return;
    }


    toast("Marked helpful.");

    loadPosts();
    loadHall();
}


/* ========================================================
   HALL OF FAME
======================================================== */

async function loadHall(){

    const box=document.getElementById("hall");

    const r=await fetch("/api/hall-of-fame");

    const data=await r.json();


    if(!data.people.length){

        box.innerHTML=`

            <div class="card hall-card">

                <div class="rank">
                    HERO OF THE WEEK
                </div>

                <div>
                    <div class="hall-name">
                        Waiting...
                    </div>

                    <div class="score">
                        Make the first helpful contribution.
                    </div>
                </div>

            </div>

        `;

        return;
    }


    const titles=[
        "HERO OF THE WEEK",
        "TOP CONTRIBUTOR",
        "RISING HELPER"
    ];


    box.innerHTML=
        data.people.map((p,i)=>`

            <div class="card hall-card">

                <div class="rank">
                    ${titles[i]||"TOP CONTRIBUTOR"}
                </div>

                <div>

                    <div class="hall-name">
                        ${escapeHTML(p.name)}
                    </div>

                    <div class="score">
                        ${p.score} contribution points
                    </div>

                </div>

            </div>

        `).join("");
}


/* ========================================================
   ESCAPE
======================================================== */

function escapeHTML(value){

    return String(value ?? "")
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");
}


/* ========================================================
   START
======================================================== */

loadPosts();
loadHall();

</script>

</body>
</html>
"""


# =========================================================
# ROUTES
# =========================================================


@app.route("/")
def home():
    return render_template_string(HTML)


# =========================================================
# SGPA
# =========================================================


@app.route("/api/sgpa", methods=["POST"])
def calculate_sgpa():

    data = request.get_json(silent=True) or {}

    credits = data.get("credits", [])
    grades = data.get("grades", [])

    if len(credits) != len(grades):
        return jsonify({"error": "Credits and grade points must match."}), 400

    total_credits = 0
    total_points = 0

    try:
        for c, g in zip(credits, grades):
            c = float(c)
            g = float(g)

            if c <= 0:
                continue

            if g < 0 or g > 10:
                return jsonify({"error": "Grade point must be between 0 and 10."}), 400

            total_credits += c
            total_points += c * g

    except Exception:
        return jsonify({"error": "Enter valid numbers."}), 400

    if total_credits == 0:
        return jsonify({"error": "Add at least one subject."}), 400

    sgpa = total_points / total_credits

    return jsonify({"sgpa": round(sgpa, 2)})


# =========================================================
# CGPA
# =========================================================


@app.route("/api/cgpa", methods=["POST"])
def calculate_cgpa():

    data = request.get_json(silent=True) or {}

    credits = data.get("credits", [])
    sgpas = data.get("sgpas", [])

    if len(credits) != len(sgpas):
        return jsonify({"error": "Semester credits and SGPA must match."}), 400

    total_credits = 0
    total_weight = 0

    try:
        for c, s in zip(credits, sgpas):
            c = float(c)
            s = float(s)

            if c <= 0:
                continue

            if s < 0 or s > 10:
                return jsonify({"error": "SGPA must be between 0 and 10."}), 400

            total_credits += c
            total_weight += c * s

    except Exception:
        return jsonify({"error": "Enter valid numbers."}), 400

    if total_credits == 0:
        return jsonify({"error": "Add at least one semester."}), 400

    cgpa = total_weight / total_credits

    # Shivaji University BCA 2024-25 NEP grade bands
    if cgpa >= 9:
        band = "O — Outstanding"
    elif cgpa >= 8:
        band = "A+ — Excellent"
    elif cgpa >= 7:
        band = "A — Very Good"
    elif cgpa >= 6:
        band = "B+ — Good"
    elif cgpa >= 5:
        band = "B — Above Average"
    elif cgpa >= 4:
        band = "C — Average"
    else:
        band = "F — Fail"

    return jsonify({"cgpa": round(cgpa, 2), "grade_band": band})


# =========================================================
# CSIBER ASSISTANT
# =========================================================


@app.route("/api/csiber-assistant", methods=["POST"])
def csiber_assistant():

    data = request.get_json(silent=True) or {}

    q = str(data.get("question", "")).strip().lower()

    if not q:
        return jsonify({"answer": "Please ask a CSIBER-related question."})

    # ---------------------------------------------
    # Strict CSIBER scope
    # ---------------------------------------------

    keywords = [
        "csiber",
        "siber",
        "bca",
        "college",
        "admission",
        "semester",
        "course",
        "programme",
        "program",
        "attendance",
        "sgpa",
        "cgpa",
        "exam",
        "campus",
        "school of computer",
        "computer science",
    ]

    if not any(k in q for k in keywords):
        return jsonify(
            {
                "answer": "I'm the CSIBER Assistant, so I stay focused on "
                "CSIBER-related academic and student questions. "
                "Ask me something about CSIBER, BCA, semesters, "
                "admission, exams, SGPA/CGPA or student life."
            }
        )

    # ---------------------------------------------
    # BCA
    # ---------------------------------------------

    if "bca" in q and ("year" in q or "duration" in q or "kitne" in q or "course" in q):
        return jsonify(
            {
                "answer": "CSIBER ka official BCA programme 3/4-year "
                "undergraduate programme hai. 6/8 semesters "
                "structure diya gaya hai. Fourth year ke baad "
                "Honours pathway available hai."
            }
        )

    # ---------------------------------------------
    # Admission
    # ---------------------------------------------

    if "admission" in q or "eligibility" in q:
        return jsonify(
            {
                "answer": "CSIBER ke official BCA admission information ke "
                "according, BCA ke liye 10+2 (HSC) ya equivalent "
                "qualification required hai. Current admission "
                "rules ke liye official CSIBER admission page "
                "check karna best rahega."
            }
        )

    # ---------------------------------------------
    # SGPA
    # ---------------------------------------------

    if "sgpa" in q:
        return jsonify(
            {
                "answer": "SGPA = Σ(Credit × Grade Point) / Σ(Credits). "
                "CSIBER//ONE mein isi weighted method se SGPA "
                "calculate kiya ja raha hai."
            }
        )

    # ---------------------------------------------
    # CGPA
    # ---------------------------------------------

    if "cgpa" in q:
        return jsonify(
            {
                "answer": "CGPA multiple semesters ke SGPA ko semester "
                "credits ke according weight karke calculate "
                "karta hai. Formula: Σ(Semester Credits × SGPA) "
                "/ Σ(Semester Credits)."
            }
        )

    # ---------------------------------------------
    # Attendance
    # ---------------------------------------------

    if "attendance" in q or "leave" in q:
        return jsonify(
            {
                "answer": "CSIBER//ONE ka Leave & Attendance Guard "
                "working days, holidays aur tumhari leave ke "
                "basis par estimated attendance calculate karta "
                "hai. 80% ko safe zone aur 75% ko warning "
                "threshold ke roop mein dikhaya gaya hai."
            }
        )

    # ---------------------------------------------
    # Exam
    # ---------------------------------------------

    if "exam" in q or "schedule" in q:
        return jsonify(
            {
                "answer": "CSIBER mein BCA examination information official "
                "CSIBER examination/schedule section mein publish "
                "hoti hai. CSIBER//ONE mein future version mein "
                "official schedule integration add ki ja sakti hai."
            }
        )

    # ---------------------------------------------
    # Campus
    # ---------------------------------------------

    if "campus" in q:
        return jsonify(
            {
                "answer": "CSIBER Kolhapur ek autonomous institute hai. "
                "Official CSIBER website par campus, programmes, "
                "announcements aur student information available hai."
            }
        )

    return jsonify(
        {
            "answer": "Mujhe is question ka verified CSIBER-specific "
            "answer abhi available knowledge mein nahi mila. "
            "Main general internet answer invent nahi karunga. "
            "CSIBER, BCA, admission, exam, SGPA/CGPA ya attendance "
            "se related question poochho."
        }
    )


# =========================================================
# POSTS
# =========================================================


@app.route("/api/posts", methods=["GET"])
def posts():

    con = db()

    rows = con.execute("""
        SELECT *
        FROM posts
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()

    output = []

    for p in rows:
        replies = con.execute(
            """
            SELECT *
            FROM replies
            WHERE post_id=?
            ORDER BY id ASC
        """,
            (p["id"],),
        ).fetchall()

        output.append(
            {
                "id": p["id"],
                "name": clean_name(p["name"]),
                "category": p["category"],
                "message": p["message"],
                "helpful": p["helpful"],
                "created_at": fmt_time(p["created_at"]),
                "attachment": "/uploads/" + p["attachment"]
                if p["attachment"]
                else None,
                "attachment_name": p["attachment"] or "",
                "replies": [
                    {
                        "id": r["id"],
                        "name": clean_name(r["name"]),
                        "message": r["message"],
                        "helpful": r["helpful"],
                        "created_at": fmt_time(r["created_at"]),
                    }
                    for r in replies
                ],
            }
        )

    con.close()

    return jsonify({"posts": output})


# =========================================================
# CREATE POST
# =========================================================


@app.route("/api/posts", methods=["POST"])
def create_post():

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "General").strip()

    message = request.form.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    attachment = None

    uploaded = request.files.get("file")

    if uploaded and uploaded.filename:
        if not allowed_file(uploaded.filename):
            return jsonify({"error": "File type not allowed."}), 400

        original = secure_filename(uploaded.filename)

        if not original:
            return jsonify({"error": "Invalid file."}), 400

        filename = uuid.uuid4().hex[:12] + "_" + original

        uploaded.save(os.path.join(UPLOAD_DIR, filename))

        attachment = filename

    con = db()

    con.execute(
        """
        INSERT INTO posts
        (
            name,
            category,
            message,
            attachment,
            helpful,
            created_at
        )
        VALUES (?, ?, ?, ?, 0, ?)
    """,
        (name[:60], category[:30], message[:2000], attachment, current_time()),
    )

    con.commit()
    con.close()

    return jsonify({"success": True})


# =========================================================
# REPLY
# =========================================================


@app.route("/api/posts/<int:post_id>/replies", methods=["POST"])
def reply(post_id):

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()

    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Reply cannot be empty."}), 400

    con = db()

    exists = con.execute(
        """
        SELECT id
        FROM posts
        WHERE id=?
    """,
        (post_id,),
    ).fetchone()

    if not exists:
        con.close()

        return jsonify({"error": "Post not found."}), 404

    con.execute(
        """
        INSERT INTO replies
        (
            post_id,
            name,
            message,
            helpful,
            created_at
        )
        VALUES (?, ?, ?, 0, ?)
    """,
        (post_id, name[:60], message[:1000], current_time()),
    )

    con.commit()
    con.close()

    return jsonify({"success": True})


# =========================================================
# HELPFUL
# =========================================================


@app.route("/api/helpful", methods=["POST"])
def helpful():

    data = request.get_json(silent=True) or {}

    typ = data.get("type")
    item_id = data.get("id")

    if typ not in ("post", "reply"):
        return jsonify({"error": "Invalid target."}), 400

    try:
        item_id = int(item_id)
    except:
        return jsonify({"error": "Invalid ID."}), 400

    vid = visitor_id()

    con = db()

    already = con.execute(
        """
        SELECT id
        FROM votes
        WHERE visitor_id=?
        AND target_type=?
        AND target_id=?
    """,
        (vid, typ, item_id),
    ).fetchone()

    if already:
        con.close()

        return jsonify({"error": "You already marked this helpful."}), 400

    table = "posts" if typ == "post" else "replies"

    exists = con.execute(f"SELECT id FROM {table} WHERE id=?", (item_id,)).fetchone()

    if not exists:
        con.close()

        return jsonify({"error": "Content not found."}), 404

    con.execute(
        f"""
        UPDATE {table}
        SET helpful=helpful+1
        WHERE id=?
        """,
        (item_id,),
    )

    con.execute(
        """
        INSERT INTO votes
        (
            visitor_id,
            target_type,
            target_id
        )
        VALUES (?, ?, ?)
    """,
        (vid, typ, item_id),
    )

    con.commit()
    con.close()

    return jsonify({"success": True})


# =========================================================
# HALL OF FAME
# =========================================================


@app.route("/api/hall-of-fame")
def hall_of_fame():

    today = datetime.now()

    monday = today - timedelta(days=today.weekday())

    start = monday.strftime("%Y-%m-%d 00:00:00")

    con = db()

    people = {}

    posts = con.execute(
        """
        SELECT
            TRIM(name) name,
            COUNT(*) contributions,
            COALESCE(SUM(helpful),0) helpful
        FROM posts
        WHERE created_at>=?
        AND TRIM(name)<>''
        GROUP BY TRIM(name)
    """,
        (start,),
    ).fetchall()

    replies = con.execute(
        """
        SELECT
            TRIM(name) name,
            COUNT(*) contributions,
            COALESCE(SUM(helpful),0) helpful
        FROM replies
        WHERE created_at>=?
        AND TRIM(name)<>''
        GROUP BY TRIM(name)
    """,
        (start,),
    ).fetchall()

    for row in posts:
        name = row["name"]

        people.setdefault(name, {"contributions": 0, "helpful": 0})

        people[name]["contributions"] += row["contributions"]

        people[name]["helpful"] += row["helpful"]

    for row in replies:
        name = row["name"]

        people.setdefault(name, {"contributions": 0, "helpful": 0})

        people[name]["contributions"] += row["contributions"]

        people[name]["helpful"] += row["helpful"]

    result = []

    for name, stats in people.items():
        score = stats["contributions"] * 2 + stats["helpful"] * 3

        result.append(
            {
                "name": name,
                "score": score,
                "contributions": stats["contributions"],
                "helpful": stats["helpful"],
            }
        )

    result.sort(
        key=lambda x: (x["score"], x["helpful"], x["contributions"]), reverse=True
    )

    con.close()

    return jsonify({"people": result[:3]})


# =========================================================
# FILES
# =========================================================


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    from flask import send_from_directory

    return send_from_directory(UPLOAD_DIR, filename)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    print()
    print("==========================================")
    print("       CSIBER//ONE")
    print("       Student OS")
    print("       Architected by Anuj Gupta")
    print("==========================================")
    print()
    print("Local:")
    print("http://127.0.0.1:5000")
    print()
    print("Network:")
    print("http://YOUR-PC-IP:5000")
    print()

    app.run(host="0.0.0.0", port=5000, debug=True)
