from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()
class Admin_Info(db.Model):
    __tablename__="admin_info"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=0)
class User_Info(db.Model):
    __tablename__="user_info"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=1)
    full_name=db.Column(db.String,nullable=False)
    location=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
class Prof_Info(db.Model):
    __tablename__="prof_info"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=2)
    full_name=db.Column(db.String,nullable=False)
    service_name=db.Column(db.String,nullable=False)
    experience=db.Column(db.Integer,nullable=False)
    location=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
class Service(db.Model):
    __tablename__="service"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    baseprice=db.Column(db.Float, default=0.0)
    timereq=db.Column(db.Integer,nullable=False)
    desc=db.column(db.String)
class Service_req(db.Model):
    __tablename__="service_req"
    id=db.Column(db.Integer,primary_key=True)
    service_id=db.Column(db.Integer, db.ForeignKey("service.id"),nullable=False)
    cust_id=db.Column(db.Integer, db.ForeignKey("user_info.id"),nullable=False)
    prof_id=db.Column(db.Integer, db.ForeignKey("prof_info.id"),nullable=False)
    date_of_req=db.Column(db.DateTime,nullable=False)
    date_of_comp=db.Column(db.DateTime,nullable=False)
    remark=db.Column(db.String)