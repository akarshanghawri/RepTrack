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
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date).all()
    unique_dates = []
    pr = defaultdict(list)
    
    for workout in workouts :
        if workout.date not in unique_dates :
            unique_dates.append(workout.date)

    # Streak logic 
    longest_streak = 1
    temp_streak = 1 

    for i in range(len(unique_dates)-1) :
        d1 = unique_dates[i]
        d2 = unique_dates[i+1]
        if d1 - d2 > timedelta(days=1) :
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else :
            temp_streak += 1
    
    today = date.today()
    last_workout_date = unique_dates[-1]  

    if (today - last_workout_date) > timedelta(days=1):
        curr_streak = 0
    else : 
        curr_streak = 1
        for i in range(len(unique_dates)-1, 0, -1):
            diff = unique_dates[i] - unique_dates[i-1]
            if diff == timedelta(days=1):
                curr_streak += 1
            else:
                break
    

    # Personal Records (pr)
    pr = {}
    for workout in workouts:
        name = workout.exercise.name
        for s in workout.sets:
            if s.weight:
                if name not in pr:
                    pr[name] = s.weight
                elif s.weight > pr[name]:
                    pr[name] = s.weight

    most_trained = {}
    for workout in workouts:
        name = workout.exercise.name
        if name not in most_trained:
            most_trained[name] = 0
        most_trained[name] += 1
    
    most_trained = dict(sorted(most_trained.items(), key=lambda x: x[1], reverse=True))
    
    progress = {}
    for workout in workouts:
        name = workout.exercise.name

        if name not in progress:
            progress[name] = {"dates": [], "volumes": []}

        best_volume = 0
        for s in workout.sets:
            if s.weight:
                volume = s.reps * s.weight
                if volume > best_volume:
                    best_volume = volume

        if best_volume > 0:
            progress[name]["dates"].append(str(workout.date))
            progress[name]["volumes"].append(best_volume)

    # print(most_trained, progress)
    
    return render_template("stats.html", curr_streak  = curr_streak,
                           longest_streak  = longest_streak,
                           total_sessions  = len(workouts),
                           pr              = pr,
                           most_trained    = most_trained,
                           progress        = progress)

# @main.route('/new')
# @login_required
