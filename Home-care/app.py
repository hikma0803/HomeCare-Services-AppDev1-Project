from flask import Flask
from backend.models import *
from backend.api_controllers import *
def init_app():
    home_app=Flask(__name__)
    
    home_app.debug=True
    home_app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///home.sqlite3"
    # app.config['UPLOAD_FOLDER'] = 'static/uploads'
    home_app.app_context().push()
    db.init_app(home_app)
    api.init_app(home_app)
    print('hello world')
    return home_app
app=init_app()
from backend.controllers import *
if __name__=="__main__":
    app.run()
    