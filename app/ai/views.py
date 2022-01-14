#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from . import ai
from flask import render_template, request, jsonify, current_app, redirect, url_for
from app import db
from ..models import Algorithm, Parameter
import os
import uuid

re_float = r'-?\d+\.?\d*e?-?\d*?'


def make_response_dict(code, msg, data):
    return {'code': code, 'msg': msg, 'data': data}


@ai.route('/set', methods=["POST", "GET"])
def set_algorithm():
    if request.method == 'POST':
        if request.method == "POST":
            data = request.get_json()
            a = Algorithm()
            a.name = data['name']
            a.description = data['desc']
            a.parameter = data['parameter']
            a.train_first = data['train_first']
            db.session.add(a)
            db.session.commit()
            return jsonify({"url": url_for('ai.upload', al_id=a.id)})
    als = Algorithm.query.all()
    return render_template('/ai/set.html', als=als)


@ai.route('/upload/<int:al_id>', methods=['POST', 'GET'])
def upload(al_id):
    if request.method == 'POST':
        file = request.files['file']
        new_filename = uuid.uuid4().hex + '.' + file.filename.split('.')[-1]
        file_path = os.path.join(current_app.config['UPLOAD_ALGORITHM_PATH'], new_filename)
        file.save(file_path)
        al = Algorithm.query.get(al_id)
        al.path = file_path
        db.session.add(al)
        db.session.commit()
        return redirect(url_for('ai.set_algorithm'))
    return render_template('/ai/upload.html', pid=al_id)


def set_para(al, s):
    for x in s.split(";"):
        print(x)
        if len(x) > 2:
            y = x.split(':')
            setattr(al, y[0], float(y[1]))


@ai.route('/test/<int:al_id>')
def test(al_id):
    al = Algorithm.query.get_or_404(al_id)
    file_name = al.path.split("/")[-1].split(".")[0]
    para = Parameter.query.all()[:1000]
    s = "upload_algorithm." + file_name
    p = __import__(s, fromlist=["Algorithm", ])
    a = p.Algorithm()
    set_para(a, al.parameter)
    if al.train_first:
        a.fit(para[:800])
        result = a.predict(para[800:])
    else:
        result = a.predict(para)
    return jsonify(result)


@ai.route('/check')
def check():
    return render_template('/ai/check.html')
