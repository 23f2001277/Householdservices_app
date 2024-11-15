from flask import Flask, render_template, request, url_for, redirect, session, flash
from datetime import datetime
from .models import *
from flask import current_app as app

ROLE_ADMIN = 0
ROLE_USER = 1
ROLE_PROFESSIONAL = 2

STATUS_PENDING = "pending"
STATUS_ACCEPTED = "accepted"
STATUS_REJECTED = "rejected"
STATUS_CLOSED = "closed"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template('login.html')
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
            session['user_id'] = user.id
            session['role'] = user.role
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
    
    # return render_template("login.html", msg="")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        uname = request.form.get("user_name")
        pwd = request.form.get("password")
        full_name = request.form.get("full_name")
        location = request.form.get("location")
        pin_code = request.form.get("pin_code")
        phone = request.form.get("phone")
        usr = User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html", msg="Sorry, this email is already registered!!!")
        new_usr = User_Info(email=uname, password=pwd, full_name=full_name,
                            location=location, pin_code=pin_code,phone=phone, role=1)  # Assign role
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
        phone = request.form.get("phone")
        experience = request.form.get("experience")
        location = request.form.get("location")
        pin_code = request.form.get("pin_code")
        prof = Prof_Info.query.filter_by(email=uname).first()
        if prof:
            return render_template("signup2.html", msg="Sorry, this email is already registered!!!")
        new_prof = Prof_Info(email=uname, password=pwd, full_name=full_name, phone=phone,
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
    service_requests = Service_req.query.all()
    return render_template("admin_dash.html", services=services, professionals=professionals, users=users, service_requests=service_requests)

@app.route("/user")
def user_dashboard():
    user_id = session["user_id"]
    
    # Fetch the user service history
    user_service_history = db.session.query(User_Service_History, Service_req, Service).join(
        Service_req, User_Service_History.service_req_id == Service_req.id
    ).join(
        Service, Service_req.service_id == Service.id
    ).filter(
        User_Service_History.user_id == user_id
    ).all()
    
    upcoming_services = Service_req.query.filter_by(cust_id=user_id, status=STATUS_PENDING).all()
    service_requests = Service_req.query.filter_by(cust_id=user_id).all()
    services = Service.query.all()  # Get all services
    
    return render_template(
        "user_dash.html",
        user_service_history=user_service_history,
        upcoming_services=upcoming_services,
        service_requests=service_requests,
        services=services
    )



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
            users.user_status='blocked'
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
    else:
        return "User not found", 404

@app.route("/unblock_user/<int:id>", methods=["POST"])
def unblock_user(id):
    users=User_Info.query.get(id)
    if request.method == "POST":
        if users:
            users.user_status='approved'
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

@app.route("/search_user", methods=["GET"])
def search_user():
    query = request.args.get("query")
    users = User_Info.query.filter(
        (User_Info.full_name.ilike(f"%{query}%")) | 
        (User_Info.email.ilike(f"%{query}%"))
    ).all()
    
    return render_template("admin_search.html", users=users)

@app.route("/professional_profile/<int:id>")
def view_professional_profile(id):
    professional = Prof_Info.query.get(id)
    if professional:
        return render_template("professional_profile.html", professional=professional)
    else:
        return "Professional not found", 404
    
@app.route("/user_profile", methods=["GET"])
def view_user_profile():
    user_id = session['user_id']
    user = User_Info.query.get(user_id)
    if user:
        return render_template("user_profile.html", user=user)
    else:
        return "User not found", 404
    
@app.route("/user_remark")
def user_remark():
    return render_template("user_remark.html")

@app.route("/logout")
def logout():
    return redirect(url_for("signin"))

@app.route("/close")
def close():
    return redirect(url_for("user_remark"))

@app.route("/prof_dashboard")
def prof_dashboard():
    if "user_id" in session and session['role'] == 2:
    

    # Fetch professional-specific service requests
        professional_id = session["user_id"]
        today_services = Service_req.query.filter_by(
            prof_id=professional_id, status=STATUS_PENDING
        ).all()

        closed_services = Service_req.query.filter_by(
            prof_id=professional_id, status=STATUS_CLOSED
        ).all()

        return render_template("prof_dash.html", today_services=today_services, closed_services=closed_services)
    else:
        return render_template('login.html')


@app.route("/accept_service/<int:service_id>", methods=["POST"])
def accept_service(service_id):
    service_request = Service_req.query.get(service_id)
    service_request.status = STATUS_ACCEPTED
    db.session.commit()
    flash("Service accepted successfully!")
    return redirect(url_for("prof_dashboard"))

@app.route("/reject_service/<int:service_id>", methods=["POST"])
def reject_service(service_id):
    service_request = Service_req.query.get(service_id)
    service_request.status = STATUS_REJECTED
    db.session.commit()
    flash("Service rejected successfully!")
    return redirect(url_for("prof_dashboard"))

@app.route("/cancel_service/<int:service_id>", methods=["POST"])
def cancel_service(service_id):
    service_request = Service_req.query.get(service_id)
    service_request.status = STATUS_CLOSED
    db.session.commit()
    flash("Service cancelled successfully!")
    return redirect(url_for("user_dashboard"))

@app.route('/service/<name>')
def list_professionals(name):
    # Get the service by name
    service = Service.query.filter_by(name=name).first()

    # Check if the service exists
    if not service:
        # flash("Service not found.", "error")
        return redirect(url_for('user_dashboard'))

    # Filter professionals based on the service_id
    filtered_professionals = Prof_Info.query.filter_by(service_name=service.id).all()
    user_service_history = User_Service_History.query.all()
    return render_template('professional_list.html', name=name, professionals=filtered_professionals, user_service_history=user_service_history, service=service)

@app.route("/book/<int:professional_id>", methods=["POST"])
def book_professional(professional_id):
    service_id = request.form["service_id"]
    customer_id = session["user_id"]
    professional = Prof_Info.query.get(professional_id)
    service = Service.query.get(service_id)
    
    # Create a new Service_req record
    service_request = Service_req(
        service_id=service_id,
        cust_id=customer_id,
        prof_id=professional.id,
        date_of_req=datetime.now(),
        status=STATUS_PENDING
    )
    
    # Add the service request to the database
    db.session.add(service_request)
    db.session.commit()
    
    # Now link the service request to the user's service history
    user_service_history = User_Service_History(
        user_id=customer_id,
        service_req_id=service_request.id
    )
    db.session.add(user_service_history)
    db.session.commit()
    
    flash("Service booked successfully!")
    return redirect(url_for("user_dashboard"))



@app.route('/close_service/<int:service_req_id>', methods=['POST'])
def close_service(service_req_id):
    # Find the service request by ID
    service_req = Service_req.query.get(service_req_id)
    if service_req and service_req.status == "Pending":
        # Update the status and date of completion
        service_req.status = "Completed"
        service_req.date_of_comp = datetime.now()
        db.session.commit()
    return redirect(url_for('user_dashboard'))
