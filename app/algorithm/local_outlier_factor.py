import numpy as np
import pandas as pd
from sklearn.neighbors import LocalOutlierFactor


# usage:  （contamination为异常比例）
# clf = Demo1(contamination=outliers_fraction)
# y_pred = clf.fit_predict(X)

# 其中：X为array形式的输入数据，维数任意
#      y_pred为一维数组形式的识别结果，形如：array([ 1,  1,  -1,  ... ,-1])，
#             -1表示相应行为异常值，1表示 相应行为正常值 


class Algorithm:
    clf = None  # 保存算法实例
    data = None  # 原始数据，包含空数据，用于去空
    data_within_empty = None  # 去空后的数据
    data_array_within_empty = None

    # 以下为自己设定的参数
    n_neighbors = 0
    contamination = 0

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

    # def fit_predict(self, array):
    #     self.clf = Demo1(contamination=self.contamination)
    #     return self.clf.fit_predict(array)

    def fit_predict(self, array):
        self.remove_empty(array)
        self.clf = LocalOutlierFactor(n_neighbors=int(self.n_neighbors), contamination=self.contamination)
        result = self.clf.fit_predict(self.data_array_within_empty)
        return self.full_result(result)
