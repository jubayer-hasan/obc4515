from crypt import methods
import os
from tokenize import group
from app import app, db
from load_model import predict
from models import User, Record
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import select, update, delete, values

basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'super_user' in session:
        return redirect(url_for('dashboard'))
    elif request.method == "POST":
        id = request.form.get('ID')
        password = request.form.get('Password')

        if id == 'super_admin' and password == '#admin':
            session['super_user'] = {"name":"super_admin","rank":'snk',"unit":'abcd',"soinik_number":123456}
            return redirect(url_for('dashboard'))
        else:
            user = User.query.get(id)
            print(user.soinik_number)
            if user == None or user.password != password:
                return render_template('login.html', msg='userId and password do not match')
            else:
                session['user'] = user.soinik_number
                return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'super_user' in session:
        users = User.query.all()
        print(users)
        return render_template('dashboard.html', users=users, length=len(users), super_user=True)
    elif 'user' in session:
        users = User.query.all()
        print(users)
        return render_template('dashboard.html', users=users, length=len(users), super_user=False)
    else:
        return redirect(url_for('login'))


@app.route('/add_new_entry', methods=['GET', 'POST'])
def add_new_entry():
    if 'super_user' in session:
        if request.method == "POST":
            soinik_number = request.form.get('soinik_number')
            rank = request.form.get('rank')
            name = request.form.get('name')
            unit = request.form.get('unit')

            print(soinik_number, rank, name, unit)
            if soinik_number.isdigit():
                new_user = User(soinik_number, rank, name, unit)
                check = User.query.get(soinik_number)

                if check != None:
                    return render_template('add_new_entry.html', msg="soinik number already exist")

                try:
                    db.session.add(new_user)
                    db.session.commit()
                    return render_template('add_new_entry.html', msg="new entry has been added successfully")
                except:
                    return render_template('add_new_entry.html', msg="Oops failed to add the new entry")
            else:
                return render_template('add_new_entry.html', msg="soinik number must be an integer")

        else:

            return render_template('add_new_entry.html')
    else:
        return redirect(url_for('login'))


@app.route('/check_error', methods=['GET', 'POST'])
def upload_image():
    if 'super_user' in session:
        if request.method == "POST":
            soinik_number = request.form.get('soinik_number')
            date = request.form.get('date')
            firing_range = request.form.get('firing_rng')
            session['temp'] = {"soinik_number": soinik_number,
                               'date': date, "firing_range": firing_range}
            return redirect(url_for('entry'))

        else:
            return render_template('check_error.html')
    else:
        return redirect(url_for('login'))


@app.route('/entry', methods=['GET', 'POST'])
def entry():
    if 'super_user' in session:
        if request.method == 'POST':
            image = request.files['file']
            dir_path = 'static/uploads/'
            grouping = request.form.get('grouping')
            soinik_number = session['temp']['soinik_number']
            date = session['temp']['date']
            firing_range = session['temp']['firing_range']
            curr_user = User.query.get(soinik_number)
            dir_path = os.path.join(dir_path, soinik_number+'/'+date+'/')
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            count = len(os.listdir(dir_path))
            image_path = os.path.join(
                dir_path, str(count+1)+'-'+image.filename)
            image.save(image_path)
            date_time_object = datetime.strptime(
                date.replace('-', '/'), '%Y/%m/%d')
            file_name = str(count+1)+'-'+image.filename
            error = predict('static/uploads/'+soinik_number +
                            '/'+date+'/' + file_name)
            if error == 'Vertical Error':
                curr_user.vertical_error_count = curr_user.vertical_error_count + 1
            else:
                curr_user.horizontal_error_count = curr_user.horizontal_error_count + 1

            curr_user.total_firing_count = curr_user.total_firing_count + 1
            db.session.add(curr_user)
            db.session.commit()
            new_record = Record(soinik_number, date_time_object,
                                count+1, file_name, firing_range, grouping, error)
            db.session.add(new_record)
            db.session.commit()
            return render_template('entry.html', soinik_number=session['temp']['soinik_number'])
        else:
            return render_template('entry.html', soinik_number=session['temp']['soinik_number'])
    else:
        return redirect(url_for('login'))



@app.route('/display_image/<soinik_number>/<date>/<file_name>')
def display_image(soinik_number, date, file_name):
    print(soinik_number, date, file_name)
    return redirect(url_for('static', filename='uploads/'+soinik_number+'/'+date+'/'+file_name), code=301)




@app.route('/analysis_record', methods=['GET', 'POST'])
def calculate_grouping():
    if 'super_user' in session:
        if request.method == "POST":
            soinik_number = request.form.get('soinik_number')
            from_ = request.form.get('from')
            to = request.form.get('to')
            records = Record.query.filter(Record.soinik_number == soinik_number, db.func.date(
                Record.date) >= from_, db.func.date(Record.date) <= to).all()
            print(records)
            vertical_count = 0
            horizontal_count = 0
            total_firing_count = len(records)

            for record in records:
                if record.error == 'Vertical Error':
                    vertical_count += 1
                else:
                    horizontal_count += 1
            return render_template('show_record_analysis.html', super_user=True, from_=from_, to=to, soinik_number=soinik_number, vertical_count=vertical_count, horizontal_count=horizontal_count, total_firing_count=total_firing_count)
        else:
            return render_template('analysis_record.html', super_user=True)
    elif 'user' in session:
        if request.method == 'POST':
            soinik_number = request.form.get('soinik_number')
            from_ = request.form.get('from')
            to = request.form.get('to')
            records = Record.query.filter(Record.soinik_number == soinik_number, db.func.date(
                Record.date) >= from_, db.func.date(Record.date) <= to).all()

            vertical_count = 0
            horizontal_count = 0
            total_firing_count = len(records)

            for record in records:
                if record.error == 'Vertical Error':
                    vertical_count += 1
                else:
                    horizontal_count += 1
            return render_template('show_record_analysis.html', super_user=False, from_=from_, to=to, soinik_number=soinik_number, vertical_count=vertical_count, horizontal_count=horizontal_count, total_firing_count=total_firing_count)
        else:
            return render_template('analysis_record.html', super_user=False)
    else:
        return redirect(url_for('login'))


@app.route('/check_record', methods=["GET", "POST"])
def analysis_error():
    if 'super_user' in session:
        if request.method == "POST":
            soinik_number = request.form.get('soinik_number')
            date = request.form.get('date')
            records = Record.query.filter(Record.soinik_number == soinik_number, db.func.date(
                Record.date) == date).all()

            print(records)
            
            return render_template('show_record.html',super_user=True,ln=len(records),records=records)
        else:
            return render_template('check_record.html',super_user=True)

    elif 'user' in session:
        if request.method == "POST":
            soinik_number = request.form.get('soinik_number')
            date = request.form.get('date')
            
            records = Record.query.filter(Record.soinik_number == soinik_number, db.func.date(
                Record.date) == date).all()

            print(records)
            
            return render_template('show_record.html',super_user=False,ln=len(records),records=records)
        else:
            return render_template('check_record.html',super_user=False)
    else:
        return redirect(url_for('login'))



@app.route('/update_profile', methods=["GET", "POST"])
def update_profile():
    if 'super_user' in session:
        if request.method == 'POST':
            soinik_number = request.form.get('soinik_number')
            rank = request.form.get('rank')
            name = request.form.get('name')
            unit = request.form.get('unit')
            image = request.files['file']
            user = User.query.get(soinik_number)
            if user == None:
                return render_template('update_profile.html',super_user=True,msg="User doesn't exist")

            else:
                dir_path = 'static/uploads/profile_photo'
                dir_path = os.path.join(dir_path, soinik_number+'/')
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                image_path = os.path.join(
                    dir_path, image.filename)
                image.save(image_path)
                file_name = image.filename
                user.rank = rank
                user.name = name
                user.unit = unit
                user.photo = file_name
                db.session.add(user)
                db.session.commit()
                return render_template('update_profile.html',super_user=True,msg="successfully updated profile")
            
        else:
            return render_template('update_profile.html',super_user=True)
    elif 'user' in session:
        if request.method == 'POST':
            soinik_number = request.form.get('soinik_number')
            rank = request.form.get('rank')
            name = request.form.get('name')
            unit = request.form.get('unit')
            image = request.files['file']
            user = User.query.get(soinik_number)
            if user == None:
                return render_template('update_profile.html',super_user=False,msg="User doesn't exist")

            else:
                dir_path = 'static/uploads/profile_photo'
                dir_path = os.path.join(dir_path, soinik_number+'/')
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                image_path = os.path.join(
                    dir_path, image.filename)
                image.save(image_path)
                file_name = image.filename
                user.rank = rank
                user.name = name
                user.unit = unit
                user.photo = file_name
                db.session.add(user)
                db.session.commit()
                return render_template('update_profile.html',super_user=False,msg="successfully updated profile")
        else:
            return render_template('update_profile.html',super_user=False)
    else:
        return redirect(url_for('login'))

@app.route('/display_picture/<soinik_number>/<file_name>')
def display_picture(soinik_number,file_name):
    print(soinik_number, file_name)
    return redirect(url_for('static', filename='uploads/profile_photo/'+soinik_number+'/'+file_name), code=301)

@app.route('/profile')
def profile():
    if 'super_user' in session:
        return render_template('profile.html',super_user=True,user=session['super_user'])
    elif 'user' in session:
        user = User.query.get(session['user'])
        return render_template('profile.html',super_user=False,user=user)
    else:
        return redirect(url_for('login'))


@app.route('/erase_data',methods=['POST'])
def erase_date():
    if 'super_user' in session:
        if request.method == 'POST':
            soinik_number = request.form.get('soinik_number')
            sql1 = delete(User).where(User.soinik_number == soinik_number)
            sql2 = delete(Record).where(Record.soinik_number == soinik_number)

            db.session.execute(sql1)
            db.session.commit()
            db.session.execute(sql2)
            db.session.commit()
            return render_template('update_profile.html',super_user=False,msg="successfully deleted profile")
    else:
        return redirect(url_for('login'))



@app.route('/logout')
def logout():
    session.pop('super_user', None)
    session.pop('user', None)
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    return '<h1>Page not Found<h1>'


if __name__ == "__main__":
    app.run(debug=True)
