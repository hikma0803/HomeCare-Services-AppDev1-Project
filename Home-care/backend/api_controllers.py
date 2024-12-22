from flask_restful import Resource, Api
from flask import request
from .models import *
from datetime import datetime


api=Api()

class UserCustomer(Resource):

    #Reading of data
    def get(self):
        users=User_Details.query.all()
        us=[]
        for user in users:
            if user.user_type=='customer':
                us.append({'id':user.id,'name':user.fullname,'password':user.password,
                       'address':user.address, 'phone_num':user.phone_num,'pincode':user.pincode})
        
        return us
    
    #Creating data
    def post(self):
        user_type='customer'
        id=request.json.get("id")
        fullname=request.json.get("fullname")
        password=request.json.get("password")
        address=request.json.get("address")
        phone_num=request.json.get("phone_num")
        pincode=request.json.get("pincode")
        new_show=User_Details(fullname=fullname,id=id,password=password,address=address,
                              phone_num=phone_num,pincode=pincode,user_type=user_type)
        db.session.add(new_show)
        db.session.commit()
        
        return {"message":"New customer added!"},201
    

    #Updating
    def put(self,id):
        show=User_Details.query.filter_by(id=id).first()
        if show:
            show.id=request.json.get("id")
            show.name=request.json.get("name")
            show.password=request.json.get("password")
            show.phone_num=request.json.get("phone_num")
            show.address=request.json.get("address")
            show.pincode=request.json.get("pincode")
            db.session.commit()
            return {"message":"customer updated!"},200
        
        return {"message":"customer id not found!"},404

    #Delete data
    def delete(self,id):
        show=User_Details.query.filter_by(id=id).first()
        if show:
            db.session.delete(show)
            db.session.commit()
            return {"message":"customer deleted!"},200
        
        return {"message":"customer id not found!"},404

class CustomerSearchApi(Resource):
    def get(self,id):
        show=User_Details.query.filter_by(id=id).first()
        if show:
            shows_json=[]
            shows_json.append({'id':show.id,'name':show.name,'tags':show.tags,'overall_rating':show.rating, 'tkt_price':show.tkt_price,'date_time':str(show.date_time),'theatre_id':show.theatre_id})
            return shows_json
        return {"message":"User id not found!"},404


class ServiceResource(Resource):

    #Reading of data
    def get(self):
        users=Service.query.all()
        us=[]
        for user in users:
            us.append({'id':user.id,'name':user.name,'time_required':user.time_required,
                           'base_price':user.base_price, 'description':user.description})
        
        return us
    
    #Creating data
    def post(self):
        id=request.json.get("id")
        name=request.json.get("name")
        time_required=request.json.get("time_required")
        base_price=request.json.get("base_price")
        description=request.json.get("description")
        new_show=Service(name=name,id=id,time_required=time_required,base_price=base_price,description=description
                         )
        db.session.add(new_show)
        db.session.commit()
        
        return {"message":"New Service added!"},201
    

    #Updating
    def put(self,id):
        show=Service.query.filter_by(id=id).first()
        if show:
            show.id=request.json.get("id")
            show.name=request.json.get("name")
            show.time_required=request.json.get("time_required")
            show.base_price=request.json.get("base_price")
            show.description=request.json.get("description")
            db.session.commit()
            return {"message":"Srvice updated!"},200
        
        return {"message":"service id not found!"},404

    #Delete data
    def delete(self,id):
        show=Service.query.filter_by(id=id).first()
        if show:
            db.session.delete(show)
            db.session.commit()
            return {"message":"Service deleted!"},200
        
        return {"message":"Service id not found!"},404

class ServiceSearchApi(Resource):
    def get(self,id):
        show=Service.query.filter_by(id=id).first()
        if show:
            shows_json=[]
            shows_json.append({'id':show.id,'name':show.name,'time_required':show.time_required,'base_price':show.base_price, 'description':show.description
                            })
            return shows_json
        return {"message":"User id not found!"},404


api.add_resource(UserCustomer,"/api/get_customer","/api/add_customer","/api/edit_customer/<id>","/api/delete_customer/<id>")
api.add_resource(CustomerSearchApi,"/api/search_customer/<id>")
api.add_resource(ServiceResource,"/api/get_service","/api/add_service","/api/edit_service/<id>","/api/delete_service/<id>")
api.add_resource(ServiceSearchApi,"/api/search_service/<id>")