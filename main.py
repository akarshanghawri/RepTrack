from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import User,Workout

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index() :
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html",workouts=workouts)

@main.route('/add')
@login_required
def add_workout() :
    return

@main.route('/edit/<int:id>')
@login_required
def edit_workout(id) :
    return

@main.route('/delete/<int:id>')
@login_required
def delete_workout(id) :
    return

@main.route('/profile')
@login_required
def profile() :
    return render_template("profile.html")

@main.route('/stats')
@login_required
def stats():
    return render_template("stats.html")

# @main.route('/new')
# @login_required
