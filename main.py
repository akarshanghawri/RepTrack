from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from .models import User,Workout
from datetime import date, datetime
from .import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index() :
    workouts = Workout.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html",workouts=workouts)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_workout() :
    if request.method == 'POST' :
        reps = request.form.get('reps')
        sets = request.form.get('sets')
        comment = request.form.get('comment')
        date = request.form.get('date')

        if not reps or not sets :
            flash("Reps and Sets are required","danger")
            return redirect(url_for('main.add_workout'))
        
        if not comment :
            comment = "-"
        
        workout = Workout(
            reps = reps,
            sets = sets,
            comment = comment,
            date = datetime.strptime(date, "%Y-%m-%d").date(),
            user_id = current_user.id
        )

        db.session.add(workout)
        db.session.commit()

        return redirect(url_for('main.index'))

    return render_template("add_workout.html")

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_workout(id) :
    workout = Workout.query.get_or_404(id)

    if request.method == 'POST' :
        workout.reps = request.form.get('reps')
        workout.sets = request.form.get('sets')
        workout.comment = request.form.get('comment')

        workout_date = request.form.get('date')
        workout.date = datetime.strptime(workout_date, "%Y-%m-%d").date()

        db.session.commit()
        flash("Workout updated successfully", "success")

        return redirect(url_for('main.index'))

    return render_template('edit_workout.html', workout = workout)

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
