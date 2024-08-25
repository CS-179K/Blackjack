from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Application configuration
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = 'filesystem'

    # Initialize the database
    db.init_app(app)
    with app.app_context():
        from . import models
        db.create_all()

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Define user_loader callback
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize Flask-Session
    Session(app)

    # Register the authentication blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Register the main blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Register the game blueprint
    from .Basic_Game import game as game_blueprint
    app.register_blueprint(game_blueprint, url_prefix='/game')

    from .cardcount import cardcount as cardcount_blueprint
    app.register_blueprint(cardcount_blueprint, url_prefix='/cardcount')

    return app