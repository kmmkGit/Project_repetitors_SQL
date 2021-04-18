import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON

app = Flask(__name__)
app.secret_key = os.urandom(40)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
#    'sqlite:///test_my.db'
#    os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)


teachers_goals_association = db.Table(
    'teachers_goals',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
    db.Column('goal_id', db.Integer, db.ForeignKey('goals.id')),
)


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    about = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String(), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    goals = db.relationship(
        "Goal", secondary=teachers_goals_association, back_populates="teachers"
    )
#    free = db.Column(JSON, nullable=False)
    free = db.Column(db.String(), nullable=False)
    booking = db.relationship(
        "Booking", back_populates="teacher"
    )


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    name_english = db.Column(db.String(50), unique=True, nullable=False)
    name_rus = db.Column(db.String(50), unique=True, nullable=False)
    picture = db.Column(db.String(1), nullable=False)
    teachers = db.relationship(
        "Teacher", secondary=teachers_goals_association, back_populates="goals"
    )
    request = db.relationship(
        "Request", back_populates="goal"
    )


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    learner = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    weekday_id = db.Column(db.Integer, db.ForeignKey('weekdays.id'))
    weekday = db.relationship(
        "WeekDay", back_populates="bookings"
    )
    time = db.Column(db.String(5), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    teacher = db.relationship(
        "Teacher", back_populates="booking"
    )


class Request(db.Model):
    __tablename__ = "requests"

    id = db.Column(db.Integer, primary_key=True)
    learner = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    goal = db.relationship(
        "Goal", back_populates="request"
    )
    time_id = db.Column(db.Integer, db.ForeignKey('times_have.id'))
    time = db.relationship(
        "TimeHave", back_populates="requests"
    )


class TimeHave(db.Model):
    __tablename__ = "times_have"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(25), unique=True, nullable=False)
    requests = db.relationship(
        "Request", back_populates="time"
    )


class WeekDay(db.Model):
    __tablename__ = "weekdays"

    id = db.Column(db.Integer, primary_key=True)
    name_english_long = db.Column(db.String(9), unique=True, nullable=False)
    name_rus = db.Column(db.String(11), unique=True, nullable=False)
    bookings = db.relationship(
        "Booking", back_populates="weekday"
    )


# Удалить !!!!!!!!!!!!
#db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
