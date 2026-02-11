from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os 

db = SQLAlchemy()
login_manager = LoginManager()

def create_app() :
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="secretKey",
        SQLALCHEMY_DATABASE_URI="sqlite:///db.sqlite"
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"             # redirect if not logged in
    Migrate(app,db)

    from .models import User

    @login_manager.user_loader                          # register user loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app


