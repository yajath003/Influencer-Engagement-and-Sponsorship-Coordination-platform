from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()


def create_app(**config_overrides):
    app = Flask(__name__)

    # Load config
    app.config.from_pyfile('settings.py')

    db.init_app(app)
    migrate = Migrate(app, db)

    from influencers.views import influencers_app
    from sponsors.views import sponsors_app
    from admin.views import admin_app
    from api.views import api_app

    app.register_blueprint(influencers_app)
    app.register_blueprint(sponsors_app)
    app.register_blueprint(admin_app)
    app.register_blueprint(api_app, url_prefix='/api')
    return app
