#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def get_current_project():
    return current_app.config['current_project']


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # 使用从config.py文件获取到的配置，根据传入的参数config_name为app添加配置
    config[config_name].init_app(app)

    db.init_app(app)

    app.add_template_global(get_current_project, 'current_project')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .ai import ai as ai_blueprint
    app.register_blueprint(ai_blueprint, url_prefix='/ai')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .data_import import data_import as data_import_blueprint
    app.register_blueprint(data_import_blueprint, url_prefix='/data_import')

    from .project import project as project_blueprint
    app.register_blueprint(project_blueprint, url_prefix='/project')

    return app
