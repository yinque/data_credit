#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2022/1/13'
"""
from functools import wraps
from flask import current_app
from flask import redirect, url_for,abort


def current_project_check():
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_app.config['current_project']:
                abort(412)
            return func(*args, **kwargs)

        return decorated_function

    return decorator
