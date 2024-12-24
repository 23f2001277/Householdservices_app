from flask import Flask, render_template, request, url_for, redirect, session, flash
from datetime import datetime
from .models import *
from flask import current_app as app
from sqlalchemy import cast, String, func, or_
import matplotlib.pyplot as plt
import os
import io
import base64

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
        
        # Query for user, admin, and professional
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
                # Handle blocked accounts
                if isinstance(user, User_Info) and user.user_status == 'blocked':
                    return render_template(
                        "blocked_message.html",
                        message="Your account has been restricted. Please contact support."
                    )
                if isinstance(user, Prof_Info) and user.prof_status == 'blocked':
                    return render_template(
                        "blocked_message.html",
                        message="Your account has been restricted. Please contact support."
                    )
                
                # Valid user, set session details
                session['user_id'] = user.id
                session['role'] = user.role
                
                # Redirect based on role
                if user.role == 0:  # Admin
                    return redirect(url_for("admin_dashboard"))
                elif user.role == 1:  # User
                    return redirect(url_for("user_dashboard", name=uname))
                elif user.role == 2:  # Professional
                    return redirect(url_for("prof_dashboard", name=uname))
            else:
                return render_template("login.html", msg="Invalid credentials")  # Password mismatch
        
        return render_template("login.html", msg="User not found, please register")  # User not found



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
    services = Service.query.all()
    professionals = Prof_Info.query.all()
    users = User_Info.query.all()
    service_requests = Service_req.query.all()
    return render_template("admin_dash.html", services=services, professionals=professionals, users=users, service_requests=service_requests)

@app.route("/user")
def user_dashboard():
    user_id = session["user_id"]
    user_info = User_Info.query.get(user_id)
    
    # Fetch the user service history
    user_service_history = db.session.query(User_Service_History, Service_req, Service).outerjoin(
        Service_req, User_Service_History.service_req_id == Service_req.id
    ).outerjoin(
        Service, Service_req.service_id == Service.id
    ).filter(
        User_Service_History.user_id == user_id
    ).all()
    
    upcoming_services = Service_req.query.filter_by(cust_id=user_id, status='pending').all()
    service_requests = Service_req.query.filter_by(cust_id=user_id).all()
    services = Service.query.all()  # Get all services
    
    # Get the top-rated professionals
    top_rated_professionals = db.session.query(
        Prof_Info,
        func.avg(Service_req.rating).label("avg_rating")
    ).join(Service_req, Prof_Info.id == Service_req.prof_id).\
        group_by(Prof_Info.id).\
        order_by(func.avg(Service_req.rating).desc()).\
        limit(5).all()
    
    return render_template(
        "user_dash.html",
        user_service_history=user_service_history,
        upcoming_services=upcoming_services,
        service_requests=service_requests,
        services=services,
        top_rated_professionals=top_rated_professionals,
        user_info=user_info,
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
        # Calculate the average rating
        ratings = Service_req.query.filter_by(prof_id=id).all()
        ratings = [rating.rating for rating in ratings if rating.rating is not None]
        if ratings:
            average_rating = sum(ratings) / len(ratings)
        else:
            average_rating = 0
        return render_template("professional_profile.html", professional=professional, average_rating=average_rating)
    else:
        return "Professional not found", 404
    
@app.route("/user_profile/<int:id>")
def view_user_profile(id):
    user = User_Info.query.get(id)
    if user:
        return render_template("user_profile.html", user=user)
    else:
        return "User not found", 404
    
@app.route('/service_request_details/<int:id>')
def service_request_details(id):
    service_req = Service_req.query.get(id)
    if service_req:
        customer = service_req.customer
        professional = service_req.professional
        # service_name = service_req.service.name
        return render_template('service_req_details.html', service_req=service_req, customer=customer, professional=professional)
    else:
        return 'Service request not found', 404
    
@app.route("/user_remark")
def user_remark():
    return render_template("user_remark.html")
@app.route("/user_profile/<int:id>")
def edit_user_profile(id):
    user = User_Info.query.get(id)
    if user:
        return render_template("user_profile.html", user=user)
    else:
        return "User not found", 404


@app.route("/logout")
def logout():
    return redirect(url_for("signin"))

@app.route("/close")
def close():
    return redirect(url_for("user_remark"))

@app.route("/prof_dashboard")
def prof_dashboard():
    # Check if the user is logged in and is a professional (role = 2)
    if "user_id" in session and session.get('role') == 2:
        professional_id = session["user_id"]
        professional = Prof_Info.query.get(professional_id)
        
        if not professional:
            flash("Professional not found.", "error")
            return redirect(url_for("signin"))

        # Check if the professional is blocked
        if professional.prof_status == 'blocked':
            # Render a message page instead of the dashboard
            return render_template(
                "blocked_message.html",
                message="Your account has been blocked. Please contact support for further assistance."
            )
        # Fetch services assigned to the logged-in professional with status 'Pending'
        today_services = Service_req.query.filter(
            Service_req.prof_id == professional_id,
            Service_req.status == STATUS_PENDING
        ).all()

        # Fetch closed services and include customer details
        closed_services = db.session.query(
            Service_req.id.label("service_id"),
            User_Info.full_name.label("customer_name"),
            User_Info.phone.label("customer_phone"),
            User_Info.location.label("customer_location"),
            User_Info.pin_code.label("customer_pin_code"),
            Service_req.date_of_comp.label("date_of_completion"),
            Service_req.rating.label("rating"),
            Service_req.remarks.label("remarks")
        ).join(User_Info, User_Info.id == Service_req.cust_id).filter(
            Service_req.prof_id == professional_id,
            Service_req.status == STATUS_CLOSED
        ).all()

        print(professional)  # Add a print statement to print the professional object

        # Render the dashboard template with fetched data
        return render_template(
            "prof_dash.html",
            today_services=today_services,
            closed_services=closed_services,
            professional=professional
        )
    else:
        # Redirect to the login page if not logged in or unauthorized
        return redirect(url_for("signin"))



@app.route('/accept_service/<int:service_id>', methods=['POST'])
def accept_service(service_id):
    service_req = Service_req.query.get(service_id)
    if service_req:
        service_req.status = STATUS_ACCEPTED  # Update status
        db.session.commit()
        return redirect(url_for('prof_dashboard'))
    else:
        return "Service Request not found", 404


@app.route("/reject_service/<int:service_id>", methods=["POST"])
def reject_service(service_id):
    service_request = Service_req.query.get(service_id)
    service_request.status = STATUS_REJECTED
    db.session.commit()
    flash("Service rejected successfully!")
    return redirect(url_for("prof_dashboard"))

@app.route('/close_service/<int:service_req_id>', methods=['GET', 'POST'])
def close_service(service_req_id):
    # Fetch the service request
    service_req = Service_req.query.get(service_req_id)
    
    # Check if the service request exists and has been accepted
    if not service_req or service_req.status.lower() != 'accepted':
        flash("Invalid request or service not accepted.", "danger")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        # Handle form submission
        rating = request.form['rating']
        feedback = request.form['feedback_user']
        
        # Validate rating value
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                flash("Please provide a rating between 1 and 5.", "warning")
                return redirect(url_for('close_service', service_req_id=service_req_id))
        except ValueError:
            flash("Invalid rating value.", "warning")
            return redirect(url_for('close_service', service_req_id=service_req_id))
        
        # Update the service request status, rating, and feedback
        service_req.status = 'closed'
        service_req.remarks = feedback
        service_req.rating = rating
        service_req.date_of_comp = datetime.utcnow()
        
        db.session.commit()
        flash("Service request successfully closed with your feedback.", "success")
        return redirect(url_for('user_dashboard'))
    
    # Handle GET request (render the remarks page)
    service = Service.query.get(service_req.service_id)
    return render_template('user_remarks.html', service_req=service_req, service=service)


@app.route("/cancel_service/<int:service_id>", methods=["POST"])
def cancel_service(service_id):
    service_request = Service_req.query.get(service_id)
    service_request.status = STATUS_CLOSED
    db.session.commit()
    flash("Service cancelled successfully!")
    return redirect(url_for("user_dashboard"))

@app.route('/service/<name>')
def list_professionals(name):
    user_id = session["user_id"]
    user_info = User_Info.query.get(user_id)

    # Get the service by name
    service = Service.query.filter_by(name=name).first()

    # Check if the service exists
    if not service:
        # flash("Service not found.", "error")
        return redirect(url_for('user_dashboard'))

    # Filter professionals based on the service_id
    filtered_professionals = Prof_Info.query.filter_by(service_name=service.id).filter(Prof_Info.prof_status != 'blocked').all()
    user_service_history = User_Service_History.query.filter_by(service_req_id=service.id).all()
    return render_template('professional_list.html', name=name, professionals=filtered_professionals, user_service_history=user_service_history, service=service, user_info=user_info)

@app.route("/book/<int:professional_id>", methods=["POST"])
def book_professional(professional_id):
    service_id = request.form["service_id"]
    customer_id = session["user_id"]
    professional = Prof_Info.query.get(professional_id)
    if professional.prof_status == 'blocked':
        flash("This professional is not available for booking.", "error")
        return redirect(url_for("user_dashboard"))
    service = Service.query.get(service_id)
    service_request = Service_req( service_id=service_id, cust_id=customer_id, prof_id=professional.id, date_of_req=datetime.now(), status=STATUS_PENDING )
    db.session.add(service_request) 
    db.session.commit()
    user_service_history = User_Service_History( user_id=customer_id, service_req_id=service_request.id ) 
    db.session.add(user_service_history) 
    db.session.commit() 
    flash("Service booked successfully!") 
    return redirect(url_for("user_dashboard"))
       
@app.route("/professional_profile", methods=["GET", "POST"])
def professional_profile():
    # Check if the user is logged in by checking the session for the user_id
    professional_id = session.get('user_id')
    
    if not professional_id:
        flash("You must be logged in to view your profile.", "danger")
        return redirect(url_for('signin'))  # Redirect to the login page if not logged in
    
    # Fetch the professional from the database
    professional = Prof_Info.query.get(professional_id)
    
    if not professional:
        flash("Profile not found.", "danger")
        return redirect(url_for('prof_dashboard'))  # Redirect to dashboard if professional not found

    if request.method == "POST":
        # Handle profile update form submission
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        location = request.form.get("location")
        pin_code = request.form.get("pin_code")
        

        # Update the professional's information
        professional.full_name = full_name
        professional.phone = phone
        professional.email = email
        professional.location = location
        professional.pin_code = pin_code

        # Save changes to the database
        db.session.commit()
        flash("Your profile has been updated successfully!", "success")

        return redirect(url_for('prof_dashboard'))  # Redirect to the profile page to show updated info

    return render_template("professional_edit.html", professional=professional)

@app.route("/user_profile", methods=["GET", "POST"])
def user_profile():
    user_id = session.get('user_id')

    if not user_id:
        flash("You must be logged in to view your profile.", "danger")
        return redirect(url_for('signin'))

    user = User_Info.query.get(user_id)
    user_info = User_Info.query.get(user_id)  # Fetch user_info to pass to the template

    if not user:
        flash("Profile not found.", "danger")
        return redirect(url_for('user_dashboard'))

    if request.method == "POST":
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        location = request.form.get("location")
        pin_code = request.form.get("pin_code")

        user.full_name = full_name
        user.phone = phone
        user.email = email
        user.location = location
        user.pin_code = pin_code

        db.session.commit()
        flash("Your profile has been updated successfully!", "success")

        return redirect(url_for('user_dashboard'))

    return render_template("user_edit.html", user=user, user_info=user_info)


@app.route("/user/search/<int:professional_id>", methods=["GET", "POST"])  # for professional search
def search_professionals(professional_id):
    search_history = []
    professional = None
    user_id = session.get("user_id") 
    user_info = User_Info.query.get(user_id)
    if "user_id" in session and session.get('role') == 2:
        professional_id = session["user_id"]
        professional = Prof_Info.query.get(professional_id)

    if request.method == "POST":
        search_by = request.form.get("search_by")
        search_value = request.form.get("search_value")

        # Ensure the results are scoped to the professional's services
        base_query = Service_req.query.join(User_Info, Service_req.cust_id == User_Info.id).filter(
            Service_req.prof_id == professional_id
        )

        # Search by location or pin code
        if search_by == 'location':
            search_history = base_query.filter(
                (User_Info.location.ilike(f'%{search_value}%')) |
                (User_Info.pin_code.cast(String).ilike(f'%{search_value}%'))
            ).all()

        # Search by date (flexible search)
        elif search_by == 'date':
            search_history = base_query.filter(
                Service_req.date_of_req.cast(String).ilike(f'%{search_value}%') |
                Service_req.date_of_comp.cast(String).ilike(f'%{search_value}%')
            ).all()

        # Search by customer name
        elif search_by == 'name':
            search_history = base_query.filter(
                User_Info.full_name.ilike(f'%{search_value}%')
            ).all()

        # Search by pin code
        elif search_by == 'pin':
            search_history = base_query.filter(
                User_Info.pin_code.cast(String).ilike(f'%{search_value}%')
            ).all()

    return render_template("prof_search.html", search_history=search_history, professional=professional, user_info=user_info)

@app.route("/professional/search", methods=["GET", "POST"])
def search_users():
    search_history = []
    message = None

    user_id = session.get("user_id")
    user_info = User_Info.query.get(user_id)

    if request.method == "POST":
        search_by = request.form.get("search_by")
        search_value = request.form.get("search_value")

        query = db.session.query(
            Prof_Info,
            Service.name.label("service_name"),
            func.avg(Service_req.rating).label("avg_rating")
        ).join(Service, Prof_Info.service_name == Service.id)\
         .outerjoin(Service_req, Service_req.prof_id == Prof_Info.id)\
         .filter(Prof_Info.prof_status == 'approved')

        if search_by == "location":
            query = query.filter(
                or_(
                    Prof_Info.location.ilike(f"%{search_value}%"),
                    Prof_Info.pin_code.cast(String).ilike(f"%{search_value}%")
                )
            )
        elif search_by == "name":
            query = query.filter(Prof_Info.full_name.ilike(f"%{search_value}%"))
        elif search_by == "service":
            query = query.filter(Service.name.ilike(f"%{search_value}%"))
        elif search_by == "pin":
            query = query.filter(Prof_Info.pin_code.cast(String).ilike(f"%{search_value}%"))
        elif search_by == "phone":
            query = query.filter(Prof_Info.phone.ilike(f"%{search_value}%"))

        search_history = query.group_by(Prof_Info.id).all()

        if not search_history:
            message = "No matching results found."

    return render_template(
        "user_search.html",
        search_history=search_history,
        message=message,
        user_info=user_info  # Ensure user_info is passed
    )



@app.route("/professional_summary/<int:professional_id>")
def professional_summary(professional_id):
    professional = Prof_Info.query.get(professional_id)

    if not professional:
        flash("Professional not found.", "error")
        return redirect(url_for("signin"))

    # Fetch all service requests for the professional
    service_reqs = Service_req.query.filter_by(prof_id=professional_id).all()

    # Calculate the average rating (handle no ratings gracefully)
    ratings = [sr.rating for sr in service_reqs if sr.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    # Save the chart to a file
    plt.figure(figsize=(6, 4))
    plt.bar(["Rating"], [avg_rating], color='#4CAF50')
    plt.xlabel("Category")
    plt.ylabel("Average Rating")
    plt.title("Average Rating Chart")
    chart_path = os.path.join('static', f'avg_rating_{professional_id}.png')
    plt.savefig(chart_path)
    plt.close()

    # Render the template
    return render_template(
        "prof_summary.html",
        professional=professional,
        avg_rating=avg_rating,
        chart_url=url_for('static', filename=f'avg_rating_{professional_id}.png')
    )



@app.route("/user_summary/<int:user_id>")
def user_summary(user_id):
    user = User_Info.query.get(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("signin"))

    # Fetch all service requests for the user
    service_reqs = Service_req.query.filter_by(cust_id=user_id).all()

    # Calculate the number of requests by status
    status_counts = {
        'pending': 0,
        'closed': 0,
        'accepted': 0
    }

    for req in service_reqs:
        if req.status == 'pending':
            status_counts['pending'] += 1
        elif req.status == 'closed':
            status_counts['closed'] += 1
        elif req.status == 'accepted':
            status_counts['accepted'] += 1

    # Data for the bar chart
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors = ['blue', 'green', 'pink']

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=colors)

    # Add labels and title
    plt.ylabel('Number of Requests')
    plt.title('Service Requests')

    # Save the plot to a file
    chart_path = os.path.join('static', f'service_summary_{user_id}.png')
    plt.savefig(chart_path)
    plt.close()

    # Render the template
    return render_template(
        "user_summary.html",
        user=user,
        chart_url=url_for('static', filename=f'service_summary_{user_id}.png')
    )


@app.route('/admin_summary')
def admin_summary():
    # Fetch data from the database
    service_reqs = Service_req.query.all()

    # Calculate the number of requests by status
    status_counts = {
        'Requested': 0,
        'Accepted': 0,
        'Closed': 0
    }

    for req in service_reqs:
        if req.status == 'pending':
            status_counts['Requested'] += 1
        elif req.status == 'accepted':
            status_counts['Accepted'] += 1
        elif req.status == 'closed':
            status_counts['Closed'] += 1

    # Calculate the ratings distribution
    customer_ratings = [req.rating for req in service_reqs if req.rating is not None]
    rating_counts = [customer_ratings.count(i) for i in range(1, 6)]

    # Create the customer ratings donut chart
    plt.figure(figsize=(6, 6))
    plt.pie(rating_counts, labels=range(1, 6), autopct='%1.1f%%', startangle=140, 
            colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#ff6666'])
    plt.title('Overall Customer Ratings')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save the plot to a BytesIO object
    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    plot_url1 = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    # Create the service requests summary bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(status_counts.keys(), status_counts.values(), color=['blue', 'green', 'pink'])
    plt.title('Service Requests Summary')
    plt.xlabel('Status')
    plt.ylabel('Number of Requests')

    # Save the plot to a BytesIO object
    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    plot_url2 = base64.b64encode(img2.getvalue()).decode()
    plt.close()

    return render_template(
        "admin_summary.html",
        plot_url1=plot_url1,
        plot_url2=plot_url2
    )