from flask import Flask
from backend.models import db
app=None
def setup_app():
    app=Flask(__name__)
    app.debug=True
    app.app_context().push() #direct access to other modules
    print("Household Services app is started..")

setup_app()



from backend.controllers import *

if  __name__ == "__main__":
    app.run(debug=True)
