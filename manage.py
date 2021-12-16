#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
import os
from app import create_app, db
from app.models import Data, AbnormalTypes, Parameter, ParameterTypes, Abnormal
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def reset_data():
    db.drop_all()
    db.create_all()


def make_shell_context():
    return dict(app=app,
                db=db,
                Data=Data,
                AbnormalTypes=AbnormalTypes,
                Parameter=Parameter,
                ParameterTypes=ParameterTypes,
                Abnormal=Abnormal)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
