# CSIBER//ONE 
**Your Campus. One Interface.**
*Architected by ANUJ GUPTA (BCA • CSIBER)*

A premium, student-built digital utility layer designed for CSIBER students. Featuring timetable management, attendance safety calculators, CGPA tools, real-time campus chat, and a community resource hub wrapped in a cinematic, app-like UI.

## Tech Stack
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Zero frontend frameworks, 100% custom styling).
* **Backend:** Python, Flask, Flask-SocketIO.
* **Database:** SQLite (Auto-initialized).

## Features
1. **Timetable Dashboard:** Day-by-day routing.
2. **Attendance Guard:** Day-based algorithmic calculation for safe leaves (80% threshold).
3. **SGPA/CGPA Calculators:** Dynamic credit-weighted grading.
4. **Class Connect:** Resource & Doubt sharing with 10MB secure file uploads.
5. **Live Campus Chat:** Real-time Socket.IO chat rooms.
6. **Hall of Fame:** Algorithmic weekly top-contributor podium based on community help.
7. **CSIBER Assistant:** Rule-based query responder.
8. **Command Palette:** Global search via `Ctrl + K`.

## ⚠️ Important Deployment Notice for GitHub
**GitHub Pages CANNOT run this application backend.** 
GitHub Pages only hosts static files (HTML/CSS/JS). Because CSIBER//ONE relies on a Python Flask backend for SQLite databases, file uploads, and Socket.IO WebSockets, you must deploy the backend to a Python-capable hosting provider (e.g., Render, Railway, PythonAnywhere, or a VPS). 

## Local Setup (Windows)

1. **Open Terminal** in your project folder.
2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv