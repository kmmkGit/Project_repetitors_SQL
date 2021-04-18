from flask import render_template, redirect, request
import json
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import RadioField
from wtforms import SubmitField
from wtforms import HiddenField
from wtforms import SelectField
from wtforms.validators import InputRequired, Length, DataRequired

from app import app, db, Teacher, Goal, Booking, Request, TimeHave, WeekDay

with open("teachers.json", "r", encoding='utf-8') as f:
    teachers = json.load(f)

days_of_week = dict(
    (day.name_english_long[0:3],
     (day.name_english_long,
      day.name_rus))
    for day in db.session.query(WeekDay).all())

goals_pict = dict(map(lambda goal:
                      (goal[1].name_english, (goal[1].name_rus, goal[1].picture, 'goal' + str(goal[0]))),
                      enumerate(db.session.query(Goal).all(), 1)
                      ))
request_goal_choices = [(goal.name_english, goal.name_rus) for goal in db.session.query(Goal).all()]

time_have = list(map(
    lambda time:
    ("time"+str(time[0]), time[1].time), enumerate(db.session.query(TimeHave).all(), 1)
))
for r in db.session.query(TimeHave).get(4).requests:
    print(r.learner)

"""
for goal in goals_pict.keys():
    print(goal, " --> ", end=" ")
    teachers_goal = db.session.query(Teacher).join(Goal).filter(Goal.name_english == goal).all()
#    print(goal_query.name_english, goal_query.name_rus)
#    teachers_goal = db.session.query(Teacher).filter(goal_query.in_(Teacher.goals)).all()
#    Teacher.goals.name_english == goal
    for t in teachers_goal:
        print(t.name, ", ", end="")
    print()
"""