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

    def fit_predict(self, parameter_list):
        self.k = int(self.k)
        return [x.id for x in random.choices(population=parameter_list, k=self.k)]
