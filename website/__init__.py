from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from os import path 
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel, _

db = SQLAlchemy()
DB_NAME = "datbase.db"
babel = Babel()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret meow meow'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    db.init_app(app)
    migrate = Migrate(app, db)
    babel.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            # db.drop_all()
            db.create_all()
        print('Database created!')

@babel.localeselector
def get_locale():
    return request.args.get('lang', 'en')        