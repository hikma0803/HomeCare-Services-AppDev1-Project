from flask import Flask,render_template,request,send_from_directory,url_for,redirect
from flask import current_app as app
from backend.models import * 
from werkzeug.utils import secure_filename
from datetime import date
from sqlalchemy import and_,or_
from sqlalchemy.orm import aliased
from flask import jsonify
import os
from datetime import datetime
import matplotlib.pyplot as plt
from sqlalchemy import func
os.makedirs('uploads', exist_ok=True)
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
       return render_template("login.html")
    if request.method=='POST':
        id=request.form.get('id')
        password=request.form.get('password')

        usr=User_Details.query.filter_by(id=id,password=password).first()
        if usr and usr.user_type=='admin':
            service_summary=services()
            professional_summary=professionals()
            service_request_summary=service_request()
            return redirect(url_for("home1", name=usr.user_type,key=id))
        elif usr and usr.user_type=='professional':
            if usr.approved_status:
                return redirect(url_for("home2", name=usr.user_type,key=id))
        elif usr and usr.user_type=='customer':
            service_summary=services()
            u=usr.id
            service_req=service_request_customer(u)
            # print(service_req)
            history=row(u)
    #         for value in history:
    # # Access the dictionary values using the keys
    #             phone_num = value["phone_num"]
    #             service_id = value["service_id"]
    #             customer_id = value["customer_id"]
    #             professional_id = value["professional_id"]
    #             service_request_id = value["service_request_id"]
    #             service_status = value["service_status"]

    # # Print or process the values as needed
    #             print(f"Service Request ID: {service_request_id}")
    #             print(f"Customer ID: {customer_id}")
    #             print(f"Professional ID: {professional_id}")
    #             print(f"Phone Number: {phone_num}")
    #             print(f"Service Status: {service_status}")
            return redirect(url_for("home3", name=usr.user_type,key=id))
        else:
            return render_template("login.html",msg="Invalid Credentials!!!")
    
    return render_template("login.html",msg='')
@app.route('/logout',methods=['GET','POST'])
def logout():
    return redirect(url_for("login"))


@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        return render_template("login.html",msg="")
    return render_template("signup.html")

@app.route("/signup_customer",methods=["GET","POST"])
def signup_customer():
    if request.method=="POST":
        user_type="customer"
        id=request.form.get('id')
        fullname=request.form.get('fullname')
        password=request.form.get('password')
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        usr=User_Details.query.filter_by(id=id).first()
        if not usr:
            new_user=User_Details(id=id,fullname=fullname,password=password,user_type=user_type,address=address,pincode=pincode)
            
            db.session.add(new_user)
            db.session.commit()
            return render_template("login.html",msg='')
        else:
            return render_template("login.html",msg="Sorry,User Already Existed")
    return render_template("customer.html")

@app.route("/signup_service_professional",methods=["GET","POST"])
def signup_service_professional():
    if request.method=="POST":
        user_type="professional"
        id=request.form.get('id')
        fullname=request.form.get('fullname')
        password=request.form.get('password')
        service_type=request.form.get('service_type')
        experience=request.form.get('experience')
        documents = request.files.get('documents')# Handle file as upload

        # Save the file to a directory, like 'uploads/'
        filename = secure_filename(documents.filename)
        document_path = os.path.join('uploads', filename)
        documents.save(document_path)  # Save file to the path
        address=request.form.get('address')
        pincode=request.form.get('pincode')
        usr=User_Details.query.filter_by(id=id).first()
        if not usr:
            new_user=User_Details(id=id,fullname=fullname,password=password,user_type=user_type,
                                service_type=service_type,experience=experience,document_path=document_path,
                                address=address,pincode=pincode)
            
            db.session.add(new_user)
            db.session.commit()
            return render_template("login.html",msg='')
        else:
            return render_template("login.html",msg="Sorry,User Already Existed")
    return render_template("service_professional.html")

@app.route("/admin_search/<name>", methods=["GET", "POST"])
def search(name):
    msg = 'Enter something'  # Default message for GET requests
    if request.method == "POST":
        msg = 'OOps! nothing here'  # Fallback message for unsuccessful searches
        search_txt = request.form.get("search_txt")
        print(type(search_txt))
        selected_action = request.form.get("selected_action")
        print(selected_action)
        if search_txt and selected_action:
            if selected_action == 'service':
                service_name = service_search_by_name(search_txt)
                service_base_price = service_search_by_base_price(search_txt)
                service_description = service_search_by_description(search_txt)

                if service_name:
                    return render_template('admin_search.html', services=service_name, name=name, msg=msg)
                elif service_base_price:
                    return render_template('admin_search.html', base_price=service_base_price, name=name, msg=msg)
                elif service_description:
                    return render_template('admin_search.html', description=service_description, name=name, msg=msg)

            elif selected_action == 'service_request':
                service_date = service_request_search_by(search_txt)
                if service_date:
                    return render_template('admin_search.html', service_date=service_date, name=name, msg=msg)

            # elif selected_action == 'professional':
            #     profile_verified = professional_search_by_service_type(search_txt)
            #     if profile_verified:
            #         return render_template('admin_search.html', service_type=profile_verified, name=name, msg=msg)

        # If no results found:
        msg = 'No results found for your search.'

    # Render the page for GET requests or when no results are found:
    return render_template('admin_search.html', name=name, msg=msg)



@app.route("/home/<name>",methods=["GET","POST"])
def home1(name):
    service=services()
    pro=professionals()
    service_req=service_request()
    return render_template('admin_dashboard_home.html',name=name,service=service,professional=pro,service_request=service_req)



@app.route("/home_pro/<name>/<key>", methods=["GET", "POST"])
def home2(name, key):
    
    
    # Create alias for ServiceRequest to handle multiple queries
    service_request = aliased(ServiceRequest)

    # Query to fetch today's service requests (pending and available for professional) with status 'requested'
    todays_requests = db.session.query(
        User_Details.id,
        User_Details.fullname,
        User_Details.address,
        User_Details.pincode,
        service_request.id,
        service_request.service_id,
        service_request.service_status,
    ).join(service_request, service_request.customer_id == User_Details.id) \
    .filter(
        and_(
              # Filter by today's date
            service_request.service_status == 'requested',          # Only 'requested' status
            or_(
                service_request.professional_id.is_(None),          # Include unassigned requests
                service_request.professional_id == key              # Or requests assigned to this professional
            )
        )
    ).all()
    print(todays_requests)
    todays_requests_dict = [
    {
        'user_id': user_id,
        'fullname': fullname,
        'address': address,
        'pincode': pincode,
        'request_id': request_id,
        'service_id': service_id,
        'status': status,
        
    }
    for user_id, fullname, address, pincode, request_id, service_id, status in todays_requests
]

    # Query to fetch already accepted service requests for this professional
    accepted_requests = db.session.query(
        User_Details.id,
        User_Details.fullname,
        User_Details.address,
        User_Details.pincode,
        service_request.id,
        service_request.service_id,
        service_request.service_status
    ).join(service_request, service_request.customer_id == User_Details.id) \
    .filter(
        and_(
            service_request.service_status == 'accepted',           # Only accepted requests
            service_request.professional_id == key                  # Belongs to this professional
        )
    ).all()
    accepted_requests_dict = [
    {
        'user_id': user_id,
        'fullname': fullname,
        'address': address,
        'pincode': pincode,
        'request_id': request_id,
        'service_id': service_id,
        'status': status
    }
    for user_id, fullname, address, pincode, request_id, service_id, status in accepted_requests
]


    # Query to fetch closed service requests handled by the given professional
    closed_requests = db.session.query(
        User_Details.id,
        User_Details.fullname,
        User_Details.address,
        User_Details.pincode,
        service_request.id,
        service_request.service_id,
        service_request.service_status,
    ).join(service_request, service_request.customer_id == User_Details.id) \
    .filter(
        and_(
            service_request.professional_id == key,                 # Filter by professional ID
            service_request.service_status == 'closed',             # Only closed requests
        )
    ).all()

    # Combine the results of today's pending requests and already accepted requests
    # all_requests = list(set(todays_requests + accepted_requests))

    # Construct customer details with service_id for display
    # customer_details = [
    #     {
    #         'request_id': request_id,
    #         'user_id': user_id,
    #         'fullname': fullname,
    #         'address': address,
    #         'pincode': pincode,
    #         'status': status,
    #         'service_id': service_id
    #     }
    #     for user_id, fullname, address, pincode, request_id, service_id, status in all_requests
    # ]

    # Construct customer details for closed requests
    closed_customer_details = [
        {
            'request_id': service_id,
            'user_id': user_id,
            'fullname': fullname,
            'address': address,
            'pincode': pincode,
            'status': status,
            'service_id': service_id
        }
        for user_id, fullname, address, pincode, service_id, service_id, status in closed_requests
    ]

    # Render the template and pass the necessary variables
    return render_template(
        'professional_home.html',
        name=name,
        key=key,
        customer_details=todays_requests_dict,
        accept=accepted_requests_dict,
        closed_customer_details=closed_customer_details  # Pass closed requests to the template
    )

@app.route("/search_pro/<name>/<key>", methods=["GET", "POST"])
def search_pro(name, key):
    print(name)
    if request.method == "POST":
        print(request.form)
        search_txt = request.form.get("search_txt")
        selected_action = request.form.get("selected_action")
       
        
        if selected_action == 'date_of_request':
            try:
                search = get_accepted_requests_by_professional_and_date(key, search_txt)
                print(search)
                if search:
                    return render_template('search_pro.html', services=search, name=name, key=key)
            except Exception as e:
                print(f"Error: {e}")
        elif selected_action=='location':
            try:
                search = get_accepted_requests_by_professional_and_location(key, search_txt)
                print(search)
                if search:
                    return render_template('search_pro.html', services=search, name=name, key=key)
            except Exception as e:
                print(f"Error: {e}")

    return render_template('search_pro.html', name=name, key=key)

@app.route("/profile/<name>/<key>", methods=["GET", "POST"])
def profile(name,key):
    s=get_pro(key)
    ra=get_professional_rating(key)
    if request.method=='POST':
        user_type='professional'
        fullname=request.form.get('name')
        password=request.form.get('password')
        professional_id=request.form.get('professional_id')
        address=request.form.get('address')
        phone_num=request.form.get('phone_num')
        experience=request.form.get('experience')
        s.fullname=fullname
        s.professional_id=professional_id
        s.password=password
        s.address=address
        s.phone_num=phone_num
        s.experience=experience
        new=User_Details(fullname=fullname,id=professional_id,
                         address=address,phone_num=phone_num,experience=experience,user_type=user_type,password=password)
       
        db.session.commit()
        return render_template('professional_profile.html',service=s,ra=ra,name=name,key=key)


    return render_template('professional_profile.html',service=s,ra=ra,name=name,key=key)

@app.route("/profile_cus/<name>/<key>", methods=["GET", "POST"])
def profile1(name,key):
    s=get_cus(key)
    if request.method=='POST':
        user_type='customer'
        fullname=request.form.get('name')
        password=request.form.get('password')
        customer_id=request.form.get('customer_id')
        address=request.form.get('address')
        phone_num=request.form.get('phone_num')
        
        s.fullname=fullname
        s.customer_id=customer_id
        s.password=password
        s.address=address
        s.phone_num=phone_num
        
        new=User_Details(fullname=fullname,id=customer_id,
                         address=address,phone_num=phone_num,user_type=user_type,password=password)
       
        db.session.commit()
        return render_template('customer_profile.html',service=s,name=name,key=key)


    return render_template('customer_profile.html',service=s,name=name,key=key)


@app.route("/home_cu/<name>/<key>", methods=["GET", "POST"])
def home3(name,key):
    history=row(key)
    return render_template('customer_dashboard_home.html',name=name,key=key,history=history)


@app.route("/accept_request/<name>/<key>/<id>", methods=["GET", "POST"])
def accept(name, key, id):

    se = get_service_req(id)
    if not se:
        # Redirect to home with an error message
        
    
        return redirect(url_for("home2", name=name, key=key,id=id))
    
    se.professional_id = key
    se.service_status = 'accepted'
    db.session.commit()
    print(se.professional_id)
    return redirect(url_for("home2", name=name, key=key,id=id))


@app.route("/new_service/<name>", methods=["GET", "POST"])
def new_service(name):
    if request.method == "POST":
        # Retrieve form data
        service_name = request.form.get("service_name")
        service_nam=service_name.upper()
        description = request.form.get("description")
        time_required = request.form.get("time_required")
        base_price = request.form.get("base_price")

        # Validate form inputs
        if not service_name or not description or not time_required or not base_price:
            return render_template(
                "admin_dashboard_home.html",
                name=name,
                msg="All fields are required!",
            )

        # Save new service to the database
        try:
            new_service = Service(
                name=service_nam,
                description=description,
                time_required=int(time_required),
                base_price=float(base_price),
            )
            db.session.add(new_service)
            db.session.commit()
            return redirect(url_for("home1", name=name))  # Redirect to dashboard
        except Exception as e:
            db.session.rollback()
            return render_template(
                "admin_dashboard_home.html",
                name=name,
                msg="Error while adding the service: " + str(e),
            )

    # Render the form (GET request)
    return render_template("admin_dashboard_home.html", name=name)
 
@app.route('/')
def home():
    return "<h2>hello world<h3>"
@app.route("/more_service/<name>/<key>",methods=["GET","POST"])
def more(key,name):
    list=Service.query.filter_by(id=key).first()
    return render_template('more_service.html',list=list,name=name)
@app.route("/more_professional/<name>/<key>",methods=["GET","POST"])
def professional(key,name):
    professional=User_Details.query.filter_by(id=key).first()
    return render_template('more_professional.html',name=name,professional=professional)




@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    try:
        return send_from_directory('uploads', filename)
    except FileNotFoundError:
        return "File not found", 404

@app.route("/edit_service/<name>/<key>",methods=["GET","POST"])
def edit_service(name,key):
    s=get_service(key) 
    if request.method=="POST":
        iname=request.form.get("name")
        base_price=request.form.get("base_price")
        time_required=request.form.get("time_required")
        description=request.form.get("description") #data is string format
        s.name=iname
        s.base_price=base_price
        s.time_required=time_required
        s.description=description
        db.session.commit()
        service=services()
        professional=professionals()
        service_req=service_request()
        return render_template("admin_dashboard_home.html",name=name,service=service,professional=professional,service_request=service_req)
    return render_template("edit_service.html",service=s,name=name)

@app.route("/delete_service/<name>/<key>",methods=["GET","POST"])
def delete_venue(name,key):
    v=get_service(key)
    print(v)
    db.session.delete(v)
    db.session.commit()
    return redirect(url_for("home1",key=key,name=name))

@app.route("/login/clean/<name>/<key>",methods=["GET","POST"])
def one(name,key):
    two=cleaning()
    history=row(key)
    par='clean'
    return render_template("cleaning.html",clean=two,name=name,key=key,history=history,par=par)

@app.route("/login/repair/<name>/<key>",methods=["GET","POST"])
def three(name,key):
    two=repair()
    history=row(key)
    par='repair'
    return render_template("cleaning.html",repair=two,name=name,key=key,history=history,par=par)


@app.route("/login/electrical/<name>/<key>",methods=["GET","POST"])
def two(name,key):
    two=electrical()
    history=row(key)
    par='electric'
    return render_template("cleaning.html",electric=two,name=name,key=key,history=history,par=par)


@app.route("/login/others/<name>/<key>",methods=["GET","POST"])
def four(name,key):
    two=others()
    history=row(key)
    par='others'
    return render_template("cleaning.html",others=two,name=name,key=key,history=history,par=par)

@app.route("/book/<name>/<key>/<id>/<par>", methods=["GET", "POST"]) #serviceid=id
def book(name, key, id,par):
    try:
        if par=='clean':
            # two=cleaning()
            new_request = ServiceRequest(service_id=id, customer_id=key, date_of_request=date.today())
            db.session.add(new_request)
            # print(new_request)
            db.session.commit()
            return redirect(url_for("one", name=name,key=key))
        elif par=='repair':
            # two=cleaning()
            new_request = ServiceRequest(service_id=id, customer_id=key, date_of_request=date.today())
            db.session.add(new_request)
            # print(new_request)
            db.session.commit()
            return redirect(url_for("three", name=name,key=key))
        elif par=='electric':
            # two=cleaning()
            new_request = ServiceRequest(service_id=id, customer_id=key, date_of_request=date.today())
            db.session.add(new_request)
            # print(new_request)
            db.session.commit()
            return redirect(url_for("two", name=name,key=key))
        elif par=='others':
            # two=cleaning()
            new_request = ServiceRequest(service_id=id, customer_id=key, date_of_request=date.today())
            db.session.add(new_request)
            # print(new_request)
            db.session.commit()
            return redirect(url_for("four", name=name,key=key))
    except Exception as e:
        db.session.rollback()  # Roll back in case of errors
        return f"An error occurred: {e}", 500  # Or handle gracefully with an error


@app.route("/close/<name>/<key>/<id>", methods=["GET", "POST"])
def pop(name, key, id):
    print(name, key, id)
    if request.method == "POST":
        print(request.form)
        date_of_completion = request.form.get("date_of_completion")
        remarks = request.form.get("remarks")
        rating = request.form.get("rating")

        # Convert the string date to a datetime object
        try:
            date_of_completion = datetime.strptime(date_of_completion, "%Y-%m-%d")
        except ValueError as e:
            print(f"Error parsing date: {e}")
            return "Invalid date format. Please use YYYY-MM-DD.", 400

        new = Review(service_request_id=id, review_content=remarks, rating=rating)
        db.session.add(new)

        date = get_service_req(id)
        if date is not None:
            date.date_of_completion = date_of_completion
            date.service_status='closed'
            db.session.commit()
        else:
            print(f"No ServiceRequest found with id: {id}")
            return "Service request not found.", 404

        return redirect(url_for("home3", name=name, key=key))

    his = col(key, id)  # id=service_number aka serviceRequest.id
    return render_template('review.html', his=his, name=name, id=id, key=key)

    
  


@app.route("/cu_search/<name>/<key>", methods=["GET", "POST"])
def search_cu(name,key):
    print(name)
    if request.method=="POST":
        print(request.form)
        search_txt=request.form.get("search_txt")
        selected_action=request.form.get("selected_action")
        if selected_action=='service':
            service_name=service_search_by_name(search_txt)
            service_base_price=service_search_by_base_price(search_txt)
            service_description=service_search_by_description(search_txt)
            if service_name:
                return render_template('customer_search.html',services=service_name,name=name,key=key)
            elif service_base_price:
                return render_template('customer_search.html',base_price=service_base_price,name=name,key=key)
            elif service_description:
                 return render_template('customer_search.html',description=service_description,name=name,key=key)
        # elif selected_action=='service_request':
        #     service_date=service_request_search_by(search_txt)
        #     print(service_date)
        #     if service_date:
        #         return render_template('admin_search.html',service_date=service_date,name=name)
        
        # elif selected_action=='professional':
        #     profile_verified=professional_search_by(search_txt)
        #     if profile_verified:
        #         return render_template('admin_search.html',profile_verified=profile_verified,name=name)
    return render_template('customer_search.html',name=name,key=key)


@app.route("/book_se/<name>/<key>/<id>",methods=["GET","POST"])
def approve_se(name,key,id):
        new_request = ServiceRequest(service_id=id, customer_id=key, date_of_request=date.today())
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for("search_cu", name=name,key=key))



@app.route("/approve_pro/<name>/<key>",methods=["GET","POST"])
def approve(name,key):
    se=get_pro(key)
    se.approved_status=True
    db.session.commit()
    return redirect(url_for("home1", name=name,key=key))
@app.route("/reject_pro/<name>/<key>",methods=["GET","POST"])
def reject(name,key):
    se=get_pro(key)
    se.approved_status=False
    db.session.commit()
    return redirect(url_for("home1", name=name,key=key)) 
@app.route("/delete_pro/<name>/<key>",methods=["GET","POST"])
def delete(name,key):
    se=get_pro(key)
    db.session.delete(se)
    db.session.commit()
    return redirect(url_for("home1", name=name,key=key))

# @app.route("/reject_pro/<name>/<key>",methods=["GET","POST"])
# @app.route("/delete_pro/<name>/<key>",methods=["GET","POST"])
@app.route("/admin_summary/<name>",methods=["GET","POST"])
def admin_summary(name):
    plot = customer_summary()
    plot.savefig(f"./static/images/{name}_admin_summary.jpeg")  # Save with name
    plot.clf()
    return render_template("admin_summary.html", name=name) 

@app.route("/cu_summary/<name>/<key>",methods=["GET","POST"])
def cus_summary(name,key):
    plot = customer_summary()
    plot.savefig(f"./static/images/{key}_customer_summary.jpeg")  # Save with name
    plot.clf()
    return render_template("customer_summary.html", name=name,key=key) 

@app.route("/pro_summary/<name>/<key>",methods=["GET","POST"])
def pro_summary(name,key):
    plot = customer_summary()
    plot.savefig(f"./static/images/{key}_customer_summary.jpeg")  # Save with name
    plot.clf()
    return render_template("professional_summary.html", name=name,key=key) 



def services():
    services=Service.query.all()
    service_list={}
    for service in services:
        if service.id not in service_list.keys():
            service_list[service.id]=[service.name,service.base_price,service.time_required]
    return service_list
def today_services(key):
    # Fetch today's date
    today = date.today()
    today_services = ServiceRequest.query.filter_by(professional_id=key).filter(ServiceRequest.date_of_request == today, 
                            ServiceRequest.service_status == 'requested').all()
    
    return today_services
def closed_services(key):
    today = date.today()
    closed_services=ServiceRequest.query.filter_by(professional_id=key).filter(ServiceRequest.date_of_request ==date , ServiceRequest.service_status == 'closed').all()
    return closed_services
def professionals():
    professionals=User_Details.query.filter_by(user_type='professional').all()
    professional_list={}
    for professional in professionals:
        if professional.id not in professional_list.keys():
            professional_list[professional.id]=[professional.fullname,professional.experience,professional.service_type,professional.approved_status]
    return professional_list
def service_request():
    service_request=ServiceRequest.query.all()
    service_request_list={}
    for service in service_request:
        if service.id not in service_request_list.keys():
            service_request_list[service.id]=[service.service_id,service.professional_id,service.date_of_request,
                                              service.service_status]
    return service_request_list
    
def service_request_customer(id):
    service_request=ServiceRequest.query.filter_by(customer_id=id).all()
    service_request_list={}
    for service in service_request:
        if service.id not in service_request_list.keys():
            service_request_list[service.id]=[service.id,service.professional_id,service.date_of_request,
                                              service.service_status]
    return service_request_list

def service_search_by_name(search_txt):
    service_name=Service.query.filter(Service.name.ilike(f"%{search_txt}%")).all()
    return service_name
def service_search_by_base_price(search_txt):
    service_base_price=Service.query.filter(Service.base_price.ilike(f"%{search_txt}%")).all()
    return service_base_price
def service_search_by_description(search_txt):
    service_description=Service.query.filter(Service.description.ilike(f"%{search_txt}%")).all()
    return service_description
def service_request_search_by(search_txt):
    # Use ilike to perform a case-insensitive search for the text in the date_of_request field
    service_date = ServiceRequest.query.filter(ServiceRequest.date_of_request.ilike(f"%{search_txt}%")).all()
    return service_date 
def professional_search_by_service_type(search_txt):
    profile_verified=User_Details.query.filter(User_Details.service_type.ilike(f"%{search_txt}%")).all()
    return profile_verified
def get_service(id):
    ser=Service.query.filter_by(id=id).first()
    return ser
def get_service_req(id):
    ser=ServiceRequest.query.filter_by(id=id).first()
    print(id)
    print(ser)
    return ser
def get_pro(id):
    ser=User_Details.query.filter_by(id=id).first()
    return ser
def get_cus(id):
    ser=User_Details.query.filter_by(id=id).first()
    return ser
def cleaning():
    clean=Service.query.filter(Service.description.ilike("%cleaning%")).all()
    return clean
def electrical():
    electric=Service.query.filter(Service.description.ilike("electric")).all()
    return electric
def repair():
    repair=Service.query.filter(Service.description.ilike("repair")).all()
    return repair
def others():
    all=Service.query.all()
    return all
def pro():
    professionals=User_Details.query.filter_by(user_type='professional').all()
    return professionals
def review():
    ser=Service.query.all()
    return ser


def get_professional_rating(professional_id):
    # Query to calculate the average rating for the professional
    average_rating = db.session.query(func.avg(Review.rating)) \
        .join(ServiceRequest, Review.service_request_id == ServiceRequest.id) \
        .filter(ServiceRequest.professional_id == professional_id) \
        .scalar()
    
    # Check if there are ratings and return the result
    if average_rating is not None:
        return round(average_rating, 2)  # Round to 2 decimal places
    else:
        return "No ratings available for this professional."




def row(id):
    # Query to fetch service request details related to a specific professional
    his = db.session.query(
    User_Details.phone_num,  # Phone number from User_Details
    ServiceRequest.service_id,  # Service ID
    ServiceRequest.customer_id,  # Customer ID
    ServiceRequest.professional_id,  # Professional ID
    ServiceRequest.id,  # Service Request ID
    ServiceRequest.service_status  # Service Status
).outerjoin(
    User_Details, ServiceRequest.professional_id == User_Details.id  # Outer join with User_Details
).filter(
    ServiceRequest.customer_id == id  # Filter by customer ID
).all()  # Fetch all results
  # Fetch the results
    
    # Process the result into a list of dictionaries
    results = []
    for row in his:
        results.append({
            "phone_num": row[0],
            "service_id": row[1],
            "customer_id": row[2],
            "professional_id": row[3],
            "service_request_id": row[4],
            "service_status": row[5]
        })
    # print(results)
    return results

def col(id,ser_no):
    # Query to fetch service request details related to a specific professional
    his = db.session.query(
    User_Details.phone_num,  # Phone number from User_Details
    ServiceRequest.service_id,  # Service ID
    ServiceRequest.customer_id,  # Customer ID
    ServiceRequest.professional_id,  # Professional ID
    ServiceRequest.id,  # Service Request ID
    ServiceRequest.service_status  # Service Status
).outerjoin(
    User_Details, ServiceRequest.professional_id == User_Details.id  # Outer join with User_Details
).filter(
    ServiceRequest.customer_id == id, ServiceRequest.id==ser_no  # Filter by customer ID
).first()  # Fetch all results
  # Fetch the results
    
    # Process the result into a list of dictionaries
    # results = []
    # for row in his:
    #     results.append({
    #         "phone_num": row[0],
    #         "service_id": row[1],
    #         "customer_id": row[2],
    #         "professional_id": row[3],
    #         "service_request_id": row[4],
    #         "service_status": row[5]
    #     })
    # print(his.id)
    return his

def get_accepted_requests_by_professional_and_date(professional_id, date_filter):
    
    results = db.session.query(
        User_Details.fullname.label("customer_name"),
        User_Details.phone_num.label("customer_phone"),
        User_Details.address.label("customer_location"),
        ServiceRequest.date_of_request.label("request_date")
        
    ).join(ServiceRequest, User_Details.id == ServiceRequest.customer_id) \
     .filter(ServiceRequest.professional_id == professional_id) \
     .filter(ServiceRequest.service_status == 'accepted') \
     .filter(ServiceRequest.date_of_request.ilike(f"%{date_filter}%")) \
     .all()
    
    # Convert results to a list of dictionaries
    accepted_requests = [
        {
            "customer_name": result.customer_name,
            "customer_phone": result.customer_phone,
            "customer_location": result.customer_location,
            "request_date": result.request_date
        }
        for result in results
    ]
    print(accepted_requests)
    return accepted_requests

def get_accepted_requests_by_professional_and_location(professional_id, location):
    
    results = db.session.query(
        User_Details.fullname.label("customer_name"),
        User_Details.phone_num.label("customer_phone"),
        User_Details.address.label("customer_location"),
        ServiceRequest.date_of_request.label("request_date")
        
    ).join(ServiceRequest, User_Details.id == ServiceRequest.customer_id) \
     .filter(ServiceRequest.professional_id == professional_id) \
     .filter(ServiceRequest.service_status == 'accepted') \
     .filter(User_Details.address.ilike(f"%{location}%")) \
     .all()
    
    # Convert results to a list of dictionaries
    accepted_requests = [
        {
            "customer_name": result.customer_name,
            "customer_phone": result.customer_phone,
            "customer_location": result.customer_location,
            "request_date": result.request_date
        }
        for result in results
    ]
    print(accepted_requests)
    return accepted_requests




def user_summary():
    try:
        # Example data, replace this with actual data fetching logic

        prof = pro()  # Fetch the list of professional data
        summary = {}
        for t in prof:
            summary[t.service_type] = t.experience  # Map service type to experience

        # Extract keys and values for the plot
        x_names = list(summary.keys())
        y_experience = list(summary.values())

        # Create the plot
        plt.figure(figsize=(10, 6))  # Set figure size for better visibility
        plt.bar(x_names, y_experience, color="blue", width=0.6)
        plt.title("Service Type vs. Experience", fontsize=20)
        plt.xlabel("Service Type", fontsize=15)
        plt.ylabel("Experience (Years)", fontsize=15)
        plt.xticks(rotation=45, ha="right", fontsize=14)  # Adjust tick labels
        plt.yticks(fontsize=14)  # Adjust font size for y-axis ticks
        plt.tight_layout()   # Adjust layout to fit everythin
        return plt
        # Save the plo
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def customer_summary():
    try:
        prof = review()  # Fetch the list of professional data
        summary = {}
        for t in prof:
            summary[t.name] = t.time_required  # Map service type to experience

        # Extract keys and values for the plot
        x_names = list(summary.keys())
        y_experience = list(summary.values())

        # Plot the data
        plt.figure(figsize=(10, 6))  # Set figure size for better visibility
        plt.bar(x_names, y_experience, color="blue", width=0.6)
        plt.title("Service Type vs. Time Required", fontsize=29)
        plt.xlabel("Service Type", fontsize=25)
        plt.ylabel("Time Required (in min)", fontsize=25)
        plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for readability
        plt.tight_layout()  # Adjust layout to fit everything

        # Return the plot
        return plt

    except Exception as e:
        print(f"Error: {e}")
        return None
