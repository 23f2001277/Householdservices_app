from flask import Flask, render_template, request, url_for, redirect, session, flash
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
                    return redirect(url_for("admin_dashboard"))
                elif user.role == 1:  # User
                    return redirect(url_for("user_dashboard", name=uname))
                elif user.role == 2:  # Professional
                    return redirect(url_for("prof_dashboard", name=uname))
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

@app.route("/admin")
def admin_dashboard():
    services=Service.query.all()
    professionals=Prof_Info.query.all()
    users=User_Info.query.all()
    return render_template("admin_dash.html", services=services, professionals=professionals, users=users)

@app.route("/user")
def user_dashboard():
    return render_template("user_dash.html")

@app.route("/prof")
def prof_dashboard():
    return render_template("prof_dash.html")


@app.route("/service", methods=["GET","POST"])
def new_service():
    if request.method == "POST":
        name=request.form.get("service_name")
        baseprice=request.form.get("baseprice")
        desc=request.form.get("desc")
        new_serv=Service(name=name, baseprice=baseprice, desc=desc)
        db.session.add(new_serv)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    else:
        return render_template("admin_serv.html")


@app.route("/logout")
def logout():
    return  redirect(url_for("signin"))

@app.route("/delete_service/<int:id>", methods=["POST"])
def delete_service(id):
    service = Service.query.get(id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin_dashboard')) 

@app.route("/edit_service/<int:id>", methods=["GET","POST"])
def edit_service(id):
    service = Service.query.get(id)
    if request.method == "POST":
        name = request.form.get("service_name")
        baseprice = request.form.get("baseprice")
        desc = request.form.get("desc")
        new_serv=Service(name=name, baseprice=baseprice, desc=desc)
        db.session.add(new_serv)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    if request.method  == "GET":
        return render_template("edit_service.html", service=service)

@app.route('/approve_professional/<int:id>', methods=["POST"])
def approve_professional(id):
    professionals=Prof_Info.query.get(id)
    if professionals:
        professionals.status=True
        db.session.commit()
        flash('{prof_info.full_name} has been approved!', 'success')
    return redirect(url_for("admin_dashboard"))

@app.route("/block_professional/<int:id>", methods=["POST"])
def block_professional(id):
    professionals=Prof_Info.query.get(id)
    if professionals:
        professionals.status=False
        db.session.commit()
        flash('{professionals.full_name} has been blocked!', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route("/block_user/<int:id>", methods=["POST"])
def block_user(id):
    users=Prof_Info.query.get(id)
    if users:
        users.status=False
        db.session.commit()
        flash('{users.full_name} has been blocked!', 'danger')
    return redirect(url_for('admin_dashboard'))