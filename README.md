# RepTrack 🏋️

A full-stack workout tracking web application built with Flask. Log workouts, track progress over time, view personal records, and generate AI-powered personalized fitness plans.

**Live Demo:** [reptrack-3ht8.onrender.com](https://reptrack-3ht8.onrender.com)

---

## Features

- **Workout Logging** — Log exercises with dynamic per-set reps and weight tracking
- **Weekly View** — Workouts grouped by date with week-based pagination
- **Stats Dashboard** — Progress charts, personal records, streaks, and most trained exercises
- **Workout Detail** — Per-session breakdown with comparison to previous session and PR badges
- **AI Fitness Plan Generator** — Fill a form and get a personalized HTML fitness plan powered by Groq (Llama 3.1)
- **Authentication** — Secure signup, login, and session management with Flask-Login

---

## Tech Stack

**Backend**
- Python / Flask
- SQLAlchemy + Flask-Migrate (ORM + migrations)
- Flask-Login (authentication)
- Groq API — `llama-3.1-8b-instant` (AI plan generation)
- PostgreSQL (production) / SQLite (development)
- Gunicorn (production server)

**Frontend**
- Jinja2 templating
- Bootstrap 5
- Chart.js (stats visualizations)
- Vanilla JS (dynamic set rows, exercise search)

**DevOps**
- Render (hosting + managed PostgreSQL)
- Git + GitHub

---

## Architecture

This project follows a **3-tier architecture**:

```
Tier 1 — Presentation   Jinja2 templates + Bootstrap + JS
Tier 2 — Application    Flask routes, business logic (main.py, auth.py)
Tier 3 — Data           SQLAlchemy models + PostgreSQL/SQLite
```

It also follows the **MVC pattern** within the application tier:
```
Model       → models.py
View        → templates/
Controller  → main.py, auth.py
```

---

## Database Schema

```
User
 └── Workout (exercise, date, notes)
       └── WorkoutSet (set_number, reps, weight)

Exercise (global predefined + user-created)
```

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/akarshanghawri/RepTrack.git
cd RepTrack
```

**2. Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file**
```
FLASK_APP=wsgi.py
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key-here
DATABASE_URL=sqlite:///db.sqlite
```

Get a free Groq API key at [console.groq.com](https://console.groq.com)

**5. Set up the database**
```bash
flask db upgrade        # creates all tables
flask seed-exercises    # seeds predefined exercises
```

**6. Run the app**
```bash
flask run
```

Visit `http://127.0.0.1:5000`

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret key |
| `DATABASE_URL` | Database connection string (SQLite locally, PostgreSQL on Render) |
| `GROQ_API_KEY` | Groq API key for AI plan generation |
| `FLASK_APP` | Entry point — set to `wsgi.py` |

---

## Deployment (Render)

1. Create a **Web Service** on [render.com](https://render.com) connected to this repo
2. Create a **PostgreSQL** database on Render, copy the Internal Database URL
3. Set environment variables in Render dashboard
4. Set build command:
```
pip install -r requirements.txt && flask db upgrade && flask seed-exercises
```
5. Set start command:
```
gunicorn wsgi:app
```

---