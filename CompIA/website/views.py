# Flask library imports
from flask import Blueprint, render_template, request, flash, make_response
from flask_login import login_required, current_user
from datetime import datetime


# Importing modules from the __init__ package
from .models import *
from . import db
from .models import *
from .algorithm.exams import exams
from .algorithm.times import timess
from .algorithm import fc

# Global Variables  
validSubjects = []
validSubjectsId = []

# Flask Blueprint
views = Blueprint('views', __name__)


# Main HTML homepage route
@views.route('/', methods=['POST', 'GET'])
@login_required
def home():
    # Initialising Global Variables
    global validSubjects
    global validSubjectsId

    # If GET request is received, variables are reset
    if request.method == 'GET':
        fc.solution = []
        newSubject = ""
        delete = ""
        delSlot = ""
        validSubjects = []
        validSubjectsId = []

    # If POSt request is received, data is processed
    if request.method == 'POST':
        # Getting Values from HTML form on the first page
        newSubject = request.form.get('newSubject')
        newSubjectOption = request.form.get('newSubjectOption')
        newSubject1 = request.form.get('newSubject1')
        newSubject2 = request.form.get('newSubject2')
        newSubject3 = request.form.get('newSubject3')
        changeSubjectID = request.form.get('subID')
        newSubName = request.form.get('subName')
        sub1 = request.form.get('sub1')
        sub2 = request.form.get('sub2')
        sub3 = request.form.get('sub3')
        delete = request.form.get('delSubject')
        numDays = request.form.get('numDays')
        startTime = request.form.get('startTime')
        endTime = request.form.get('endTime')
        delSlot = request.form.get('delSlot')

        # User data: Number of Days, is stored in the Database and used
        if numDays != "":
            numDays = int(numDays)
            db.session.query(User).filter(User.id == current_user.id).update({User.days: numDays})
            db.session.commit()

        # User data: New Subject, is stored in the Database and used
        if newSubject1 == "":
            newSubject1 = "0"
        if newSubject2 == "":
            newSubject2 = "0"
        if newSubject3 == "":
            newSubject3 = "0"
        if newSubject != "" and newSubjectOption != "":
            newSub = Subjects(name=newSubject, option=newSubjectOption)
            db.session.add(newSub)
            db.session.commit()
            sub_id = Subjects.query.filter_by(name=newSubject).first()
            pap1 = duration(duration=newSubject1, org_id=current_user.org_id, subject_id=sub_id.id, paper_id=1)
            pap2 = duration(duration=newSubject2, org_id=current_user.org_id, subject_id=sub_id.id, paper_id=2)
            pap3 = duration(duration=newSubject3, org_id=current_user.org_id, subject_id=sub_id.id, paper_id=3)
            sub_org = subject_organisation(subjectId=sub_id.id, org_id=current_user.org_id)
            db.session.add(sub_org)
            db.session.add(pap1)
            db.session.add(pap2)
            db.session.add(pap3)
            db.session.commit()

        # User data: Change subject data, stores new values for pre-existing subjects into the database and for use
        if changeSubjectID != "" and int(changeSubjectID) <= len(validSubjectsId):
            if sub1 == "":
                sub1 = 0
            if sub2 == "":
                sub2 = 0
            if sub3 == "":
                sub3 = 0
            toChange = validSubjectsId[int(changeSubjectID) - 1]
            if newSubName != "":
                db.session.query(Subjects).filter(Subjects.id == toChange). \
                    update({Subjects.name: newSubName}, synchronize_session=False)

            db.session.query(duration).filter(duration.subject_id == toChange, duration.org_id == current_user.org_id,
                                              duration.paper_id == 1). \
                update({duration.duration: sub1}, synchronize_session=False)

            db.session.query(duration).filter(duration.subject_id == toChange, duration.org_id == current_user.org_id,
                                              duration.paper_id == 2). \
                update({duration.duration: sub2}, synchronize_session=False)

            db.session.query(duration).filter(duration.subject_id == toChange, duration.org_id == current_user.org_id,
                                              duration.paper_id == 3). \
                update({duration.duration: sub3}, synchronize_session=False)
            db.session.commit()
        elif changeSubjectID != "" and int(changeSubjectID) > len(validSubjectsId):
            flash("Invalid ID", category="error")

        # User data: Delete a pre-existing subject: chosen subject is deleted from the database
        if delete != "":
            if int(delete) not in validSubjectsId:
                flash("Invalid ID", category="error")
            else:
                toDelete = validSubjectsId[int(delete) - 1]
                del1 = Subjects.query.filter_by(id=toDelete).first()
                del2 = subject_organisation.query.filter_by(subjectId=toDelete, org_id=current_user.org_id).first()
                del3 = duration.query.filter_by(subject_id=toDelete, paper_id=1).first()
                del4 = duration.query.filter_by(subject_id=toDelete, paper_id=2).first()
                del5 = duration.query.filter_by(subject_id=toDelete, paper_id=3).first()
                for j in [del1, del2, del3, del4, del5]:
                    db.session.delete(j)
                db.session.commit()
        if delSlot != "":
            delArr = timeslots.query.filter_by(org_id=current_user.org_id).all()
            if int(delSlot) <= len(delArr):
                toDelete = int(delSlot)
                delete = delArr[toDelete - 1]
                db.session.delete(delete)
                db.session.commit()
            else:
                flash("Invalid!", category="error")

        # User data: time slots, adds time slots to the database to be used later on
        if len(startTime) == 5 and len(endTime) == 5: # time is a string here
            newSlot = timeslots(start=startTime, end=endTime, org_id=current_user.org_id)
            db.session.add(newSlot)
            db.session.commit()

    # Recurses through the users subjects stored in the database in order to be displayed on the home page
    validSubjects = []
    validSubjectsId = []
    validSubjects += subject_organisation.query.filter_by(org_id=current_user.org_id).all()
    for i in validSubjects:
        validSubjectsId.append(i.subjectId)
    option = []
    subjects = db.session.query(Subjects).filter(Subjects.id.in_(validSubjectsId)).all()
    subsToPass = []
    for i in subjects:
        subsToPass.append(i.name)
        option.append(i.option)
    durationsOrg = duration.query.filter_by(org_id=current_user.org_id).all()
    validDuration = []
    for i in durationsOrg:
        validDuration.append(i.duration)
    time = timeslots.query.filter_by(org_id=current_user.org_id).all()
    return render_template("home.html", user=current_user, subjects=subsToPass, durations=validDuration, option=option,
                           times=time)


# Secondary HTML page used to load in saved timetable
@views.route('/load/', methods=['POST', 'GET'])
def load():
    htmlTimes = timeslots.query.filter_by(org_id=current_user.org_id).all()
    stringList = []
    tempList = stores.query.filter_by(org_id=current_user.org_id).all()
    daysArray = []
    for i in tempList:
        subject = Subjects.query.filter_by(id=i.subject_id).first()
        timeslot = timeslots.query.filter_by(id=i.timeslot_id).first()
        stringList.append((subject.name, i.day, timeslot.start, timeslot.end, i.paper_id))
        if i.day not in daysArray:
            daysArray.append(i.day)
    return render_template('load.html', user=current_user, days=len(daysArray), times=htmlTimes, output=stringList)


# Secondary HTML page used to generate and display a new timetable
@views.route('/calculate/', methods=['POST', 'GET'])
def calculate():
    # Initialize Global Variable
    global validSubjectsId

    # Reset solution on GET request
    if request.method == 'GET':
        fc.solution = []

    # Loads in users Subjects from the database
    subjects = db.session.query(Subjects).filter(Subjects.id.in_(validSubjectsId)).all()
    subsToPass = []
    for i in range(len(validSubjectsId) - 1):
        durations = duration.query.filter_by(org_id=current_user.org_id, subject_id=validSubjectsId[i]).all()
        dur1 = durations[0].duration
        dur2 = durations[1].duration
        dur3 = durations[2].duration
        subsToPass.append((subjects[i].name, subjects[i].option, dur1, dur2, dur3))
    days = User.query.filter_by(id=current_user.id).first()
    counter = 0
    accessTimes = timeslots.query.filter_by(org_id=current_user.org_id).all()

    # Generate different time slots as "Timeslot" objects
    timeSlots = []
    for i in range(days.days):
        for j in range(len(accessTimes)):
            if counter == len(accessTimes):
                counter = 0
            temp = timess(accessTimes[counter].start, accessTimes[counter].end, str(i + 1))
            timeSlots.append(temp)
            counter += 1
    htmlTimes = timeslots.query.filter_by(org_id=current_user.org_id).all()

    # Generate "Exams" objects to pass into Forward Search Algorithm
    objectList = []
    for i in subsToPass:
        temp1 = []
        temp2 = []
        temp3 = []
        for k in timeSlots:
            if timeCalc(k.timeStart, k.timeEnd) >= (i[2])/60:
                temp1.append(k)
            if timeCalc(k.timeStart, k.timeEnd) >= (i[3])/60:
                temp2.append(k)
            if timeCalc(k.timeStart, k.timeEnd) >= (i[4])/60: # in hours
                temp3.append(k)

        # new object exam (name,domain,option,duration,papernumber)
        x = exams(i[0], [temp1, [0] * (len(temp1))], i[1], i[2], 1)
        y = exams(i[0], [temp2, [0] * (len(temp2))], i[1], i[3], 2)
        z = exams(i[0], [temp3, [0] * (len(temp3))], i[1], i[4], 3)
        tempList = [x, y, z]
        for j in tempList:
            if j.duration != 0:
                objectList.append(j)

    # Makes constraints between different objects to feed into the Forward search algorithm
    constraints = []
    biggestSlot = timeSlots[0]
    for slot in timeSlots:
        if timeCalc(slot.timeStart,slot.timeEnd) > timeCalc(biggestSlot.timeStart,biggestSlot.timeEnd):
            biggestSlot = slot
    for objects in objectList:
        for compared in objectList:
            if compared.option != objects.option:
                constraints.append((objects, compared))
            if compared.name == objects.name:
                if (compared.duration + objects.duration) / 60 > timeCalc(biggestSlot.timeStart,biggestSlot.timeEnd):
                    constraints.append((objects, compared))
        for times in timeSlots:
            if objects.duration / 60 > timeCalc(times.timeStart,times.timeEnd):
                constraints.append((objects, times))

    # Running the Forward Search algorithm on the given subjects
    fc.Search_FC(objectList, 1, constraints)

    # Obtaining the results of the algorithm
    stringList = []
    daysArray = []
    for i in fc.solution:
        stringList.append((i[0].name, int(i[1].day), i[1].timeStart, i[1].timeEnd, i[0].paperNumber))
        if int(i[1].day) not in daysArray:
            daysArray.append(int(i[1].day))
    sol = True

    # No possible solution
    if not fc.solution:
        flash("Not possible in the Number of Day's/Time slots", category="error")
        sol = False

    # If POST request is received from the HTML page, the timetable is saved
    if request.method == 'POST':
        # Deletes the existing timetable in the database
        toDelete = stores.query.filter_by(org_id=current_user.org_id).all()
        if toDelete:
            for j in toDelete:
                db.session.delete(j)
            db.session.commit()

        # Adds the newly generated timetable to the database
        for i in fc.solution:
            sub_id = Subjects.query.filter_by(name=i[0].name).first()
            time_id = timeslots.query.filter_by(start=i[1].timeStart, org_id=current_user.org_id).first()
            newExam = stores(subject_id=sub_id.id, org_id=current_user.org_id, paper_id=i[0].paperNumber,
                             timeslot_id=time_id.id, day=int(i[1].day))
            db.session.add(newExam)
        db.session.commit()
    return render_template('table.html', user=current_user, days=len(daysArray), times=htmlTimes, output=stringList,
                           sol=sol)


# Function to calculate duration of a time slot
def timeCalc(start, end):
    start_time = datetime(year=2020, month=1, day= 1, hour=int(start[0:2]), minute=int(start[3:]))
    end_time = datetime(year=2020, month=1, day= 1, hour=int(end[0:2]), minute=int(end[3:]))
    difference = end_time-start_time
    return divmod(difference.total_seconds(),3600)[0]   # want result in hours
