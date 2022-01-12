#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from app import db
from .algorithm.continuous import continuous_analysis, continuous_zeros_analysis
from flask import url_for
from time import time

FORMAT_DATA = '%Y-%m-%d'
FORMAT_DATA_TIME = '%Y-%m-%d %H:%M:%S'


class Project(db.Model):
    """project table"""
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    describe = db.Column(db.Text, nullable=True)
    datas = db.relationship('Data', backref='project')
    parameter_types = db.relationship('ParameterTypes', backref='project')


class Data(db.Model):
    """DATA table"""
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=True)  # 数据上传时间
    is_abnormal = db.Column(db.Boolean, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    abnormals = db.relationship('Abnormal', backref='data')  # 数据和异常建立一对多关系，一条数据对应多个异常

    parameters = db.relationship('Parameter', backref='data')  # 数据和参数建立一对多关系，一条数据对应多个参数

    def __init__(self, time=None, is_abnormal=None):
        self.time = time
        self.is_abnormal = is_abnormal

    @property
    def show_dict(self):
        d = dict()
        d['id'] = self.id
        d['时间'] = self.time.strftime(FORMAT_DATA_TIME)
        for x in self.parameters:
            d[x.parameter_type.name] = x.value
        d['abnormals'] = [x.parameter_type.name for x in self.parameters if x.is_abnormal is True]
        d['auto_check_detail'] = url_for("main.abnormal_detail", page=int(self.id / 10) if int(self.id / 10) else 1,
                                         a_id=self.id)
        d['manual_check_detail'] = url_for("main.manual_detail", page=int(self.id / 10) if int(self.id / 10) else 1,
                                           a_id=self.id)
        return d

    @staticmethod
    def transcendence_analysis(top: float, bottom: float, para_type_id: int):
        p = Parameter.query.filter_by(parameter_type_id=para_type_id).all()
        for x in p:
            if x.transcendence(top=top, bottom=bottom):
                x.data.is_abnormal = True
                x.is_abnormal = True
                _n = Abnormal()
                _n.parameter_id = x.id
                _n.abnormal_type_id = AbnormalTypes.query.filter_by(name="transcendence").first().id
                _n.parameter_type_id = para_type_id
                x.data.abnormals.append(_n)
                db.session.add(x)
        db.session.commit()

    @staticmethod
    def empty_analysis(para_type_id: int):
        p = Parameter.query.filter_by(parameter_type_id=para_type_id).all()
        for x in p:
            if x.empty():
                x.data.is_abnormal = True
                x.is_abnormal = True
                _n = Abnormal()
                _n.parameter_id = x.id
                _n.abnormal_type_id = AbnormalTypes.query.filter_by(name="empty").first().id
                _n.parameter_type_id = para_type_id
                x.data.abnormals.append(_n)
                db.session.add(x)
        db.session.commit()

    @staticmethod
    def empty_analysis_range(para_type_id: int, datas_id: list):
        s_time = time()
        p = Parameter.query.filter_by(parameter_type_id=para_type_id).filter(Parameter.data_id.in_(datas_id)).all()
        empty_abnormal_id = AbnormalTypes.query.filter_by(name="empty").first().id
        p_list = []
        for x in p:
            if x.empty():
                x.data.is_abnormal = True
                x.is_abnormal = True
                _n = Abnormal()
                _n.parameter_id = x.id
                _n.abnormal_type_id = empty_abnormal_id
                _n.parameter_type_id = para_type_id
                x.data.abnormals.append(_n)
                p_list.append(x)
        db.session.add_all(p_list)
        db.session.commit()
        print("空值检测共用时%d" % (time() - s_time))

    @staticmethod
    def continuous_analysis(para_type_id: int, n: int):
        """
        对参数类型符合para_type_id的数据进行连续异常分析
        :param para_type_id:
        :param n:
        :return:
        """
        p = Parameter.query.filter_by(parameter_type_id=para_type_id).all()
        abnotmal_list = continuous_analysis(p, n)
        abnormal_id = AbnormalTypes.query.filter_by(name="continuous_not_zero").first().id
        p_list = []
        for x in abnotmal_list:
            x.data.is_abnormal = True
            x.is_abnormal = True
            _n = Abnormal()
            _n.parameter_id = x.id
            _n.abnormal_type_id = abnormal_id
            _n.parameter_type_id = para_type_id
            x.data.abnormals.append(_n)
            p_list.append(x)
        db.session.add_all(p_list)
        db.session.commit()

    @staticmethod
    def continuous_analysis_range(para_type_id: int, n: int, datas_id: list):
        """
        对参数类型符合para_type_id的数据进行连续异常分析
        :param para_type_id:
        :param n:
        :return:
        """
        p = Parameter.query.filter_by(parameter_type_id=para_type_id).filter(Parameter.data_id.in_(datas_id)).all()
        abnormal_list = continuous_analysis(p, n)
        abnormal_id = AbnormalTypes.query.filter_by(name="continuous_not_zero").first().id
        _start_a_id = db.session.execute("select MAX(id) from abnormal").first()[0]
        start_a_id = _start_a_id + 1 if _start_a_id else 1
        p_list = []
        d_list = []
        ab_list = []
        for x in abnormal_list:
            p_list.append(x.id)
            d_list.append(x.data_id)
            ab_list.append({
                "id": start_a_id,
                "data_id": x.data_id,
                "parameter_id": x.id,
                "abnormal_type_id": abnormal_id,
                "parameter_type_id": para_type_id})
            start_a_id += 1
        if len(abnormal_list):
            db.session.execute("update parameter set is_abnormal = 1 where id in " + "(" + str(p_list)[1:-1] + ")")
            db.session.execute("update data set is_abnormal = 1 where id in " + "(" + str(d_list)[1:-1] + ")")
            db.session.execute(Abnormal.__table__.insert(), ab_list)
            db.session.commit()

    @staticmethod
    def continuous_zero_analysis_range(para_type_id: int, n: int, datas_id: list):
        """
        对参数类型符合para_type_id的数据进行连续异常分析
        :param para_type_id:
        :param n:
        :return:
        """
        p = Parameter.query.filter_by(parameter_type_id=para_type_id).filter(Parameter.data_id.in_(datas_id)).all()
        abnormal_list = continuous_zeros_analysis(p, n)
        abnormal_id = AbnormalTypes.query.filter_by(name="continuous_zero").first().id
        _start_a_id = db.session.execute("select MAX(id) from abnormal").first()[0]
        start_a_id = _start_a_id + 1 if _start_a_id else 1
        p_list = []
        d_list = []
        ab_list = []
        for x in abnormal_list:
            p_list.append(x.id)
            d_list.append(x.data_id)
            ab_list.append({
                "id": start_a_id,
                "data_id": x.data_id,
                "parameter_id": x.id,
                "abnormal_type_id": abnormal_id,
                "parameter_type_id": para_type_id})
            start_a_id += 1
        if len(abnormal_list):
            db.session.execute("update parameter set is_abnormal = 1 where id in " + "(" + str(p_list)[1:-1] + ")")
            db.session.execute("update data set is_abnormal = 1 where id in " + "(" + str(d_list)[1:-1] + ")")
            db.session.execute(Abnormal.__table__.insert(), ab_list)
            db.session.commit()

    def get_para_tuple(self, para_type_id_list: list):
        l = []
        for x in para_type_id_list:
            p = Parameter.query.filter(Parameter.data_id == self.id and Parameter.parameter_type_id == x).first()
            l.append(p.value)
        return tuple(l)


class Abnormal(db.Model):
    """abnormal table"""
    __tablename__ = 'abnormal'
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))
    abnormal_type_id = db.Column(db.Integer, db.ForeignKey('abnormal_types.id'))
    parameter_type_id = db.Column(db.Integer, db.ForeignKey('parameter_types.id'))
    parameter_id = db.Column(db.Integer, db.ForeignKey('parameter.id'))

    @property
    def show_dict(self):
        return {
            'id': self.id,
            'data_id': self.data_id,
            'abnormal_type_id': self.abnormal_type_id,
            'parameter_type_id': self.parameter_type_id
        }


class AbnormalTypes(db.Model):
    """Abnormal table"""
    __tablename__ = 'abnormal_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    abnormals = db.relationship('Abnormal', backref='abnormal_type')


class Parameter(db.Model):
    """parameter table"""
    __tablename__ = 'parameter'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=True)
    is_abnormal = db.Column(db.Boolean, nullable=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data.id'))
    parameter_type_id = db.Column(db.Integer, db.ForeignKey('parameter_types.id'))
    abnormals = db.relationship('Abnormal', backref='parameter')

    k = 2
    max_iter = 2

    def __init__(self, value=None, data_id=None, parameter_type_id=None):
        self.value = value
        self.data_id = data_id
        self.parameter_type_id = parameter_type_id

    def empty(self):
        if self.value is None:
            return True
        else:
            return False

    def transcendence(self):
        _min = self.parameter_type.min
        _max = self.parameter_type.max
        if _min is not None and _max is not None:
            if self.value is not None and (self.value < _min or self.value > _max):
                return True
        elif _min is not None:
            if self.value is not None and (self.value < _min):
                return True
        elif _max is not None:
            if self.value is not None and (self.value > _max):
                return True
        return False

    @property
    def show_dict(self):
        return {
            'id': self.id,
            'value': self.value,
            'is_abnormal': self.is_abnormal,
            'data_id': self.data_id,
            'parameter_type_id': self.parameter_type_id,
        }


def transcendence_analysis(para: Parameter, top: float, bottom: float):
    if para.value > top or para.value < bottom:
        return True


class ParameterTypes(db.Model):
    """parameter type table"""
    __tablename__ = 'parameter_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    # unit = db.Column(db.String(64))
    max = db.Column(db.Float, nullable=True)
    min = db.Column(db.Float, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    abnormals = db.relationship('Abnormal', backref='parameter_type')
    parameters = db.relationship('Parameter', backref='parameter_type')

    def __init__(self, name=None):
        self.name = name
        # self.unit = unit
        db.session.add(self)
        db.session.commit()


class CheckStandard(db.Model):
    """check standard table"""
    __tablename__ = 'check_standard'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    value = db.Column(db.Float, nullable=True)

    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value
        db.session.add(self)
        db.session.commit()
