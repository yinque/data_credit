import numpy as np
import pandas as pd
from functools import wraps


# usage:  （contamination为异常比例）
# clf = Demo1(contamination=outliers_fraction)
# y_pred = clf.fit_predict(X)

# 其中：X为array形式的输入数据，维数任意
#      y_pred为一维数组形式的识别结果，形如：array([ 1,  1,  -1,  ... ,-1])，
#             -1表示相应行为异常值，1表示 相应行为正常值


class Demo1:
    def __init__(self, contamination=0.1):
        self.contamination = contamination

    # 根据识别结果把相应的y_pred置为-1
    def __get_y_pred(self, contamination, datas):
        y_pred = np.ones(len(datas), dtype=int)

        # 这里使用模拟效果，对datas的第0列按大小排序，取最小的那些行作为异常值
        neg_index = np.argsort(datas[:, 0])

        for i in range(int(len(datas) * contamination)):
            # print(neg_index[i],datas[neg_index[i],:])
            y_pred[neg_index[i]] = -1

        return y_pred

    def fit_predict(self, datas):
        # 设置结果
        y_pred = self.__get_y_pred(self.contamination, datas)

        return y_pred


class Algorithm:
    clf = None  # 保存算法实例
    data = None  # 原始数据，包含空数据，用于去空
    data_within_empty = None  # 去空后的数据
    data_array_within_empty = None

    # 以下为自己设定的参数
    contamination = 0

    def remove_empty(self, array):
        data = list(zip(range(len(array)), array))
        self.data = [x[0] for x in data]
        self.data_within_empty = [x[0] for x in data if None not in x[1]]
        self.data_array_within_empty = np.array([x[1] for x in [x for x in data if None not in x[1]]])

    def full_result(self, result):
        _t = [x for x in self.data if x not in self.data_within_empty]
        _array_1 = [(x, 1) for x in _t]
        _array_2 = list(zip(self.data_within_empty, list(result)))
        array = _array_1 + _array_2
        return np.array([x[1] for x in sorted(array, key=lambda x: x[0])])

    # def fit(self, array):
    #     self.clf = Demo1(contamination=self.contamination)
    #     self.clf.fit(array)

    # def predict(self, array):
    #     return self.clf.predict(array)

    # def fit_predict(self, array):
    #     self.clf = Demo1(contamination=self.contamination)
    #     return self.clf.fit_predict(array)

    def fit_predict(self, array):
        self.remove_empty(array)
        self.clf = Demo1(contamination=self.contamination)
        result = self.clf.fit_predict(self.data_array_within_empty)
        return self.full_result(result)
