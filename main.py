from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from sqlalchemy import func 
from collections import defaultdict
from .models import User,Workout,Exercise, WorkoutSet
from datetime import date, datetime, timedelta
from .import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    workouts = (Workout.query
                .filter_by(user_id=current_user.id)
                .order_by(Workout.date.desc())
                .all())

    # grouping by date 
    by_date = defaultdict(list)
    for workout in workouts:
        by_date[workout.date].append(workout)

    by_week = defaultdict(dict)
    for date, date_workouts in by_date.items():
        iso = date.isocalendar()                    
        week_key = (iso.year, iso.week)                 # isocalendar () - tells the week and year of any date 
        by_week[week_key][date] = date_workouts
    
    sorted_weeks = sorted(by_week.keys(), reverse=True)
    total_weeks = len(sorted_weeks)

    # pagination by week  
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 1   # 1 week per page
    current_week_key = sorted_weeks[start] if start < total_weeks else None

    total_pages = total_weeks

    # get the dates for current week 
    if current_week_key:
        week_data = dict(sorted(
            by_week[current_week_key].items(),
            reverse=True
        ))
    else:
        week_data = {}

    if week_data:
        any_date = list(week_data.keys())[0]
        # Monday of this week
        week_start = any_date - timedelta(days=any_date.weekday())
        # Sunday is 6 days after Monday
        week_end = week_start + timedelta(days=6)
    else:
        week_start = week_end = None

    return render_template("index.html",
                           grouped=week_data,
                           page=page,
                           total_pages=total_pages,
                           week_start=week_start,
                           week_end=week_end,
                           total_weeks=total_weeks)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_workout() :
    global_exercises = Exercise.query.filter_by(is_global=True).all()
    user_exercises = Exercise.query.filter_by(user_id = current_user.id).all()
    exercises = global_exercises + user_exercises

    if request.method == 'POST' :
        exercise_id = request.form.get('exercise_id')
        comment = request.form.get('comment') or '-'
        date = request.form.get('date')

        if not exercise_id :
            flash("Please select an exercise", "danger")
            return redirect(url_for('main.add_workout'))

        reps_list = request.form.getlist('reps')
        weights_list = request.form.getlist('weight')

        if not reps_list or not weights_list :
            flash("Fill the Reps","danger")
            return redirect(url_for('main.add_workout'))
                
        workout = Workout(
            comment = comment,
            date = datetime.strptime(date, "%Y-%m-%d").date(),
            user_id = current_user.id,
            exercise_id = exercise_id
        )

        db.session.add(workout)
        db.session.flush()

        for i, (reps, weight) in enumerate(zip(reps_list,weights_list)) :
            if reps :
                workout_set = WorkoutSet(
                    set_number = i + 1,
                    reps = int(reps), 
                    weight = float(weight), 
                    workout_id = workout.id
                )
                db.session.add(workout_set)

        db.session.commit()

        flash("Workout added successfully", "success")
        return redirect(url_for('main.index'))

    return render_template("add_workout.html", exercises=exercises)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_workout(id) :
    workout = Workout.query.get_or_404(id)

    if request.method == 'POST' :
        workout.comment = request.form.get('comment')

        workout_date = request.form.get('date')
        workout.date = datetime.strptime(workout_date, "%Y-%m-%d").date()

        # delete old sets
        workout.sets.clear()
        db.session.flush()

        reps_list = request.form.getlist('reps')
        weights_list = request.form.getlist('weight')

        for i, (reps, weight) in enumerate(zip(reps_list, weights_list)) :
            if reps :
                workout_set = WorkoutSet(
                    set_number = i + 1,
                    reps = int(reps),
                    weight = float(weight),
                    workout_id = workout.id
                )
                db.session.add(workout_set)

        db.session.commit()
        flash("Workout updated successfully", "success")

        return redirect(url_for('main.index'))

    return render_template('edit_workout.html', workout = workout)

@main.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_workout(id) :
    workout = Workout.query.get_or_404(id)

    db.session.delete(workout)
    db.session.commit()

    flash("Workout Deleted", "success")
    return redirect(url_for('main.index'))

@main.route('/profile')
@login_required
def profile() :
    return render_template("profile.html")

@main.route('/stats')
@login_required
def stats():
    workouts = Workout.query.filter_by(user_id=current_user.id).all()

    stats = {}
    for workout in workouts :
        exercise_name = workout.exercise.name

        if exercise_name not in stats :
            stats[exercise_name] = {"total_workouts" : 0, "total_reps": 0}
        
        stats[exercise_name]["total_workouts"] += 1 

        for workout_set in workout.sets:
            stats[exercise_name]["total_reps"] += workout_set.reps

    exercise_names = []
    total_workouts = []
    total_reps = []

    # print(stats)
    
    for name, data in stats.items() :
        exercise_names.append(name)
        total_workouts.append(data["total_workouts"])
        total_reps.append(data["total_reps"])
    

    return render_template("stats.html", exercise_names=exercise_names,
                                        total_workouts=total_workouts,total_reps=total_reps)

# @main.route('/new')
# @login_required
