from flask import render_template, request
import json
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import RadioField
from wtforms import SubmitField
from wtforms import HiddenField
from wtforms import SelectField
from wtforms.validators import InputRequired, Length
from sqlalchemy.sql import func

from app import app, db, Teacher, Goal, Booking, Request, TimeHave, WeekDay

with open("goals.json", "r", encoding='utf-8') as f:
    goals = json.load(f)
with open("teachers.json", "r", encoding='utf-8') as f:
    teachers = json.load(f)

TEACHERS_LIMIT = 6

goals_pict = dict(map(
    lambda goal:
    (goal[1].name_english, (goal[1].name_rus, goal[1].picture, 'goal' + str(goal[0]))),
    enumerate(db.session.query(Goal).all(), 1)
))

time_have = list(map(
    lambda time:
    ("time" + str(time[0]), time[1].time),
    enumerate(db.session.query(TimeHave).all(), 1)
))

days_of_week = dict(
    (day.name_english_long[0:3],
     (day.name_rus,
      day.name_english_long))
    for day in db.session.query(WeekDay).all())

request_goal_choices = [(goal.name_english, goal.name_rus) for goal in db.session.query(Goal).all()]


class FormRequest(FlaskForm):
    name = StringField("Вас зовут", [InputRequired(message="Необходимо указать имя"),
                                     Length(min=2, max=50, message="Имя %(min)d - %(max)d символов")])
    phone = StringField("Ваш телефон", [InputRequired(message="Необходимо ввести ваш номер телефона"),
                                        Length(max=15, message="Слишком много символов в номере телефона")])
    goal = RadioField('Какая цель занятий?', choices=request_goal_choices, default=request_goal_choices[0][0])
    time = RadioField('Сколько времени есть?', choices=time_have, default=time_have[0][0])
    submit = SubmitField('Найдите мне преподавателя')


class BookingToTeacher(FlaskForm):
    name = StringField("Вас зовут", [InputRequired(message="Необходимо указать имя"),
                                     Length(min=2, max=50, message="Имя %(min)d - %(max)d символов")])
    phone = StringField("Ваш телефон", [InputRequired(message="Необходимо ввести ваш номер телефона"),
                                        Length(max=15, message="Слишком много символов в номере телефона")])
    submit = SubmitField('Записаться на пробный урок')
    weekday = HiddenField("День недели для записи")
    time = HiddenField("Часы занятий для записи")
    teacher = HiddenField("Id учителя")


class SortTeachers(FlaskForm):
    sort_type = SelectField("Сортировка преподавателей",
                            choices=[("Случайно", "В случайном порядке"),
                                     ("Рейтинг", "Сначала лучшие по рейтингу"),
                                     ("Дорогие", "Сначала дорогие"),
                                     ("Недорогие", "Сначала недорогие")])
    submit = SubmitField('Сортировать')


def free_time_exist(teacher_id, day, time):
    my_teacher = db.session.query(Teacher).get(teacher_id)
    teacher_free = eval(my_teacher.free)
    if time in list(teacher_free.values())[0].keys() and \
            teacher_free[day[0:3]][time]:
        return True
    return False


@app.route('/')
# здесь будет главная
def render_main():
    teachers_list = db.session.query(Teacher).order_by(func.random()).limit(TEACHERS_LIMIT)
    return render_template('index.html', teachers=teachers_list, goals=goals_pict)


@app.route('/all/', methods=["POST", "GET"])
# здесь будут преподаватели
def render_all():
    form = SortTeachers()
    teachers_query = db.session.query(Teacher)
    teachers_sort = []
    if request.method == 'POST':
        sort_type = form.sort_type.data
        if sort_type == form.sort_type.choices[0][0]:
            teachers_sort = teachers_query.order_by(func.random()).all()
        if sort_type == form.sort_type.choices[1][0]:
            teachers_sort = teachers_query.order_by(Teacher.rating.desc()).all()
        if sort_type == form.sort_type.choices[2][0]:
            teachers_sort = teachers_query.order_by(Teacher.price.desc()).all()
        if sort_type == form.sort_type.choices[3][0]:
            teachers_sort = teachers_query.order_by(Teacher.price).all()
    else:
        teachers_sort = teachers_query.all()
    return render_template('all.html', teachers=teachers_sort, form=form)


@app.route('/goals/<goal>/')
# здесь будет цель <goal>
def render_goal(goal):
    if not db.session.query(Goal).filter(Goal.name_english == goal).all():
        return render_template('str_404.html', error='Неверно указана цель обучения'), 404
    teachers_goal = []
    teachers_all = db.session.query(Teacher).order_by(Teacher.rating.desc()).all()
    goal_tek = db.session.query(Goal).filter(Goal.name_english == goal).scalar()
    for teacher in teachers_all:
        if goal_tek in teacher.goals:
            teachers_goal.append(teacher)
#    teachers_goal = db.session.query(Teacher).filter(goal in Teacher.goals.name_english).all()
#        [a for a in teachers if goal in a['goals']] order_by(Teacher.rating.desc()).
    return render_template('goal.html', teachers=teachers_goal, goal=goals_pict[goal])


@app.route('/profiles/<int:teacher_id>/')
# здесь будет преподаватель <id учителя>
def render_profile(teacher_id):
    teacher_query = db.session.query(Teacher).get_or_404(teacher_id, description='Неверно указан код преподавателя')
    teacher = {
        "id": teacher_query.id,
        "name": teacher_query.name,
        "about": teacher_query.about,
        "rating": teacher_query.rating,
        "picture": teacher_query.picture,
        "price": teacher_query.price,
        "goals": [goal.name_english for goal in teacher_query.goals],
        "free": eval(teacher_query.free)
    }
    return render_template('profile.html', teacher=teacher, goals=goals_pict, days_of_week=days_of_week)


@app.route('/request/', methods=["POST", "GET"])
# здесь будет заявка на подбор
def render_request():
    form = FormRequest()
    if form.validate_on_submit():
        goal = goals_pict[form.goal.data][0]
        time = dict(time_have)[form.time.data]
        name = form.name.data
        phone = form.phone.data
        db.session.add(Request(
            learner=name,
            phone=phone,
            goal=db.session.query(Goal).filter(Goal.name_rus == goal).scalar(),
            time=db.session.query(TimeHave).filter(TimeHave.time == time).scalar(),
        ))
        db.session.commit()
        return render_template('request_done.html', request_param=[goal, time, name, phone])
    return render_template('request.html', form=form)


@app.route('/booking/<int:teacher_id>/<day_of_week>/<time_booking>/', methods=["POST", "GET"])
#  здесь будет форма бронирования <id учителя>
def render_booking(teacher_id=None, day_of_week=None, time_booking=None):
    form = BookingToTeacher()
    if form.validate_on_submit():
        print("booking.validate_on_submit()")
        days = dict([(day_rus_eng[1], [day_rus_eng[0], day_eng]) for day_eng, day_rus_eng in days_of_week.items()])
        day = days[form.weekday.data][0]
        time = form.time.data + ":00"
        name = form.name.data
        phone = form.phone.data
        booking_param = [day, time, name, phone]
        db.session.add(Booking(
            learner=name,
            phone=phone,
            weekday=db.session.query(WeekDay).filter(WeekDay.name_english_long == day_of_week).scalar(),
            time=time,
            teacher=db.session.query(Teacher).get(teacher_id),
        ))
        db.session.commit()
        return render_template('booking_done.html', booking_param=booking_param)
    teacher_query = db.session.query(Teacher).get_or_404(teacher_id, description='Неверно указан код преподавателя')
    days = dict((day_eng, day_rus) for day_rus, day_eng in days_of_week.values())
    if request.method == "GET" and (
            (day_of_week not in days.keys()) or
            not free_time_exist(teacher_id, day_of_week, time_booking + ":00")):
        return render_template('str_404.html', error='Неверно указаны день недели или время бронирования'), 404
    day_booking = [days[day_of_week], day_of_week]
    form.weekday.data = day_of_week
    form.time.data = time_booking
    form.teacher.data = str(teacher_id)
    return render_template('booking.html', teacher=teacher_query, day_booking=day_booking, form=form)


@app.errorhandler(404)
def render_not_found(error):
    return render_template('str_404.html', error=error), 404


if __name__ == '__main__':
    app.run(debug=True)
