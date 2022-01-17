#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from . import data_import
from flask import render_template, request, current_app, redirect, url_for, jsonify
from ..models import Project, ParameterTypes, AbnormalTypes, Parameter, Data, Abnormal, CheckStandard
from app import db
import pandas as pd
from datetime import datetime
import re
import os
import uuid

re_float = r'-?\d+\.?\d*e?-?\d*?'


def make_response_dict(code, msg, data):
    return {'code': code, 'msg': msg, 'data': data}


@data_import.route('/')
def index():
    p = Project.query.all()
    return render_template('data_import/index.html', projects=p)


@data_import.route('/form/<int:pid>')
def form(pid):
    return render_template('/data_import/form.html', pid=pid)


def read_excel(src, pid):
    p = Project.query.get_or_404(pid)
    frame = pd.read_excel(src)
    columns = frame.columns
    empty_abnormal_id = AbnormalTypes.query.filter_by(name="empty").first().id
    pts = [x.name for x in p.parameter_types]
    pt_list = []
    for x in columns:
        if ('时间' in x) or ('time' in x):
            continue
        if x not in pts:
            pt = ParameterTypes(name=x)
            pt.project_id = pid
            pt_list.append(pt)
    db.session.add_all(pt_list)
    db.session.commit()
    # 完成数据元素类型建表
    column_dict = {x.name: x.id for x in p.parameter_types}
    d_list, p_list, ab_list = [], [], []
    _start_p_id = db.session.execute("select MAX(id) from parameter").first()[0]
    start_p_id = _start_p_id + 1 if _start_p_id else 1
    _start_d_id = db.session.execute("select MAX(id) from data").first()[0]
    start_d_id = _start_d_id + 1 if _start_d_id else 1
    _start_a_id = db.session.execute("select MAX(id) from abnormal").first()[0]
    start_a_id = _start_a_id + 1 if _start_a_id else 1
    for x in frame.values:
        c_v = zip(columns, x)
        d_abnormal = False

        d_list.append(
            {
                "id": start_d_id,
                "time": datetime.now(),
                "is_abnormal": d_abnormal,
                "project_id": pid
            })  # 插入一条数据
        for y in c_v:
            p_abnormal = False
            if ("时间" in y[0]) or ("time" in y[0]):
                continue
            value = re.findall(re_float, str(y[1]))[0] if not pd.isnull(y[1]) else None
            if value is None:
                d_list[-1]['is_abnormal'] = True
                p_abnormal = True
                ab_list.append({
                    "id": start_a_id,
                    "data_id": start_d_id,
                    "parameter_id": start_p_id,
                    "abnormal_type_id": empty_abnormal_id,
                    "parameter_type_id": column_dict[y[0]]})  # 插入一条异常数据到列表
                start_a_id += 1
            p_list.append({
                "id": start_p_id,
                "value": value,
                "data_id": start_d_id,
                "parameter_type_id": column_dict[y[0]],
                "is_abnormal": p_abnormal})  # 插入一条参数数据
            start_p_id += 1
        start_d_id += 1
    db.session.execute(Data.__table__.insert(), d_list)
    db.session.execute(Parameter.__table__.insert(), p_list)
    db.session.execute(Abnormal.__table__.insert(), ab_list)
    db.session.commit()
    return len(d_list), [x["id"] for x in d_list]


@data_import.route('excel/<int:pid>', methods=['POST', 'GET'])
def excel(pid):
    if request.method == 'POST':
        p = Project.query.get(pid)
        new = True if len(p.parameter_types) == 0 else False
        file = request.files['file']
        new_filename = uuid.uuid4().hex + '.' + file.filename.split('.')[-1]
        file_path = os.path.join(current_app.config['UPLOAD_PATH'], new_filename)
        file.save(file_path)
        count, data_id_list = read_excel(file_path, pid)
        start_data_id = min(data_id_list)
        end_data_id = max(data_id_list)
        if new:
            return redirect(
                url_for('data_import.set_range', pid=pid, start_data_id=start_data_id, end_data_id=end_data_id))
        else:
            return redirect(
                url_for('data_import.upload_success', pid=pid, start_data_id=start_data_id, end_data_id=end_data_id))
    return render_template('/data_import/upload.html', pid=pid)


@data_import.route('set_range/<int:pid>/<int:start_data_id>/<int:end_data_id>/', methods=['POST', 'GET'])
def set_range(pid, start_data_id, end_data_id):
    if request.method == "POST":
        data = request.get_json()
        pts = data['para_types']
        for x in pts:
            _pt = ParameterTypes.query.get_or_404(int(x['id']))
            _max = float(x['max']) if x['max'] != "未设置" else None
            _min = float(x['min']) if x['max'] != "未设置" else None
            if _min is not None and _max is not None:
                if _min < _max:
                    _pt.max = _max
                    _pt.min = _min
                    db.session.add(_pt)
            elif _min is not None:
                if _min < _pt.max or _pt.max is None:
                    _pt.min = _min
                    db.session.add(_pt)
            elif _max is not None:
                if _max > _pt.min or _pt.min is None:
                    _pt.max = _max
                    db.session.add(_pt)
        _zero = data['zero']
        _not_zero = data['not_zero']
        print(_zero)
        print(_not_zero)
        zero = CheckStandard.query.filter_by(name='连续异常_零值').filter(CheckStandard.project_id == pid).first()
        not_zero = CheckStandard.query.filter_by(name='连续异常_非零').filter(CheckStandard.project_id == pid).first()
        zero.value = _zero
        not_zero.value = _not_zero
        db.session.add(zero)
        db.session.add(not_zero)
        db.session.commit()
        new_url = url_for('data_import.upload_success', pid=pid, start_data_id=start_data_id, end_data_id=end_data_id)
        return jsonify(make_response_dict(200, "set successful", new_url))
    zero = CheckStandard.query.filter_by(name='连续异常_零值').filter(CheckStandard.project_id == pid).first()
    not_zero = CheckStandard.query.filter_by(name='连续异常_非零').filter(CheckStandard.project_id == pid).first()
    paras = ParameterTypes.query.filter_by(project_id=pid).all()
    return render_template('/data_import/set_range.html', paras=paras, pid=pid, zero=zero, not_zero=not_zero,
                           start_data_id=start_data_id, end_data_id=end_data_id)


@data_import.route('/upload_success/<int:pid>/<int:start_data_id>/<int:end_data_id>/')
def upload_success(pid, start_data_id, end_data_id):
    datas = Data.query.filter(Data.id > start_data_id).filter(Data.id < end_data_id).all()
    data_id_list = [x.id for x in datas]
    para_type_id_list = [x.id for x in ParameterTypes.query.all()]
    for x in para_type_id_list:
        Data.continuous_analysis_range(x, int(CheckStandard.query.filter(CheckStandard.name == '连续异常_非零').filter(
            CheckStandard.project_id == pid).first().value),
                                       data_id_list)
    for x in para_type_id_list:
        Data.continuous_zero_analysis_range(x, int(CheckStandard.query.filter(CheckStandard.name == '连续异常_非零').filter(
            CheckStandard.project_id == pid).first().value),
                                            data_id_list)
    abnormal_id = AbnormalTypes.query.filter_by(name="transcendence").first().id
    p = Project.query.get(pid)
    pts = p.parameter_types
    for x in pts:
        _min = x.min
        _max = x.max
        if _min is not None and _max is not None:
            for y in x.parameters:
                if y.data_id in data_id_list:
                    if y.value is not None and (y.value < _min or y.value > _max):
                        y.is_abnormal = True
                        y.data.is_abnormal = True
                        _a = Abnormal()
                        _a.data_id = y.data.id
                        _a.abnormal_type_id = abnormal_id
                        _a.parameter_type_id = x.id
                        _a.parameter_id = y.id
                        db.session.add(y)
                        db.session.add(_a)
        elif _min is not None:
            for y in x.parameters:
                if y.data_id in data_id_list:
                    if y.value is not None and (y.value < _min):
                        y.is_abnormal = True
                        y.data.is_abnormal = True
                        _a = Abnormal()
                        _a.data_id = y.data.id
                        _a.abnormal_type_id = abnormal_id
                        _a.parameter_type_id = x.id
                        _a.parameter_id = y.id
                        db.session.add(y)
                        db.session.add(_a)
        elif _max is not None:
            for y in x.parameters:
                if y.data_id in data_id_list:
                    if y.value is not None and (y.value > _max):
                        y.is_abnormal = True
                        y.data.is_abnormal = True
                        _a = Abnormal()
                        _a.data_id = y.data.id
                        _a.abnormal_type_id = abnormal_id
                        _a.parameter_type_id = x.id
                        _a.parameter_id = y.id
                        db.session.add(y)
                        db.session.add(_a)
    db.session.commit()
    return render_template('/data_import/upload_success.html')
