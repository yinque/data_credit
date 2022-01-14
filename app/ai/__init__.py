#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from flask import Blueprint

ai = Blueprint('ai', __name__)

from . import views
