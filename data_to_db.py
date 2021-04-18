import json
from app import db, migrate, Teacher, Goal, TimeHave, WeekDay

with open("goals.json", "r", encoding='utf-8') as f:
    goals = json.load(f)
with open("teachers.json", "r", encoding='utf-8') as f:
    teachers = json.load(f)

days_of_week = list(
    map(lambda a, b: (a, b),
        ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
        ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']))
goals_pict = list(map(lambda a, b: [a, b[0], b[1]], goals.keys(), goals.values()))
time_have = [('time1', '1-2 часа в неделю'), ('time2', '3-5 часов в неделю'),
             ('time3', '5-7 часов в неделю'), ('time4', '7-10 часов в неделю')]

for time in time_have:
    db.session.add(TimeHave(time=time[1]))

for day in days_of_week:
    db.session.add(WeekDay(name_english_long=day[0], name_rus=day[1]))

for goal in goals_pict:
    db.session.add(Goal(name_english=goal[0], name_rus=goal[1], picture=goal[2]))
db.session.commit()

for teacher in teachers:
    tek_teacher = Teacher(
        name=teacher["name"],
        about=teacher["about"],
        rating=teacher["rating"],
        picture=teacher["picture"],
        price=teacher["price"],
        free=str(teacher["free"]),
#        free=json.dumps(teacher["free"]),
    )
    db.session.add(tek_teacher)

    for teacher_goal in teacher["goals"]:
        goal = db.session.query(Goal).filter(Goal.name_english == teacher_goal).scalar()
        tek_teacher.goals.append(goal)


db.session.commit()
