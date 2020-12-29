import logging
from logging.config import dictConfig
import time

from flask import Flask, request, Blueprint, g, current_app

from app.urls import blueprints
from app.dao.mysql import db
from app.exts import migrate, login_manager
from app.configs import CONFIG
from app.utils.routeconverters import RegexConverter
from app.utils import errors


def register_extensions(app):
    app.config.from_object(CONFIG)
    app.config['JSON_AS_ASCII'] = False
    app.url_map.converters['re'] = RegexConverter
    db.init_app(app)
    migrate.init_app(app=app, db=db)
    login_manager.init_app(app)


def register_blueprints(app, blueprints):
    """路由封装"""
    for blueprint in blueprints:
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint)
        else:
            raise ValueError(blueprint)


def create_app():
    dictConfig(CONFIG.LOGGING_CONFIG)

    app = Flask(__name__, static_url_path='')

    with app.app_context():
        register_extensions(app)
        register_blueprints(app=app, blueprints=blueprints)

    @app.before_request
    def record_request_from():
        g.request_from = time.time()

    @app.after_request
    def log_access(resp):
        logger = logging.getLogger('access')
        message = {
            'ip': request.remote_addr,
            'method': request.method,
            'path': request.path,
            'request': {
                'args': request.args,
                'form': request.form,
                'json': request.json,
                'files': request.files,
                'cookies': request.cookies,
                'headers': request.headers
            },
            'response': {
                'status_code': resp.status_code
            },
            'cost': time.time() - hasattr(g, 'request_from')
        }
        logger.info(f"{message}")
        return resp

    @app.errorhandler(Exception)
    def on_exception(e):
        logger = logging.getLogger('on_exception')
        if isinstance(e, errors.Error):
            err = e
            logger.log(level=err.log_level, msg=err.log, exc_info=e)
        else:
            err = errors.Error(errmsg=str(e))
            logger.critical('Unknown error:', exc_info=e)
        return err.to_dict_response()

    @app.route('/')
    def healthcheck():
        return 'ok'

    @app.route('/favicon.ico')
    def get_fav():
        return current_app.send_static_file('logo.png')
    return app


app = create_app()
