from flask import render_template, url_for, flash, redirect, request
from minor import app, mail, db
from minor.forms import (RegistrationForm, LoginForm,
                         ResetForm, PasswordForm, PostForm)
from minor.models import User, Post
from flask_mail import Message
import bcrypt
import os
from flask_login import login_user, current_user, logout_user, login_required
import sqlite3
from minor.collect_face_data import collectData
from minor.facelockdoor import faceUnlock, training
connection = sqlite3.connect('minor/database.db', check_same_thread=False)


@app.route('/')
def home():

    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(fullname=form.name.data, email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.confirmation_token()
        send_confirmation(token)
        flash(f'confirmation mail is send to the email account')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and form.password.data == user.password:
            login_user(user, remember=form.remember.data)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Unsuccessful login check email or password!', 'danger')
    return render_template('login.html', form=form)


@app.route("/confirmation/<token>", methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_confirmation_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
    user.confirm = 1
    db.session.commit()
    flash(f'Account Verified Successfully!', 'success')
    return redirect(url_for('login'))


def send_confirmation(token):
    msg = Message('localhost:5000/confirmation/{}'.format(token),
                  recipients=['godiyalanu@gmail.com'])
    mail.send(msg)
    return None


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/resetpassword', methods=['GET', 'POST'])
def reset_password():
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('No account is registered with that email id', 'warning')
        else:
            token = user.confirmation_token()
            send_forget_password(token)
            flash('Email is sent to registered mail for further instruction!', 'info')
            return redirect(url_for('home'))

    return render_template('resetpassword.html', form=form)


@app.route("/resetpassword/<token>", methods=['GET', 'POST'])
def forget_token(token):
    user = User.verify_confirmation_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('login'))
    form = PasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('password.html', form=form)


def send_forget_password(token):
    msg = Message('localhost:5000/resetpassword/{}'.format(token),
                  recipients=['godiyalanu@gmail.com'])
    mail.send(msg)
    return None


@app.route("/posts/newpost", methods=['GET', 'POST'])
@login_required
def newpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been Created!', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', form=form)


@app.route('/addevent', methods=['GET', 'POST'])
@login_required
def addevent():
    if request.method == 'GET':
        return render_template('addevent.html', message=[''])
    else:
        cursor = connection.cursor()
        eventName = request.form['inputEvent']
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS events(
        pk integer PRIMARY KEY AUTOINCREMENT,
        eventName varchar(16),
        organiser varchar(32)
        );'''
        )
        cursor.execute(
            'select * from events;'
        )
        data = cursor.fetchall()
        eventExists = False
        for i in data:
            if eventName == i[1][:-1]:
                eventExists = True
        if eventExists:
            return(render_template('addevent.html', message=['Event With that name alredy Exists.']))
        else:
            query = "INSERT INTO events(eventName , organiser) values('" + \
                eventName + " ', '" + current_user.fullname + "');"
            cursor.execute(query)
            connection.commit()
            cursor.close()
            return(render_template('addevent.html', message=['Event Added Successfully']))


@app.route('/addmember', methods=['GET', 'POST'])
@login_required
def addmember():
    cursor = connection.cursor()
    cursor.execute(
        'select DISTINCT eventName from events'
    )
    data = cursor.fetchall()
    eventList = list(_[0] for _ in data)
    if request.method == 'GET':
        if len(eventList) == 0:
            return render_template('addmember.html', eventList=eventList,  message=['Please add some Events First.'])
        else:
            return render_template('addmember.html', eventList=eventList,  message=[''])
    else:
        if (len(request.form['inputName']) == request.form['inputName'].count(" ") or int(request.form['inputAge']) < 0):
            return render_template('addmember.html', eventList=eventList,  message=['Please enter Valid Details.'])
        else:
            cursor = connection.cursor()
            formData = request.form
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS members(
            uniqueID varchar PRIMARY KEY,
            memberName varchar(16),
            age varchar(3),
            event varchar(32),
            state varchar(5)
            );'''
            )
            cursor.execute(
                'select * from members where uniqueID = "' +
                request.form['inputID'] + '";'
            )
            data = cursor.fetchall()
            if len(data) > 0:
                connection.commit()
                cursor.close()
                return render_template('addmember.html', eventList=eventList,  message=['This Person is already registered.'])
            else:
                os.mkdir('./minor/FaceData/' + str(request.form['inputID']))
                resultFaceData = collectData(request.form['inputID'])
                if resultFaceData:
                    cursor.execute(
                        'INSERT INTO members( uniqueID , memberName, age, event,state) values("' +
                        request.form['inputID'] + '","' + request.form['inputName'] + '","' +
                        request.form['inputAge'] + '","' +
                        request.form['inputEvent'] + '","OUT");'
                    )
                    connection.commit()
                    cursor.close()
                    return render_template('addmember.html', eventList=eventList,  message=['Person Registered Successfully.'])
                else:
                    return render_template('addmember.html', eventList=eventList,  message=['An Error occured while collecting Face Data. Please try again.'])


@app.route('/verifyentry', methods=['GET', 'POST'])
def verifyentry():
    cursor = connection.cursor()
    cursor.execute(
        'select DISTINCT eventName from events'
    )
    data = cursor.fetchall()
    eventList = list(_[0] for _ in data)
    if request.method == 'GET':
        return render_template('verifyentry.html', eventList=eventList, message=[''])
    else:
        cursor = connection.cursor()
        cursor.execute(
                '''CREATE TABLE IF NOT EXISTS members(
            uniqueID varchar PRIMARY KEY,
            memberName varchar(16),
            age varchar(3),
            event varchar(32),
            state varchar(5)
            );'''
            )
        formData = request.form
        cursor.execute(
            'select * from members where uniqueID = "' + formData['inputID'] + '" AND event = "' + formData['inputEvent'] +'";'
        )
        data = cursor.fetchall()
        if (len(data) == 0 ):
            return render_template('error.html', message=['This person is not invited in this event.' ,' ' ,' '])
        else:
            print(data[0])
            userID = data[0][0]
            model = training(userID)
            door = faceUnlock(model,userID)
            print(door)
            if door:
                return render_template('error.html', message=['Access Granted!', 'Have Fun in the event!','Face is matching with database. Door is opening for 5 seconds'])
            else:
                return render_template('error.html', message=['Access Denied!', 'Please Try Again!',' '])

    