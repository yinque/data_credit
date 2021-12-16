#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ChangXin'
__mtime__ = '2018/5/15'
"""
from . import main
import pandas as pd
from ..models import Data, Parameter, ParameterTypes, AbnormalTypes, Abnormal, CheckStandard
from app import db
import re
from flask import render_template, request, redirect, current_app, url_for, jsonify
import os
import uuid
from datetime import datetime, timedelta
from app.pagination import Pagination
from app.algorithm.kmeans import kmeans_analysis
import time

re_float = r'-?\d+\.?\d*e?-?\d*?'
FORMAT_DATE = '%Y-%m-%d'
FORMAT_DATE_TIME = '%Y-%m-%d %H:%M:%S'


def make_response_dict(code, msg, data):
    return {'code': code, 'msg': msg, 'data': data}


@main.before_app_first_request
def create_abnormal_type():
    types = ["transcendence", "empty", "continuous_not_zero", "continuous_zero", 'kmeans']
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
    if not CheckStandard.query.filter_by(name='连续异常_非零').first():
        db.session.add(CheckStandard(name=continuous_not_zero_standard['name'],
                                     description=continuous_not_zero_standard['description'],
                                     value=continuous_not_zero_standard['value']))
    if not CheckStandard.query.filter_by(name='连续异常_零值').first():
        db.session.add(
            CheckStandard(name=continuous_zero_standard['name'], description=continuous_zero_standard['description'],
                          value=continuous_zero_standard['value']))
    for x in types:
        t = AbnormalTypes.query.filter_by(name=x).first()
        if not t:
            t = AbnormalTypes()
            t.name = x
            db.session.add(t)
    db.session.commit()
    current_app.config['abnormal_types'] = {x.name: x.id for x in AbnormalTypes.query.all()}


def create_id_list(start_id, length):
    return [x for x in range(start_id, start_id + length)]


def read_excel(src):
    frame = pd.read_excel(src)
    columns = frame.columns
    empty_abnormal_id = AbnormalTypes.query.filter_by(name="empty").first().id
    pts = [x.name for x in ParameterTypes.query.all()]
    pt_list = []
    for x in columns:
        if ('时间' in x) or ('time' in x):
            continue
        if x not in pts:
            pt_list.append(ParameterTypes(name=x))
    db.session.add_all(pt_list)
    db.session.commit()
    # 完成数据元素类型建表
    column_dict = {x.name: x.id for x in ParameterTypes.query.all()}
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
                # "time": datetime.strptime(next(c_v)[1], '%Y-%m-%d %H:%M'),
                "time": datetime.now(),
                "is_abnormal": d_abnormal
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


@main.route('/')
def index():
    return render_template('index.html')


# @main.route('/test_auto_deploy')
# def test_auto_deploy():
#     return "test 2 success"


@main.route('/auto_check')
def auto_check():
    p_types = ParameterTypes.query.all()
    p_types_id = [x.id for x in p_types]
    page = request.args.get('page', 1, type=int)
    pagination = Data.query.filter_by(is_abnormal=True).paginate(page, per_page=10, error_out=False)
    datas = pagination.items
    for data in datas:
        data.sort_para = []
        p_t_dict = {x.parameter_type_id: x for x in data.parameters}
        for x in p_types_id:
            data.sort_para.append(p_t_dict[x])
    return render_template('auto_check.html', p_types=p_types, pagination=pagination, datas=datas)


@main.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        s_time = time.time()
        file = request.files['file']
        new_filename = uuid.uuid4().hex + '.' + file.filename.split('.')[-1]
        file_path = os.path.join(current_app.config['UPLOAD_PATH'], new_filename)
        file.save(file_path)
        count, data_id_list = read_excel(file_path)
        u_time = time.time()
        para_type_id_list = [x.id for x in ParameterTypes.query.all()]
        for x in para_type_id_list:
            Data.continuous_analysis_range(x, int(CheckStandard.query.filter_by(name='连续异常_非零').first().value),
                                           data_id_list)
        end_time = time.time()
        print("创建数据共用时%d,本次上传用时%d秒" % (u_time - s_time, end_time - s_time))
        return redirect(url_for('main.upload_success', count=count))
    return render_template('upload.html')


@main.route('/upload_success/<int:count>')
def upload_success(count):
    return render_template('upload_success.html', count=count)


@main.route('/data_table')
def data_table():
    p_types = ParameterTypes.query.all()
    p_types_id = [x.id for x in p_types]
    page = request.args.get('page', 1, type=int)
    pagination = Data.query.paginate(page, per_page=10, error_out=False)
    datas = pagination.items
    for data in datas:
        data.sort_para = []
        p_t_dict = {x.parameter_type_id: x for x in data.parameters}
        for x in p_types_id:
            data.sort_para.append(p_t_dict[x])
    return render_template('data_table.html', p_types=p_types, pagination=pagination, datas=datas)


@main.route('/data_table_result', methods=['get', 'post'])
def data_table_result():
    data = request.get_json()
    page = request.args.get('page', 1, type=int)
    _datas = Data.query
    if data:
        if 'start_time' in data and 'end_time' in data:
            start_time = datetime.strptime(data['start_time'], FORMAT_DATE)
            end_time = datetime.strptime(data['end_time'], FORMAT_DATE) + timedelta(days=1)
            _datas = _datas.filter(Data.time > start_time).filter(Data.time < end_time)
    pagination = Pagination(_datas.all(), page=page, per_page=10)
    _test = pagination.get_dict()
    return jsonify(_test)


@main.route('/auto_check_result', methods=['get', 'post'])
def auto_check_result():
    page = request.args.get('page', 1, type=int)
    _datas = Data.query.filter_by(is_abnormal=True)
    pagination = Pagination(_datas.all(), page=page, per_page=10)
    _test = pagination.get_dict()
    return jsonify(_test)


@main.route('/abnormal_detail/<int:a_id>/<int:page>')
def abnormal_detail(a_id, page):
    data = Data.query.get_or_404(a_id)
    return render_template('abnormal_detail.html', a_id=a_id, page=page, data=data)


@main.route('/manual_check')
def manual_check():
    p_types = ParameterTypes.query.all()
    p_types_id = [x.id for x in p_types]
    page = request.args.get('page', 1, type=int)
    pagination = Data.query.filter_by(is_abnormal=True).paginate(page, per_page=10, error_out=False)
    datas = pagination.items
    for data in datas:
        data.sort_para = []
        p_t_dict = {x.parameter_type_id: x for x in data.parameters}
        for x in p_types_id:
            data.sort_para.append(p_t_dict[x])
    abnormal_types = AbnormalTypes.query.all()
    return render_template('manual_check.html', p_types=p_types, pagination=pagination, datas=datas,
                           abnormal_types=abnormal_types)


@main.route('/manual_check_result', methods=['get', 'post'])
def manual_check_result():
    data = request.get_json()
    page = request.args.get('page', 1, type=int)
    # _datas = Data.query.filter_by(is_abnormal=True)
    _datas = Data.query
    if data:
        if 'check_type' in data:
            if data['check_type'] == 'all':
                pass
            elif data['check_type'] == 'true':
                _datas = _datas.filter_by(is_abnormal=True)
            elif data['check_type'] == 'false':
                _datas = _datas.filter_by(is_abnormal=False)
        if 'start_time' in data and 'end_time' in data:
            start_time = datetime.strptime(data['start_time'], FORMAT_DATE)
            end_time = datetime.strptime(data['end_time'], FORMAT_DATE) + timedelta(days=1)
            _datas = _datas.filter(Data.time > start_time).filter(Data.time < end_time)
        if 'abnormal_type' in data:
            if data['abnormal_type'] == 'all':
                pass
            else:
                a_list = AbnormalTypes.query.filter_by(name=data['abnormal_type']).first().abnormals
                _datas = _datas.join(Data.abnormals).filter(Abnormal.id.in_(x.id for x in a_list))
        # if 'paras' in data:
        #     a_list = AbnormalTypes.query.filter(Abnormal.parameter_type_id.in_([int(x) for x in data['paras']])).all()
        #     _datas = _datas.join(Data.abnormals).filter(Abnormal.id.in_(x.id for x in a_list))
    pagination = Pagination(_datas.all(), page=page, per_page=10)
    _test = pagination.get_dict()
    return jsonify(_test)


@main.route('/manual_detail/<int:a_id>/<int:page>')
def manual_detail(a_id, page):
    data = Data.query.get_or_404(a_id)
    return render_template('manual_detail.html', a_id=a_id, page=page, data=data)


@main.route('/manual_alert/<int:p_id>', methods=["POST", "GET"])
def manual_alert(p_id):
    p = Parameter.query.get_or_404(p_id)
    if request.method == "POST":
        data = request.get_json()
        print(data)
        if data['value'] == "None":
            p.value = None
        else:
            p.value = float(data['value'])
        db.session.add(p)
        db.session.commit()
        return jsonify(make_response_dict(200, "alert successful", "alert successful"))
    today = datetime(year=p.data.time.year, month=p.data.time.month, day=p.data.time.day)
    tomorrow = today + timedelta(days=1)
    datas = Data.query.filter(Data.time > today).filter(Data.time < tomorrow).all()
    datas_ids = [x.id for x in datas]
    paras = Parameter.query.filter(Parameter.data_id.in_(datas_ids)).filter(
        Parameter.parameter_type_id == p.parameter_type_id).all()
    max_value = max([x.value for x in paras if x.value is not None])
    return render_template('manual_alert.html', today_max=max_value, para=p)


@main.route('/expert_rule_setup')
def expert_rule_setup():
    return render_template('expert_rule_setup.html')


@main.route('/abnormal_rule_alert', methods=["POST", "GET"])
def abnormal_rule_alert():
    if request.method == "POST":
        data = request.get_json()
        c = CheckStandard.query.filter_by(name=data['name']).first()
        c.value = float(data['value'])
        db.session.add(c)
        db.session.commit()
        return jsonify(make_response_dict(200, "alert successful", "alert successful"))
    zero = CheckStandard.query.filter_by(name='连续异常_零值').first()
    not_zero = CheckStandard.query.filter_by(name='连续异常_非零').first()
    return render_template('abnormal_rule_alert.html', zero=zero, not_zero=not_zero)


@main.route('/parameter_range_alert', methods=["POST", "GET"])
def parameter_range_alert():
    if request.method == "POST":
        data = request.get_json()
        id = int(data['id'])
        para_type = ParameterTypes.query.get_or_404(id)
        para_type.max = float(data['max'])
        para_type.min = float(data['min'])
        db.session.add(para_type)
        db.session.commit()
        return jsonify(make_response_dict(200, "alert successful", "alert successful"))
    paras = ParameterTypes.query.all()
    return render_template('parameter_range_alert.html', paras=paras)


@main.route('/intelligent_check')
def intelligent_check():
    return render_template('intelligent_check.html')


@main.route('/intelligent_rule_setup')
def intelligent_rule_setup():
    return render_template('intelligent_rule_setup.html')


@main.route('/intelligent_kmeans')
def intelligent_kmeans():
    p_types = ParameterTypes.query.all()
    id_max = Data.query.count()
    return render_template('intelligent_kmeans.html', p_types=p_types, id_max=id_max)


@main.route('/intelligent_kmeans_result')
def intelligent_kmeans_result():
    return render_template('intelligent_kmeans_result.html')


@main.route('/kmeans', methods=["POST"])
def kmeans():
    data = request.get_json()
    datas = Data.query.filter(Data.id >= data['id_start']).filter(Data.id <= data['id_end']).all()
    datas_id = [x.id for x in datas]
    para_list = Parameter.query.filter_by(parameter_type_id=int(data['para_type'])).filter(
        Parameter.data_id.in_(datas_id)).all()
    a_l, cluster_dict = kmeans_analysis(para_list=para_list, k=int(data['k']), i=int(data['i']), j=int(data['j']))
    cluster_dict['k'] = int(data['k'])
    return jsonify(make_response_dict(200, "analysis successful", cluster_dict))


@main.route('/kmeans_apply', methods=["POST"])
def kmeans_apply():
    data = request.get_json()
    ids = data['ids'].split(',')
    id_list = [int(x) for x in ids if x.isdigit()]
    p = Parameter.query.filter(Parameter.id.in_(id_list)).all()
    for x in p:
        x.data.is_abnormal = True
        x.is_abnormal = True
        _n = Abnormal()
        _n.parameter_id = x.id
        _n.abnormal_type_id = AbnormalTypes.query.filter_by(name="kmeans").first().id
        _n.parameter_type_id = x.parameter_type_id
        x.data.abnormals.append(_n)
        db.session.add(x)
    db.session.commit()
    return jsonify(make_response_dict(200, "apply successful", "apply successful"))
