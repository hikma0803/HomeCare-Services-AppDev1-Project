from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db=SQLAlchemy()

class User_Details(db.Model):
    __tablename__="user_details"                
    id=db.Column(db.String,primary_key=True)           #unique for everybody
    user_type=db.Column(db.String(20), nullable=False)  #admin,professional,customer
    password=db.Column(db.String(100), nullable=False)  #for everyone
    fullname=db.Column(db.String(50),nullable=True)    #name for pro,cus
    address = db.Column(db.String(255),nullable=True)                 #for professional
    phone_num = db.Column(db.String(100),unique=True,nullable=True)   #for professional
    approved_status = db.Column(db.Boolean, nullable=True)#for professional
    service_type = db.Column(db.String(100), nullable=True)#for professional
    experience = db.Column(db.Integer, nullable=True)        #for professional
    document_path = db.Column(db.String(255), nullable=True) 
    pincode=db.Column(db.String(50),nullable=True)                       #for professional,customer
    profile_verified = db.Column(db.Boolean, default=False)  # Admin approval
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy=True, foreign_keys='ServiceRequest.customer_id')
    accepted_requests = db.relationship('ServiceRequest', backref='professional', lazy=True, foreign_keys='ServiceRequest.professional_id')



class Service(db.Model):
    __tablename__ = 'service'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255)) # Internal column for name
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer)  # in minutes
    description = db.Column(db.String(255))

    # Relationship
    requests = db.relationship('ServiceRequest', backref='service')
class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user_details.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user_details.id'))
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(20), default='requested')  # e.g., 'requested', 'assigned', 'closed'
    remarks = db.Column(db.String(255))

    # Relationship
    review = db.relationship('Review', backref='service_request')

class Review(db.Model):
    __tablename__ = 'review'
    
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    review_content = db.Column(db.Text)
    rating = db.Column(db.Integer)  # e.g., 1-5 scale1`   `