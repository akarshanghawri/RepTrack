from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os 
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app() :
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="secretKey",
        SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite"
    )

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"   # redirect if not logged in

    from . import models                # ensures models are registered before create_all()
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app



from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
