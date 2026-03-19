from . import db 
from flask_login import UserMixin

# db.Model (defines tables)
# UserMixin automatically adds: is_authenticated, is_active, is_anonymous, get_id() 
class User(UserMixin, db.Model) :              
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    workouts = db.relationship('Workout', backref='user', lazy=True)

class Workout(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    comment = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)

    sets = db.relationship('WorkoutSet', backref='workout', lazy=True, cascade='all, delete-orphan')

class WorkoutSet(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)

    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)

class Exercise(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # True - predefined common exercises
    # False - user-created exercises
    is_global = db.Column(db.Boolean, default=False)

    # Null if user has created no new exercises
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    workouts = db.relationship('Workout', backref='exercise', lazy=True)