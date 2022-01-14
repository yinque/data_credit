#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2022/1/14'
"""
import random
import pandas as pd


class Parameter:
    id = 0
    value = 0
    is_abnormal = False
    data_id = 0
    parameter_type_id = 0

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __repr__(self):
        return '<Parameter> id="{}" value="{}"\n'.format(self.id, self.value)


class Algorithm:
    k = 0
    t = 0
    trained = False

    def fit(self, parameter_list):
        self.trained = True
        print("fitted" + str(len(parameter_list)))

    def predict(self, parameter_list):
        assert self.trained
        self.k = int(self.k)
        self.t = int(self.t)
        return [x.id for x in random.choices(population=parameter_list, k=(self.k - self.t))]

