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
from ..models import Algorithm, Parameter, Project, AbnormalTypes, ParameterTypes, Abnormal
import os
import uuid
from util.redis import Redis
import json
import datetime
import random
from sklearn.cluster import k_means

re_float = r'-?\d+\.?\d*e?-?\d*?'


def make_response_dict(code, msg, data):
    return {'code': code, 'msg': msg, 'data': data}


def clean_para_str(s):
    new_s = ""
    for x in s.split(";"):
        if len(x) > 2:
            y = x.split(":")
            new_s = "%s%s:%s;" % (new_s, y[0], y[1])
    return new_s


def identifier_maker():
    s = '{0:%Y%m%d%H%M%S%f}'.format(datetime.datetime.now()) + ''.join(
        [str(random.randint(1, 10)) for i in range(3)])
    return s[8:]


@ai.route('/set', methods=["POST", "GET"])
def set_algorithm():
    if request.method == "POST":
        data = request.get_json()
        a = Algorithm()
        a.name = data['name']
        a.description = data['desc']
        a.parameter = clean_para_str(data['parameter'])
        a.train_first = data['train_first']
        t = AbnormalTypes.query.filter_by(name=data['name']).first()
        assert (t is None)
        if not t:
            t = AbnormalTypes()
            t.name = data['name']
            db.session.add(t)
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


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    #
    # try:
    #     import unicodedata
    #     unicodedata.numeric(s)
    #     return True
    # except (TypeError, ValueError):
    #     pass
    return False


def set_para(al, s):
    for x in s.split(";"):
        if len(x) > 2:
            y = x.split(':')
            setattr(al, y[0], float(y[1]) if is_number(y[1]) else y[1])


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


def check_use_algorithm(algorithm_id, para_list):
    al = Algorithm.query.get_or_404(algorithm_id)
    file_name = al.path.split("/")[-1].split(".")[0]
    s = "upload_algorithm." + file_name
    p = __import__(s, fromlist=["Algorithm", ])
    a = p.Algorithm()
    set_para(a, al.parameter)
    if al.train_first:
        a.fit(para_list)
        result = a.predict(para_list)
    else:
        result = a.fit_predict(para_list)
    return result


def check_project_use_algorithm(algorithm_id, check_array):
    al = Algorithm.query.get_or_404(algorithm_id)
    file_name = al.path.split("/")[-1].split(".")[0].split("\\")[-1].split(".")[0]
    s = "upload_algorithm." + file_name
    p = __import__(s, fromlist=["Algorithm", ])
    a = p.Algorithm()
    set_para(a, al.parameter)
    # set_para(a, al.parameter)
    if al.train_first:
        a.fit(check_array)
        result = a.predict(check_array)
    else:
        result = a.fit_predict(check_array)
    return result


@ai.route('/check', methods=['POST', 'GET'])
def check():
    if request.method == "POST":
        _data = request.get_json()
        para_type_ids = [int(x) for x in _data['check_parameters']]
        para_types = ParameterTypes.query.filter(ParameterTypes.id.in_(para_type_ids)).all()
        algorithm = Algorithm.query.get(_data['algorithm_id'])
        project = Project.query.get(_data['project_id'])
        abnormal_type = AbnormalTypes.query.filter_by(name=algorithm.name).first()
        result = check_project_use_algorithm(algorithm.id, project.check_array(para_type_ids))
        data = {'parameter_types': [x.name for x in para_types],
                'algorithm': algorithm.name,
                'project': project.name,
                'num': len(result),
                'abnormal_num': len([x for x in result if x == -1]),
                'proportion': len([x for x in result if x == -1]) / len(result),
                '-1_1': [int(x) for x in list(result)]
                }
        abnormal_datas = project.get_abnormal_datas(result)
        print(abnormal_datas)
        abnormal_list = []
        for x in abnormal_datas:
            x.is_abnormal = True
            for p in x.parameters:
                if p.parameter_type_id in para_type_ids:
                    p.is_abnormal = True
                    _a = Abnormal()
                    _a.data_id = x.id
                    _a.abnormal_type_id = abnormal_type.id
                    _a.parameter_type_id = p.parameter_type_id
                    _a.parameter_id = p.id
                    abnormal_list.append(_a)
        db.session.add_all(abnormal_datas)
        db.session.add_all(abnormal_list)
        db.session.commit()
        identifier = identifier_maker()
        Redis.hset('check_result', identifier, json.dumps(data))
        new_url = url_for('ai.check_result', identifier=identifier)
        return jsonify(new_url)
    algorithms = [x.show_dict for x in Algorithm.query.all()]
    projects = Project.query.all()
    return render_template('/ai/check.html', algorithms=algorithms, projects=projects)


@ai.route('/check_result/<string:identifier>')
def check_result(identifier):
    _data = Redis.hget('check_result', identifier)
    data = json.loads(_data)
    return render_template('/ai/result.html', data=data)


@ai.route('/testRedisWrite', methods=['GET'])
def test_redis_write():
    """
    测试redis
    """
    Redis.write("test_key", "test_value", 60)
    return "ok"


@ai.route('/testRedisRead', methods=['GET'])
def test_redis_read():
    """
    测试redis
    """
    _data = Redis.hget('check_result', '1635228151547610')
    data = json.loads(_data)
    return jsonify(data)
