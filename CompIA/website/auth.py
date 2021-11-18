# Imports 
from flask import Blueprint, render_template, request
from flask.helpers import flash, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash


# Flask blueprints
auth = Blueprint('auth', __name__)


# Primary HTML login page
@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        email = None
        password = None
    if request.method == 'POST':

        # Getting form data from the HTML page
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        # If user is validated, they are re-routed to the home page
        if user:
            if check_password_hash(user.password, password):
                flash('Login successful!', category='success')
                login_user(user, remember=False)
                return redirect(url_for('views.home'))
            else:
                flash('Wrong Password!', category='error')
        else:
            flash('Account does not exist!', category='error')
    return render_template("login.html", user=current_user)


# Secondary HTML logout link
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Secondary HTML sign-up page
@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    # Setting up a new or pre-existing organisation
    temp = db.session.query(Organisation.name).all()
    org = []
    for i in temp:
        org += i
    del org[0]
    if request.method == 'GET':
        email = None
        firstName = None
        password1 = None
        password2 = None
    if request.method == 'POST':

        # Getting form data from the HTML page
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()

        # Validating user inputs
        if user:
            flash('Account with this email already exists', category='error')
        elif len(email) < 4:
            flash('Email must contain more than 4 characters', category='error')
        elif len(firstName) < 2 or firstName == None:
            flash('Name must contain more than 2 characters', category='error')
        elif password1 != password2:
            flash('Passwords dont match', category='error')
        elif len(password1) < 7 or password1 == None:
            flash('Password must contain more than 6 characters', category='error')
        else:

            # Checking if user made a new Organisation
            flag = False
            if request.form.get('addOrg') == "":
                organisation = request.form.get('org')
            else:
                organisation = request.form.get('addOrg')
                newOrg = Organisation(name=organisation)
                db.session.add(newOrg)
                db.session.commit()
                flag = True
            to_send = Organisation.query.filter_by(name=organisation).first()
            temp2 = subject_organisation.query.filter_by(org_id=1).all()

            # Adding new user to the database with preset subjects and time slots
            if flag == True:
                for i in range(len(temp2)):
                    temp3 = subject_organisation(subjectId=temp2[i].subjectId, org_id=to_send.id)
                    dur1 = duration(duration=70, org_id=to_send.id, subject_id=temp2[i].id, paper_id=1)
                    dur2 = duration(duration=135, org_id=to_send.id, subject_id=temp2[i].id, paper_id=2)
                    dur3 = duration(duration=0, org_id=to_send.id, subject_id=temp2[i].id, paper_id=3)
                    for j in [dur1, dur2, dur3, temp3]:
                        db.session.add(j)
                    db.session.commit()
                slot1 = timeslots(start=9, end=10, org_id=to_send.id)
                slot2 = timeslots(start=11, end=12, org_id=to_send.id)
                slot3 = timeslots(start=13, end=14, org_id=to_send.id)
                for j in [slot1, slot2, slot3]:
                    db.session.add(j)
                db.session.commit()
            newUser = User(email=email, password=generate_password_hash(password1, method="sha256"), name=firstName,
                           org_id=to_send.id, days=8)
            db.session.add(newUser)
            db.session.commit()
            flash('Account Created', category='success')

            # Logging in the new user
            login_user(newUser, remember=False)
            return redirect(url_for('views.home'))
    return render_template("signUp.html", user=current_user, orgs=org)
