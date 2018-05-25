import flask
from flask import Flask, Response, render_template, request, redirect, flash, url_for
from flaskext.mysql import MySQL
import flask_login
from flask_login import current_user
import geocoder

app = Flask(__name__)
mysql = MySQL()

#may be different depending on user system!
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
app.config['MYSQL_DATABASE_DB'] = 'ADVERTISING'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.secret_key = 'QgW7*,F:2q}aF+U'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM User")
    return cursor.fetchall()
class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return 
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user    
# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if flask.request.method == "GET":
        return '''
        <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='password' id='password' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form></br>
               <a href="/register">Make an account</a>
           <a href='/'>Home</a>
           '''
    email = flask.request.form['email']
    cursor = conn.cursor()
    if cursor.execute("SELECT password FROM USER WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user) 
            return flask.redirect(flask.url_for('users', email = email))
        #return render_template("hello.html", name = getName(email))
    return "<a href='/login'>Try again</a>\</br><a href='/register'> or make and account </a>"

@app.route("/settings")
@flask_login.login_required
def settings():
    pass

@app.route("/logout")
@flask_login.login_required
def logout():
    logout_user()
    return redirect(somewhere)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

@app.route("/register", methods=['GET','POST'])
def register():
    if flask.request.method=='GET':
        return render_template('register.html')

    elif flask.request.method=="POST":
        try:
            fname = request.form.get('first-name')
            lname = request.form.get('last-name')
            email = request.form.get('email')
            password = request.form.get('password')
            hometown = request.form.get('hometown')

        except:
            print(
                "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
            return flask.redirect(flask.url_for('register'))
        if isEmailUnique(email):
            # gender, email, password, dob, hometown, fname, lname
            cursor = conn.cursor()
            query= "INSERT INTO User(email, password, hometown, fname, lname) VALUES ('{}', '{}', '{}', '{}', '{}')".format(email, password, hometown, fname, lname)
            cursor.execute(query)
            conn.commit()
            # log user in
            user = User()
            user.id = email
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('users', email = email))
            #return render_template('hello.html', name=getName(email), message='Account Created!')
        else:
            print("couldn't find all tokens")
            return flask.redirect(flask.url_for('register'))

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM User WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email FROM User WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def getName(email):
    cursor.execute("SELECT fname, lname FROM User WHERE email = '{0}'".format(email));
    return cursor.fetchall()

@app.route('/addBussiness', methods=["POST"])
@flask_login.login_required
def advertise():
    email = flask_login.current_user.id
    housenum = request.form.get('housenum')
    street = request.form.get('street')
    city = request.form.get('city')
    state = request.form.get('state')
    message = request.form.get('message')
    cursor = conn.cursor()
    query = "INSERT INTO business(email, housenum, street, city, state, message) VALUES ('{}','{}','{}','{}','{}','{}')".format(email, housenum, street, city, state, message)
    cursor.execute(query)
    conn.commit()
    return flask.redirect(flask.url_for('users', email = email))

@flask_login.login_required
def get_locaions(email):
    email = flask_login.current_user.id
    cursor.execute("SELECT housenum, street, city, state FROM business WHERE email = '{0}'".format(email));
    business = cursor.fetchall()
    latlong = []
    #temp = ""
    for i in business:
        temp = ""
        for j in i:
            temp = temp + " " + j
            ' '.join(temp.split())
        g = geocoder.google(temp)
        latlong.append(g.latlng)
    print(latlong)
    return latlong

@flask_login.login_required
def show_inputs(email):
    email = flask_login.current_user.id
    cursor.execute("SELECT housenum, street, city, state FROM business WHERE email = '{0}'".format(email));
    inputs = cursor.fetchall()
    return inputs

@app.route('/delete/<housenum>', methods = ['GET', 'POST'])
@flask_login.login_required
def delete_input(housenum):
    email = flask_login.current_user.id
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BUSINESS WHERE email = '{0}' and housenum = '{1}'".format(email,housenum))
    conn.commit()
    return flask.redirect(flask.url_for('users', email = email))

@flask_login.login_required
def get_user_location():
    email = flask_login.current_user.id
    cursor.execute("SELECT hometown FROM user WHERE email = '{0}'".format(email));
    return cursor.fetchall()

@flask_login.login_required
def geocode_user_location():
    email = flask_login.current_user.id
    city = get_user_location()
    city_state = city[0]
    g = geocoder.google(city_state)
    latlong = g.latlng
    return latlong

@flask_login.login_required
def show_business_message():
    email = flask_login.current_user.id
    cursor.execute("SELECT message FROM business WHERE email ='{0}'".format(email));
    message = cursor.fetchall()
    word = ""
    lst = []
    if message:
        word = word + message[0][0]
        word.replace('( ',"")
        word.replace(')',"")
        lst.append(word)
    else:
        word = word + "This user does not have a message. But you can contact them at: " + str(email)
        lst.append(word)
    return lst

def list_all_businesses():
    cursor.execute("SELECT housenum, street, city, state FROM business")
    all_locations = cursor.fetchall()
    lst = []
    for i in all_locations:
        all_things = ""
        for j in i:
            all_things = all_things + " " + j
            ' '.join(all_things.split())
        print(all_things)
        g = geocoder.google(all_things)
        localall = g.latlng
        lst.append(localall)
    return lst

def list_all_messages():
    cursor.execute("SELECT message FROM business")
    users_messages = cursor.fetchall()
    lst = []
    for i in users_messages:
        all_words = ""
        for j in i:
            all_words = all_words + " " + j
            ' '.join(all_words.split())
        lst.append(all_words)
    return lst

@app.route('/inputComments', methods=['GET', 'POST'])
@flask_login.login_required
def input_comment():
    commenter = flask_login.current_user.id
    place = request.form.get('optionselect')
    comment = request.form.get('comment')
    rate = request.form.get('rate')
    words = place.split()
    print(words)
    cursor.execute("SELECT bid FROM business WHERE housenum = '{}' and state = '{}'".format(words[0],words[-1]));
    the_bid = cursor.fetchall()
    print(the_bid) 
    print(comment)
    query = "INSERT INTO rating(email, rating, comment, bid) VALUES ('{}', '{}', '{}', '{}')".format(commenter,rate,comment,the_bid[0][0])
    cursor.execute(query)
    conn.commit()
    return 'ok'

def list_all_businessess_no_geo():
    cursor.execute("SELECT housenum, street, city, state FROM business")
    all_locations = cursor.fetchall()
    lst = []
    for i in all_locations:
        all_things = ""
        for j in i:
            all_things = all_things + " " + j
            ' '.join(all_things.split())
        lst.append(all_things)
    return lst

@app.route('/')
def users():
    return render_template('hello.html', name = getName(request.args.get('email')), inputs = show_inputs(request.args.get('email')) ,loc = get_locaions(request.args.get('email')),local = geocode_user_location(), msg = show_business_message(), all = list_all_businesses(), messg = list_all_messages(), nogeo = list_all_businessess_no_geo())

if __name__ == '__main__':
    app.run(debug=True)