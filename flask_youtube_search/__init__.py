from flask import Flask
from .routes import main
from .extensions import mysql
import yaml


def create_app(config_file='settings.py'):
    app = Flask(__name__)

    # Configure db
    db = yaml.safe_load(open('db.yaml'))
    app.config['MYSQL_HOST'] = db['mysql_host']
    app.config['MYSQL_USER'] = db['mysql_user']
    app.config['MYSQL_PASSWORD'] = db['mysql_password']
    app.config['MYSQL_DB'] = db['mysql_db']

    app.secret_key = "hello"

    mysql.init_app(app)

    app.config.from_pyfile(config_file)

    app.register_blueprint(main)

    app.debug = True

    return app
