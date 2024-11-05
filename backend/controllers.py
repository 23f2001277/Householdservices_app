from flask import Flask, render_template, request, url_for, redirect
from .models import *
from flask import current_app as app


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        uname = request.form.get("user_name")
        pwd = request.form.get("password")
        usr = User_Info.query.filter_by(email=uname).first()
        adm = Admin_Info.query.filter_by(email=uname).first()
        prof = Prof_Info.query.filter_by(email=uname).first()
        
        user = None
        if usr:
            user = usr
        elif adm:
            user = adm
        elif prof:
            user = prof
        
        if user: 
            if user.password == pwd:  # Check if the password matches
                if user.role == 0:  # Admin
                    return render_template("admin_dash.html", name=uname)
                elif user.role == 1:  # User
                    return render_template("user_dash.html", name=uname)
                elif user.role == 2:  # Professional
                    return render_template("prof_dash.html", name=uname)
            else:
                return render_template("login.html", msg="Invalid credentials")  # Password does not match
        
        return render_template("login.html", msg="User not found, please register")  # User not found
    
    return render_template("login.html", msg="")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        uname = request.form.get("user_name")
        pwd = request.form.get("password")
        full_name = request.form.get("full_name")
        location = request.form.get("location")
        pin_code = request.form.get("pin_code")
        usr = User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html", msg="Sorry, this email is already registered!!!")
        new_usr = User_Info(email=uname, password=pwd, full_name=full_name,
                            location=location, pin_code=pin_code, role=1)  # Assign role
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html", msg="Registration successful!!!")
    return render_template("signup.html", msg="")


@app.route("/signup2", methods=["GET", "POST"])
def signup2():
    if request.method == "POST":
        uname = request.form.get("user_name")
        pwd = request.form.get("password")
        full_name = request.form.get("full_name")
        service_name = request.form.get("service_name")
        experience = request.form.get("experience")
        location = request.form.get("location")
        pin_code = request.form.get("pin_code")
        prof = Prof_Info.query.filter_by(email=uname).first()
        if prof:
            return render_template("signup2.html", msg="Sorry, this email is already registered!!!")
        new_prof = Prof_Info(email=uname, password=pwd, full_name=full_name,
                             service_name=service_name, experience=experience, location=location, pin_code=pin_code)
        db.session.add(new_prof)
        db.session.commit()
        return render_template("login.html", msg="Registration successful!!!")
    return render_template("signup2.html", msg="")

@app.route("/admin/<name>")
def admin_dashboard(name):
    return render_template("admin_dash.html", name=name)

@app.route("/user/<name>")
def user_dashboard(name):
    return render_template("user_dash.html", name=name)

@app.route("/prof/<name>")
def prof_dashboard(name):
    return render_template("prof_dash.html", name=name)


@app.route("/service/<service_name>", methods=["GET","POST"])
def new_service(service_name):
    if request.method == "POST":
        service_name=request.form.get("service_name")
        baseprice=request.form.get("baseprice")
        desc=request.form.get("desc")
        serv=Service.query.filter_by(service_name=service_name).first()
        if serv:
            return render_template("admin_serv.html", msg="Sorry, this service has already been registered")
        new_serv=Service(service_name=service_name, baseprice=baseprice, desc=desc)
        db.session.add(new_serv)
        db.session.commit()
        return render_template("admin_dash.html", msg="Registration successfull!!!")
    return render_template("admin_serv.html")