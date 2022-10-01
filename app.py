

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import time,datetime
from helper import apology, login_required


app = Flask(__name__)

# Configure application

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///records.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        try:
            db.execute("SELECT * FROM users")
        except:
            db.execute("CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,username TEXT, roll_no INT, hash TEXT,phone INT,email TEXT)")
        username = request.form.get("username")
        roll_no=request.form.get("roll_no")
        passw = request.form.get("password")
        conf = request.form.get("confirmation")
        phone=request.form.get("phone")
        email=request.form.get("email")
        users = db.execute("SELECT username FROM users")
        if username == "":
            return apology("Invalid Username")
        for i in users:
            if username == i['username']:
                return apology("Invalid Username")
        if passw == "":
            return apology("Issue with password")
        if passw != conf:
            return apology("Issue with password")
        if len(roll_no)!=9:
            return apology("Invalid roll no")
        if len(phone)!=10:
            return apology("Invalid phone no")
        hashed = generate_password_hash(passw)
        print(email)
        db.execute("INSERT INTO users (username,hash,roll_no,phone,email) VALUES (:username,:hashed,:roll_no,:phone,:email)",username=username,hashed=hashed,roll_no=roll_no,phone=phone,email=email)
        return render_template("login.html")
    """Register user"""
    return apology("issue in registration")

@app.route("/")
@login_required
def index():
    try:
        db.execute("SELECT * FROM trips")
    except:
        db.execute("CREATE TABLE trips (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,days INT, start_date TEXT , est_cost FLOAT,location TEXT, min_people INT,leader_roll_no INT, description TEXT )")
    try:
        db.execute("SELECT * FROM entries")
    except:
        db.execute("CREATE TABLE entries (id INT, member_roll_no INT,experience TEXT)")
    user=db.execute("SELECT username FROM users WHERE id=?",session["user_id"])[0]['username']
    return render_template("index.html",user=user)

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method=="GET":
        return render_template("create.html")
    elif request.method=="POST":
        days=int(request.form.get("days"))
        if days<=0:
            return apology("Invalid Number Of Days")
        start_date=request.form.get("day")
        est_cost=int(request.form.get("cost"))
        if est_cost<0:
            return apology("Invalid estimated cost")
        location=request.form.get("location")
        min_people=int(request.form.get("people"))
        if min_people<2:
            return apology("Invaid minimun people")
        description=request.form.get("description")
        username = db.execute("SELECT username FROM users WHERE id=?",session["user_id"])[0]['username']
        leader_roll_no=db.execute("SELECT roll_no FROM users WHERE id=?",session["user_id"])[0]['roll_no']
        db.execute("INSERT INTO trips (days,start_date,est_cost,location,min_people,leader_roll_no,description) VALUES (?,?,?,?,?,?,?)",days,start_date,est_cost,location,min_people,leader_roll_no,description)
        return render_template("index.html",user=username)

@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method=="GET":
        valid=db.execute("SELECT id,days,start_date,est_cost,location,min_people,description,leader_roll_no FROM trips")
        #today=str(datetime.datetime.today()).split()[0]
        today=str(datetime.datetime.today()).split(" ")[0]
        to_show=[]
        titles_to_show=['id','days','start_date','est_cost','location','min_people','description']
        our_roll_no=db.execute("SELECT roll_no FROM users WHERE id=?",session["user_id"])[0]['roll_no']
        all_trips=db.execute("SELECT id,days,start_date,est_cost,location,min_people,description,leader_roll_no FROM trips")
        for i in valid:
            if i['leader_roll_no']!=our_roll_no:
                dict={}
                joined=0
                registered=False
                for j in db.execute("SELECT member_roll_no FROM entries WHERE id IS ?",i['id']):
                    if j['member_roll_no']!=our_roll_no:
                        joined+=1
                    else:
                        registered=True
                dict['joined']=joined
                d1=str_to_date(today)+datetime.timedelta(5)
                d2=str_to_date(i['start_date'])
                print("h1",d2,d1)
                if(d2>d1):
                    for j in titles_to_show:
                        dict[j]=i[j]
                    print("h2")
                    if not registered:
                        to_show.append(dict)

                # for j in db.execute("SELECT member_roll_no FROM entries WHERE id IS ?",i['id']):
                #     print(j)
                    # same=False
                    # if j['member_roll_no']==our_roll_no:
                    #     same=True
                    # else:
                    # for i in all_trips:
                    #     if i['leader_roll_no']==our_roll_no:

                    # print(same)
                    # if not same:
                    # d1=str_to_date(today)+datetime.timedelta(5)
                    # d2=str_to_date(i['start_date'])
                    # print("h1",d2,d1)
                    # if(d2>d1):
                    #     for j in titles_to_show:
                    #         dict[j]=i[j]
                    #     print("h2")
                    #     to_show.append(dict)
        exist=False
        if len(to_show)>0:
            exist=True

        last=None
        if len(to_show)%2==1:
            last=to_show.pop()
        dummy=[]
        switch=False
        twice=[]
        for x,i in enumerate(to_show):
            twice.append(i)
            if switch:
                dummy.append(twice)
                twice=[]
            switch=~switch
        to_show=dummy
        return render_template("join.html",to_show=to_show,exist=exist,last=last)
    elif request.method=="POST":
        our_roll_no=db.execute("SELECT roll_no FROM users WHERE id=?",session["user_id"])[0]['roll_no']
        trip_id=request.form.get("trip_id")
        #print(trip_id)
        db.execute("INSERT INTO entries (id,member_roll_no) VALUES (?,?)",trip_id,our_roll_no)
        user=db.execute("SELECT username FROM users WHERE id=?",session["user_id"])[0]['username']
        return render_template("index.html",user=user)


def str_to_date(in_str):
    year,month,date=map(int,in_str.split('-'))
    return datetime.datetime(year,month,date)


@app.route("/mine", methods=["GET","POST"])
@login_required
def mine():
    if request.method=="GET":
        created=False
        registered=False
        username=db.execute("SELECT username FROM users WHERE id=?",session["user_id"])[0]['username']
        our_roll_no=db.execute("SELECT roll_no FROM users WHERE id=?",session["user_id"])[0]['roll_no']
        all_created=[]
        all_trips=db.execute("SELECT id,days,start_date,est_cost,location,min_people,description,leader_roll_no FROM trips")
        for i in all_trips:
            if i['leader_roll_no']==our_roll_no:
                joined=0
                members=[]
                for j in db.execute("SELECT member_roll_no FROM entries WHERE id IS ?",i['id']):
                    if j['member_roll_no']!=our_roll_no:
                        members.append(j['member_roll_no'])
                        joined+=1
                i['joined']=joined
                in_this=[]
                for j in members:
                    name=db.execute("SELECT username FROM users WHERE roll_no is ?",j)[0]['username']
                    phone_no=db.execute("SELECT phone FROM users WHERE roll_no is ?",j)[0]['phone']
                    in_this.append({'name':name,'phone_no':phone_no})
                i['members']=in_this
                all_created.append(i)
        all_registered=[]
        all_entries=db.execute("SELECT id FROM entries WHERE member_roll_no IS ?",our_roll_no)
        print(all_entries)
        for i in all_entries:
            d=db.execute("SELECT * FROM trips WHERE id IS ?",i['id'])
            if len(d)>0:
                all_registered.append(d[0])
        if len(all_trips)>0:
            created=True
        if len(all_registered)>0:
            registered=True

        last_created=None
        if len(all_created)%2==1:
            last_created=all_created.pop()

        last_registered=None
        if len(all_registered)%2==1:
            last_registered=all_registered.pop()

        dummy=[]
        switch=False
        twice=[]
        for i in all_created:
            twice.append(i)
            if switch:
                dummy.append(twice)
                twice=[]
            switch=~switch
        all_created=dummy

        dummy=[]
        switch=False
        twice=[]
        for i in all_registered:
            twice.append(i)
            if switch:
                dummy.append(twice)
                twice=[]
            switch=~switch
        all_registered=dummy
        return render_template("mine.html",username=username,created=created,registered=registered,all_created=all_created,all_registered=all_registered,last_created=last_created,last_registered=last_registered)
    elif request.method == 'POST':
        trip_id=request.form.get('trip_id')
        print(trip_id)
        db.execute("DELETE FROM trips WHERE id IS ?",trip_id)
        request.method="GET"
        return mine()

@app.route("/past", methods=["GET",])
@login_required
def past():
    if request.method=="GET":
        happened=False
        all_past=[]
        username=db.execute("SELECT username FROM users WHERE id=?",session["user_id"])[0]['username']
        #our_roll_no=db.execute("SELECT roll_no FROM users WHERE id=?",session["user_id"])[0]['roll_no']
        all_trips=db.execute("SELECT id,days,start_date,est_cost,location,min_people,description,leader_roll_no FROM trips")
        for i in all_trips:
            if str_to_date(i['start_date'])<datetime.datetime.today():
                joined=0
                for j in db.execute("SELECT member_roll_no FROM entries WHERE id IS ?",i['id']):
                    if j['member_roll_no']!=i['leader_roll_no']:
                        joined+=1
                i['joined']=joined
                all_past.append(i)
        if len(all_past)>0:
            happened=True
        last=None
        if len(all_past)%2==1:
            last=all_past.pop()
        dummy=[]
        switch=False
        twice=[]
        for i in all_past:
            twice.append(i)
            if switch:
                dummy.append(twice)
                twice=[]
            switch=~switch
        all_past=dummy
        return render_template("past.html",happened=happened,all_past=all_past,last=last,username=username)