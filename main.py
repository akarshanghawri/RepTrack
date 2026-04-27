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

@main.route('/workout/<int:id>')
@login_required
def workout_detail(id) :
    workout = Workout.query.get_or_404(id)

    previous = (Workout.query.filter_by(user_id=current_user.id, exercise_id = workout.exercise_id)
                .filter(Workout.date < workout.date)
                .order_by(Workout.date.desc())
                .first())
    
    all_workouts = Workout.query.filter_by(user_id = current_user.id, exercise_id=workout.exercise_id).all()

    pr_weight = 0
    for workout in all_workouts :
        for set in workout.sets :
            if set.weight and set.weight > pr_weight :
                pr_weight = set.weight
    
    return render_template('workout_detail.html',
                           workout = workout,
                           previous = previous,
                           pr_weight = pr_weight)

from groq import Groq
import os 

@main.route('/plan', methods=['GET', 'POST'])
@login_required
def generate_plan():
    if request.method == 'POST':
        
        # All form data of user

        height = request.form.get('height')
        weight = request.form.get('weight')
        age = request.form.get('age')
        gender = request.form.get('gender')
        occupation = request.form.get('occupation')
        activity_level = request.form.get('activity_level')

        primary_goal = request.form.get('primary_goal')
        secondary_goal = request.form.get('secondary_goal')
        target_weight = request.form.get('target_weight')
        timeframe = request.form.get('timeframe')

        days_per_week = request.form.get('days')
        duration = request.form.get('duration')
        days_per_week = request.form.get('days')

        experience = request.form.get('experience')
        equipment = request.form.get('equipment')
        diet = request.form.get('diet')
        preferred_time = request.form.get('preferred_time')

        sleep = request.form.get('sleep')
        injuries = request.form.get('injuries')
        stress = request.form.get('stress')

        # prompt for generating the plan
        prompt = f"""
            You are a certified fitness coach and strength & conditioning expert.
            Create a personalized workout plan using the following user details.

            USER PROFILE
            Age: {age}
            Gender: {gender}
            Height: {height} cm
            Weight: {weight} kg
            Occupation: {occupation}
            Daily activity level: {activity_level}

            FITNESS GOALS
            Primary goal: {primary_goal}
            Secondary goal: {secondary_goal}
            Target weight: {target_weight} kg
            Timeframe: {timeframe}

            EXPERIENCE LEVEL
            {experience}

            AVAILABILITY
            Workout frequency: {days_per_week} days per week
            Session duration: {duration} minutes
            Preferred workout time: {preferred_time}

            WORKOUT ENVIRONMENT
            Equipment available: {equipment}

            HEALTH CONSIDERATIONS
            Injuries or concerns: {injuries}

            LIFESTYLE
            Sleep: {sleep} hours/night
            Stress level: {stress}
            Diet type: {diet}

            OUTPUT REQUIREMENTS
            1. Create a structured weekly workout split.
            2. Include exercises, sets, reps, rest time, and estimated duration.
            3. Add warm-up and cooldown recommendations.
            4. Include progression strategy for the full timeframe.
            5. Suggest beginner-friendly weights and intensity guidance.
            6. Provide injury prevention tips based on health considerations.
            7. Keep instructions practical, clear, and beginner-friendly.
            8. Add optional cardio recommendations.
            9. Provide weekly progression checkpoints.

            IMPORTANT: Return ONLY a complete HTML document starting with <!DOCTYPE html>.
            Use inline CSS for styling. Clean modern look with tables where helpful.
            No markdown. No code blocks. No explanation outside the HTML.
            Use the current year {date.today().year} for any copyright or date references.

            STRICT RULES:
            - Always use a white background with dark text
            - Always include a weekly table as the first section
            - Always use the exact same section order:
            1. Weekly Split Table
            2. Exercise Details
            3. Nutrition
            4. Progression Plan
            - Never skip any section
         """

        # 3. call API
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0       # to stop the randomness
        )
        
        reply = response.choices[0].message.content
    

        return render_template("plan_result.html", reply=reply)
    
    return render_template("generate_plan.html")
