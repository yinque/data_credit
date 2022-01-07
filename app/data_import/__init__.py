#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from flask import Blueprint

data_import = Blueprint('data_import', __name__)

from . import views
