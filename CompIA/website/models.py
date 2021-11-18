# Imports
from . import db
from flask_login import UserMixin

# Table format for User table in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    org_id = db.Column(db.Integer)
    days = db.Column(db.Integer)

# Table format for Organisation table in the database
class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))

# Table format for subject_organisation table in the database
class subject_organisation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subjectId = db.Column(db.Integer)
    org_id = db.Column(db.Integer)

# Table format for Subject table in the database
class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    option = db.Column(db.Integer)

# Table format for duration table in the database
class duration(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    duration = db.Column(db.Integer)
    org_id = db.Column(db.Integer)
    subject_id = db.Column(db.Integer)
    paper_id = db.Column(db.Integer)

# Table format for timeslots table in the database
class timeslots(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    org_id = db.Column(db.Integer)

# Table format for stores table in the database
class stores(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subject_id = db.Column(db.Integer)
    org_id = db.Column(db.Integer)
    paper_id = db.Column(db.Integer)
    timeslot_id = db.Column(db.Integer)
    day = db.Column(db.Integer)