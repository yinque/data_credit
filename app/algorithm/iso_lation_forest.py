#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2022/1/14'
"""
import random
import pandas as pd
from sklearn.ensemble import IsolationForest
import numpy as np


class Algorithm:
    clf = None  # 保存算法实例
    data = None  # 原始数据，包含空数据，用于去空
    data_within_empty = None  # 去空后的数据
    data_array_within_empty = None

    # 以下为自己设定的参数
    random_state = 0

    def remove_empty(self, array):
        """
        去除array中包含的空值，
        """
        data = list(zip(range(len(array)), array))
        self.data = [x[0] for x in data]
        self.data_within_empty = [x[0] for x in data if None not in x[1]]
        self.data_array_within_empty = np.array([x[1] for x in [x for x in data if None not in x[1]]])

    def full_result(self, result):
        """
        将结果恢复为输入的数据规模
        """
        _t = [x for x in self.data if x not in self.data_within_empty]
        _array_1 = [(x, 1) for x in _t]
        _array_2 = list(zip(self.data_within_empty, list(result)))
        array = _array_1 + _array_2
        return np.array([x[1] for x in sorted(array, key=lambda x: x[0])])

    def fit(self, array):
        self.clf = IsolationForest(random_state=int(self.random_state))
        self.remove_empty(array)
        self.clf.fit(self.data_array_within_empty)

    def predict(self, array):
        self.remove_empty(array)
        result = self.clf.predict(self.data_array_within_empty)
        return self.full_result(result)

    # def fit_predict(self, array):
    #     self.clf = Demo1(contamination=self.contamination)
    #     return self.clf.fit_predict(array)

    # def fit_predict(self, array):
    #     self.remove_empty(array)
    #     self.clf = Demo1(contamination=self.contamination)
    #     result = self.clf.fit_predict(self.data_array_within_empty)
    #     return self.full_result(result)
