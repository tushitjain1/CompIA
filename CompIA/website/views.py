from os import error
import re
from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from sqlalchemy.sql.schema import Table
from werkzeug.utils import redirect
from .models import *
from . import db
from .models import *
from .algorithm.exams import exams
from .algorithm.times import timess
from .algorithm import fc

validSubjects = []
validSubjectsid = []

views = Blueprint('views',__name__)

@views.route('/', methods = ['POST','GET'])
@login_required
def home():
    global validSubjects 
    global validSubjectsid 
    if request.method == 'GET':
        fc.solution=[]
        newSubject=""
        delete =""
        delSlot =""
    if request.method == 'POST':
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
        if numDays != "":
            numDays= int(numDays)
            db.session.query(User).filter(User.id==current_user.id).update({User.days:numDays})
            db.session.commit()
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
            pap1 = duration(duration=newSubject1, org_id=current_user.org_id,subject_id=sub_id.id,paper_id=1)
            pap2 = duration(duration=newSubject2, org_id=current_user.org_id,subject_id=sub_id.id,paper_id=2)
            pap3 = duration(duration=newSubject3, org_id=current_user.org_id,subject_id=sub_id.id,paper_id=3)
            sub_org = subject_organisation(subjectId=sub_id.id,org_id=current_user.org_id)
            db.session.add(sub_org)
            db.session.add(pap1)
            db.session.add(pap2)
            db.session.add(pap3)
            db.session.commit()
        if changeSubjectID != "":
            for i in [sub1,sub2,sub3]:
                if i == "":
                    i=0
            if newSubName != "":
                toChange = validSubjectsid[int(changeSubjectID)-1]
                db.session.query(Subjects).filter(Subjects.id==toChange).\
                    update({Subjects.name:newSubName}, synchronize_session=False)

            db.session.query(duration).filter(duration.subject_id==toChange,duration.org_id==current_user.org_id,duration.paper_id==1).\
                update({duration.duration:sub1}, synchronize_session=False)

            db.session.query(duration).filter(duration.subject_id==toChange,duration.org_id==current_user.org_id,duration.paper_id==2).\
                update({duration.duration:sub2}, synchronize_session=False)

            db.session.query(duration).filter(duration.subject_id==toChange,duration.org_id==current_user.org_id,duration.paper_id==3).\
                update({duration.duration:sub3},synchronize_session=False)
            db.session.commit()

        if delete != "":
            toDelete = validSubjectsid[int(delete)-1]
            del1 = Subjects.query.filter_by(id=toDelete).first()
            del2 = subject_organisation.query.filter_by(subjectId=toDelete,org_id=current_user.org_id).first()
            del3 = duration.query.filter_by(subject_id=toDelete,paper_id=1).first()
            del4 = duration.query.filter_by(subject_id=toDelete,paper_id=2).first()
            del5 = duration.query.filter_by(subject_id=toDelete,paper_id=3).first()
            for j in [del1,del2,del3,del4,del5]:
                db.session.delete(j)
            db.session.commit()
        
        if delSlot != "":
            toDelete = int(delSlot)
            delArr = timeslots.query.filter_by(org_id=current_user.org_id).all()
            delete = delArr[toDelete-1]
            db.session.delete(delete)
            db.session.commit()

        if startTime != "" and endTime != "":
            newSlot = timeslots(start=int(startTime),end=int(endTime),org_id=current_user.org_id)
            db.session.add(newSlot)
            db.session.commit()
        elif (startTime != "" and endTime == "") or (startTime == "" and endTime != ""):
            flash("Invalid",category="error")

    validSubjects = []
    validSubjectsid = []
    validSubjects += subject_organisation.query.filter_by(org_id=current_user.org_id).all()
    for i in validSubjects:
        validSubjectsid.append(i.subjectId)
    option = []
    subjects = db.session.query(Subjects).filter(Subjects.id.in_(validSubjectsid)).all()
    subsToPass = []
    for i in subjects:
        subsToPass.append(i.name)
        option.append(i.option)
    durationsorg = duration.query.filter_by(org_id=current_user.org_id).all()
    validDuration = []
    for i in durationsorg:
        validDuration.append(i.duration)
    time = timeslots.query.filter_by(org_id=current_user.org_id).all()
    return render_template("home.html", user=current_user, subjects = subsToPass, durations = validDuration, option = option, times = time)

@views.route('/load/',methods=['POST','GET'])
def load():
    days = User.query.filter_by(org_id=current_user.org_id).first()
    htmlTimes = timeslots.query.filter_by(org_id=current_user.org_id).all()
    stringList = []
    tempList = stores.query.filter_by(org_id=current_user.org_id).all()
    for i in tempList:
        subject = Subjects.query.filter_by(id=i.subject_id).first()
        timeslot = timeslots.query.filter_by(id=i.timeslot_id).first()
        stringList.append((subject.name,i.day,timeslot.start,timeslot.end,i.paper_id))
    return render_template('load.html',user=current_user, days=days.days,times=htmlTimes,output=stringList)

@views.route('/calculate/',methods=['POST','GET'])
def calculate():
    global validSubjectsid
    if request.method == 'GET':
        fc.solution=[]
    subjects = db.session.query(Subjects).filter(Subjects.id.in_(validSubjectsid)).all()
    subsToPass = []
    for i in range(len(subjects)-1):
        durations = duration.query.filter_by(org_id=current_user.org_id,subject_id=validSubjectsid[i]).all()
        dur1= durations[0].duration
        dur2= durations[1].duration
        dur3= durations[2].duration
        subsToPass.append((subjects[i].name,subjects[i].option,dur1,dur2,dur3))
    days = User.query.filter_by(id=current_user.id).first()
    counter = 0
    accessTimes = timeslots.query.filter_by(org_id=current_user.org_id).all()
    timeSlots = []
    for i in range(days.days):
        for j in range(len(accessTimes)):
            if counter == len(accessTimes):
                counter = 0
            temp = timess(accessTimes[counter].start,accessTimes[counter].end,str(i+1))
            timeSlots.append(temp)
            counter +=1

    htmlTimes = timeslots.query.filter_by(org_id=current_user.org_id).all()

    objectList = []
    for i in subsToPass:
        x = exams(i[0],[timeSlots,[0]*(len(timeSlots))],i[1],i[2],1) #new object exam (name,domain,option,duration,papernumber)
        y = exams(i[0],[timeSlots,[0]*(len(timeSlots))],i[1],i[3],2)
        z = exams(i[0],[timeSlots,[0]*(len(timeSlots))],i[1],i[4],3)
        tempList = [x,y,z]
        for j in tempList:
            if j.duration != 0:
                objectList.append(j)

    constraints = []
    for objects in objectList:
        for compared in objectList:            
            if compared.option != objects.option:
                constraints.append((objects,compared))
            if compared.name == objects.name:
                constraints.append((objects,compared))
        for times in timeSlots:
            if (objects.duration)/60 > (times.timeEnd-times.timeStart):
                constraints.append((objects,times))
    fc.Search_FC(objectList,1,constraints)
    stringList = []
    for i in fc.solution:
        stringList.append((i[0].name,int(i[1].day),int(i[1].timeStart),int(i[1].timeEnd), i[0].paperNumber))
    if fc.solution==[]:
        flash("Not possible in the Number of Day's/Time slots", category="error")
    if request.method == 'POST':
        toDelete = stores.query.filter_by(org_id=current_user.org_id).all()
        if toDelete != []:
            for j in toDelete:
                db.session.delete(j)
            db.session.commit()
        for i in fc.solution:
            sub_id = Subjects.query.filter_by(name=i[0].name).first()
            time_id = timeslots.query.filter_by(start=i[1].timeStart,org_id=current_user.org_id).first()
            newExam = stores(subject_id=sub_id.id,org_id=current_user.org_id,paper_id=i[0].paperNumber,timeslot_id=time_id.id,day=int(i[1].day))
            db.session.add(newExam)
        db.session.commit()
    return render_template('table.html',user=current_user, days=days.days,times=htmlTimes,output=stringList)
