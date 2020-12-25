from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import current_user
from flask import g

from app.dao.mysql import db
from app.models import User


migrate = Migrate()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    g.user = current_user
    return db.session.query(User).get_active(user_id)
