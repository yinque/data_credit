#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from . import project
from flask import render_template, request, url_for, jsonify, current_app
from app import db
from ..models import Project, CheckStandard


@project.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        data = request.get_json()
        p = Project()
        p.name = data['name']
        p.describe = data['desc']
        db.session.add(p)
        continuous_not_zero_standard = {
            'name': '连续异常_非零',
            'description': '参数值连续不变的个数超过设定的连续个数',
            'value': 5.0,

        }
        continuous_zero_standard = {
            'name': '连续异常_零值',
            'description': '参数值连续为0的连续个数',
            'value': 5.0,
        }
        if not CheckStandard.query.filter_by(name='连续异常_非零').filter(CheckStandard.project_id == p.id).first():
            db.session.add(CheckStandard(name=continuous_not_zero_standard['name'],
                                         description=continuous_not_zero_standard['description'],
                                         value=continuous_not_zero_standard['value'],
                                         project_id=p.id))
        if not CheckStandard.query.filter_by(name='连续异常_零值').filter(CheckStandard.project_id == p.id).first():
            db.session.add(CheckStandard(name=continuous_zero_standard['name'],
                                         description=continuous_zero_standard['description'],
                                         value=continuous_zero_standard['value'],
                                         project_id=p.id))
        db.session.commit()
        return jsonify({"url": url_for('data_import.index')})
    return render_template('project/create.html')


@project.route('/get')
def get():
    projects = []
    for x in Project.query.all():
        _p = {'id': x.id, 'name': x.name}
        if current_app.config['current_project']:
            if x.id == current_app.config['current_project']['id']:
                _p['selected'] = True
            else:
                _p['selected'] = False
        else:
            _p['selected'] = False
        projects.append(_p)
    return jsonify(projects)
