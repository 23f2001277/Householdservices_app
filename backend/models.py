from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()
class User_Info(db.Model):
    __tablename__="user_info"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=1)
    full_name=db.Column(db.String,nullable=False)
    location=db.Column(db.String,nullable=False)
    pin_code=db.column(db.Integer,nullable=False)