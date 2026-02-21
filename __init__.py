from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os 

db = SQLAlchemy()
login_manager = LoginManager()

def create_app() :
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="secretKey",
        SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite"
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"             # redirect if not logged in
    Migrate(app,db)


    @app.cli.command("seed-exercises")
    def seed_exercises() :
        from .models import Exercise

        existing = Exercise.query.filter_by(is_global=True).first()

        if existing :
            print("Exercises already added")
            return 

        exercises = [
            "Push-ups", "Bench Press", "Incline Bench Press",
            "Decline Bench Press", "Dumbbell Press", "Chest Fly",
            "Cable Fly", "Chest Dips",
            "Pull-ups", "Chin-ups", "Lat Pulldown", "Deadlift",
            "Barbell Row", "Dumbbell Row", "Seated Cable Row",
            "T-Bar Row", "Face Pull",
            "Overhead Press", "Arnold Press", "Lateral Raise",
            "Front Raise", "Rear Delt Fly", "Shrugs",
            "Squats", "Front Squat", "Leg Press", "Lunges",
            "Romanian Deadlift", "Leg Curl", "Leg Extension",
            "Calf Raises", "Bulgarian Split Squat", "Hip Thrust",
            "Barbell Curl", "Dumbbell Curl", "Hammer Curl",
            "Preacher Curl", "Tricep Dips", "Tricep Pushdown",
            "Skull Crushers", "Overhead Tricep Extension",
            "Plank", "Crunches", "Leg Raises",
            "Russian Twists", "Hanging Leg Raises", "Cable Crunch"
        ]

        for name in exercises :
            exercise = Exercise(name=name, is_global=True)
            db.session.add(exercise)

        db.session.commit()
        print("Exercises added")

    from .models import User

    @login_manager.user_loader                          # register user loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app


