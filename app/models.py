#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/5/15'
"""
from app import db
from .algorithm.continuous import continuous_analysis
from flask import url_for
from time import time

FORMAT_DATA = '%Y-%m-%d'
FORMAT_DATA_TIME = '%Y-%m-%d %H:%M:%S'


class Data(db.Model):
    """DATA table"""
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=True)
    is_abnormal = db.Column(db.Boolean, nullable=True)

    abnormals = db.relationship('Abnormal', backref='data')  # 数据和异常建立一对多关系，一条数据对应多个异常

    parameters = db.relationship('Parameter', backref='data')  # 数据和参数建立一对多关系，一条数据对应多个参数

    def __init__(self, time=None, is_abnormal=None):
        self.time = time
        self.is_abnormal = is_abnormal
        # db.session.add(self)
        # db.session.commit()

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
                # db.session.add(x)
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
        abnormal_id = AbnormalTypes.query.filter_by(name="continuous_not_zere").first().id
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
        s_time = time()
        p = Parameter.query.filter_by(parameter_type_id=para_type_id).filter(Parameter.data_id.in_(datas_id)).all()
        abnotmal_list = continuous_analysis(p, n)
        abnormal_id = AbnormalTypes.query.filter_by(name="continuous_not_zere").first().id
        p_list = []
        for x in abnotmal_list:
            x.data.is_abnormal = True
            x.is_abnormal = True
            _n = Abnormal()
            _n.parameter_id = x.id
            _n.abnormal_type_id = abnormal_id
            _n.parameter_type_id = para_type_id
            x.data.abnormals.append(_n)
            # db.session.add(x)
            p_list.append(x)
        db.session.add_all(p_list)
        db.session.commit()
        print("连续值检测共用时%d" % (time() - s_time))


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

    def transcendence(self, top: float, bottom: float):
        if (top is not None and (self.value is not None and self.value < bottom)) or (
                bottom is not None and (self.value is not None and self.value < bottom)):
            return True
        else:
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
    unit = db.Column(db.String(64))
    max = db.Column(db.Float, nullable=True)
    min = db.Column(db.Float, nullable=True)

    abnormals = db.relationship('Abnormal', backref='parameter_type')
    parameters = db.relationship('Parameter', backref='parameter_type')

    def __init__(self, name=None, unit=None):
        self.name = name
        self.unit = unit
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
