#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from . import project
from flask import render_template, request, url_for, jsonify
from app import db
from ..models import Project


@project.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        data = request.get_json()
        p = Project()
        p.name = data['name']
        p.describe = data['desc']
        db.session.add(p)
        db.session.commit()
        return jsonify({"url": url_for('data_import.index')})
    return render_template('project/create.html')
