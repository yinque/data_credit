#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2022/1/28'
"""
import pandas as pd
import numpy as np
import math
from numpy.ma import sort
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import KMeans
from pandas.core.frame import DataFrame

import warnings

warnings.filterwarnings("ignore")


class AMK12:
    def __init__(self, k, b):
        self.k = int(k)
        self.b = b

    def __get_y_pred(self, k, b, a):

        abnormal_list = []
        result_list = []
        new_list = []

        ap = AffinityPropagation(preference=-50).fit(a)
        cluster_centers_indices = ap.cluster_centers_indices_  # 预测出的中心点的索引

        n_clusters_ = len(cluster_centers_indices)  # 预测聚类中心的个数
        print('预测的聚类中心个数：%d' % n_clusters_)
        print(cluster_centers_indices)  # 聚类中心

        def start_cluster(data, t):
            zs = [data[0]]  # 聚类中心集，选取第一个模式样本作为第一个聚类中心Z1
            # 第2步：寻找Z2,并计算阈值T
            T = step2(data, t, zs)
            # 第3,4,5步，寻找所有的聚类中心
            get_clusters(data, zs, T)
            # 按最近邻分类
            result = classify(data, zs, T)
            return result

        # 分类
        def classify(data, zs, T):
            result = [[] for i in range(len(zs))]
            for aData in data:
                min_distance = T
                index = 0
                for i in range(len(zs)):
                    temp_distance = get_distance(aData, zs[i])
                    if temp_distance < min_distance:
                        min_distance = temp_distance
                        index = i
                result[index].append(aData)
            return result

        # 寻找所有的聚类中心
        def get_clusters(data, zs, T):
            max_min_distance = 0
            index = 0
            for i in range(len(data)):
                min_distance = []
                for j in range(len(zs)):
                    distance = get_distance(data[i], zs[j])
                    min_distance.append(distance)
                min_dis = min(dis for dis in min_distance)
                if min_dis > max_min_distance:
                    max_min_distance = min_dis
                    index = i
            if max_min_distance > T:
                zs.append(data[index])
                # 迭代
                get_clusters(data, zs, T)

        # 寻找Z2,并计算阈值T
        def step2(data, t, zs):
            distance = 0
            index = 0
            for i in range(len(data)):
                temp_distance = get_distance(data[i], zs[0])
                if temp_distance > distance:
                    distance = temp_distance
                    index = i
            # 将Z2加入到聚类中心集中
            zs.append(data[index])
            # 计算阈值T
            T = t * distance
            return T

        # 计算两个模式样本之间的欧式距离
        def get_distance(data1, data2):
            distance = 0
            for i in range(len(data1)):
                distance += pow((data1[i] - data2[i]), 2)
            return math.sqrt(distance)

        data = [[5], [7], [13], [14], [15], [24], [25], [34], [41], [44], [46]]
        t = 0.5
        result = start_cluster(data, t)
        for i in range(len(result)):
            print("----------第" + str(i + 1) + "个聚类----------")
            print(result[i])

        model = KMeans(n_clusters=k)  # 获取模型
        model.fit(data)  # 训练模型
        r1 = pd.Series(model.labels_).value_counts()  # 统计各个类别簇的数目
        r2 = pd.DataFrame(cluster_centers_indices)  # 找出聚类中心
        r3 = pd.DataFrame(result)
        # r3 = pd.DataFrame(result[i])
        print(r1)
        print(r1.index)
        # print(r1.index[1])
        # print(r2)
        # print(r3)

        c = sort(r1.values)  # 簇数从小到大排序
        print(c)
        # print(c[4])

        # 先全部赋值为1
        for x in range(int(len(a))):
            new_list.append(0)
            new_list[x] = 1
        # print(new_list)

        # 判断异常
        for i in range(0, k - 1):
            if (c[i] + c[i + 1]) >= b and (c[i] + c[i + 1]) < 1.1 * b:  # 从最小的簇开始，依次对簇数求和，直到和等于或刚刚超过b
                print(c[i] + c[i + 1])  # 累加结果即异常的个数
                res0Series = pd.Series(model.labels_)  # 可以查看簇的分布情况
                # print(res0Series)
                # print(res0Series.values)

                for m in range(k - 4, k):  # 通过观察从k-4开始的簇数找到对应的index
                    res0 = res0Series[res0Series.values == r1.index[m]]
                    print(res0)
                    print(res0.index)
                    result_list.extend(res0.index)
                print(result_list)

                y_pred = np.array(new_list)
                for i in range(int(len(result_list))):
                    y_pred[result_list[i]] = -1
                # print(y_pred)
                return y_pred

    def fit(self, a):
        # 设置结果
        # y_pred = self.__get_y_pred(a)
        y_pred = self.__get_y_pred(self.k, self.b, a)

        return y_pred


class Algorithm:
    clf = None  # 保存算法实例
    data = None  # 原始数据，包含空数据，用于去空
    data_within_empty = None  # 去空后的数据
    data_array_within_empty = None

    k = 7
    b = 4

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

    # def fit_predict(self, array):
    #     print("begin")
    #     self.clf = AMK12(k=self.k, b=self.b)
    #     self.clf.fit(array)

    def fit_predict(self, array):
        print("begin")
        self.remove_empty(array)
        self.clf = AMK12(k=self.k, b=self.b)
        print("finish")
        result = self.clf.fit(self.data_array_within_empty)
        return self.full_result(result)
