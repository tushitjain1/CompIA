from os import pathsep
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    org_id = db.Column(db.Integer)
    days = db.Column(db.Integer)

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))

class subject_organisation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subjectId = db.Column(db.Integer)
    org_id = db.Column(db.Integer)

class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    option = db.Column(db.Integer)

class duration(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    duration = db.Column(db.Integer)
    org_id = db.Column(db.Integer)
    subject_id = db.Column(db.Integer)
    paper_id = db.Column(db.Integer)

class timeslots(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    org_id = db.Column(db.Integer)

class stores(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subject_id = db.Column(db.Integer)
    org_id = db.Column(db.Integer)
    paper_id = db.Column(db.Integer)
    timeslot_id = db.Column(db.Integer)
    day = db.Column(db.Integer)