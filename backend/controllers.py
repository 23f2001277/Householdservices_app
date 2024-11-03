from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User_Info.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: #Existed and admin
            return render_template("admin_dash.html")
        elif usr and usr.role==1: #Existed and admin
            return render_template("user_dash.html")
        elif usr and usr.role==2: #Existed and admin
            return render_template("prof_dash.html")
        else:
            return render_template("login.html",msg="Invalid user credentials")
    return render_template("login.html",msg="")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") 
        full_name=request.form.get("full_name")
        address=request.form.get("location")
        pin_code=request.form.get("pin_code")
        usr=User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry, this mail already registered!!!")
        new_usr=User_Info(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now") 
    return render_template("signup.html",msg="")

@app.route("/signup2", methods=["GET","POST"])
def signup2():
     if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") 
        full_name=request.form.get("full_name")
        service_name=request.form.get("service_name")
        experience=request.form.get("experience")
        address=request.form.get("location")
        pin_code=request.form.get("pin_code")
        usr=User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry, this mail already registered!!!")
        new_usr=User_Info(email=uname,password=pwd,full_name=full_name,service_name=service_name,experience=experience,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now") 
     return render_template("signup2.html",msg="")
