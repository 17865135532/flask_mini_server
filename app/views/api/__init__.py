from flask import Blueprint
from flask_restx import Api

from app.views.api.user import user_api
from app.configs import CONFIG
from app.utils import errors


v1 = Blueprint("v1", __name__, url_prefix='/api/v1')
api_v1 = Api(v1, title='api_v1', doc=CONFIG.DOC_URL_PATH, description=errors.gen_doc())
api_v1.add_namespace(user_api)
