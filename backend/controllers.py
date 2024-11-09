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
    services=Service.query.all()
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
    return render_template("signup2.html", msg="", services=services)

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
        existing_service = Service.query.filter_by(name=name).first()
        if existing_service:
            return render_template("admin_serv.html", msg="Service name already exists. Please edit the existing service instead.")
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

@app.route('/edit_service/<int:id>', methods=['GET', 'POST'])
def edit_service(id):
    service = Service.query.get(id)  # Fetch the service from the database
    if request.method == 'POST':
        if service:
            service.name = request.form['service_name']
            service.desc = request.form['desc']
            service.baseprice = request.form['baseprice']
            db.session.commit()  # Save the updated service back to the database
            return redirect(url_for("admin_dashboard"))  # Redirect to the admin page or another page
        else:
            return "Service not found", 404
    else:  # Handle GET request
        if service:
            return render_template("edit_service.html", service=service)  # Render edit form with service details
        else:
            return "Service not found", 404

@app.route('/approve_professional/<int:id>', methods=["POST"])
def approve_professional(id):
    professionals=Prof_Info.query.get(id)
    if request.method == "POST":
        if professionals:
            professionals.prof_status='approved'
            db.session.commit()
        
    return redirect(url_for("admin_dashboard"))


@app.route('/delete_professional/<int:id>', methods=["POST"])
def delete_professional(id):
    professionals=Prof_Info.query.get(id)
    db.session.delete(professionals)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/block_professional/<int:id>", methods=["POST"])
def block_professional(id):
    professionals=Prof_Info.query.get(id)
    if request.method == "POST":
        if professionals:
            professionals.prof_status='blocked'
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
    else:
        return "Professionals not found", 404

@app.route("/unblock_professional/<int:id>", methods=["POST"])
def unblock_professional(id):
    professionals=Prof_Info.query.get(id)
    if request.method == "POST":
        if professionals:
            professionals.prof_status='approved'
            db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/block_user/<int:id>", methods=["POST"])
def block_user(id):
    users=User_Info.query.get(id)
    if request.method == "POST":
        if users:
            users.user_status=False
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
    else:
        return "User not found", 404

@app.route("/unblock_user/<int:id>", methods=["POST"])
def unblock_user(id):
    users=User_Info.query.get(id)
    if request.method == "POST":
        if users:
            users.user_status=False
            db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/search_professional", methods=["GET"])
def search_professional():
    query = request.args.get("query")
    professionals = Prof_Info.query.filter(
        (Prof_Info.full_name.ilike(f"%{query}%")) | 
        (Prof_Info.email.ilike(f"%{query}%"))
    ).all()
    
    return render_template("admin_search.html", professionals=professionals)

@app.route("/professional_profile/<int:id>")
def view_professional_profile(id):
    professional = Prof_Info.query.get(id)
    if professional:
        return render_template("professional_profile.html", professional=professional)
    else:
        return "Professional not found", 404