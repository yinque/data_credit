import pandas as pd
from sklearn.cluster import KMeans
from pandas.core.frame import DataFrame


class Parameter:
    id = 0
    value = 0
    is_abnormal = False
    data_id = 0
    parameter_type_id = 0

    def __init__(self, id, value, k=2, max_iter=2):
        self.id = id
        self.value = value
        self.n_cluster = k  # k值
        self.max_iter = max_iter  # 迭代次数

    def __repr__(self):
        return '<Parameter> id="{}" value="{}"\n'.format(self.id, self.value)


def kmeans_analysis(para_list: list, k: int, i: int, j: int):
    '''
    通过k-means聚类算法检测一列数据，聚类后簇中数据个数小于i值则为异常
    :param para_list:Parameter类型的数据列
    :param k: 聚类个数即K值
    :param i: 簇中数据个数判断的标准值
    :param j: 聚类时的迭代次数
    :return:Parameter类型的数据列，内容为出现了异常的数据id
    '''
    abnormal_list = []
    result_list = []
    new_list = []

    # 1取出para_list中的各个对象p.value, 放入new_list
    for x in range(len(para_list)):
        new_list.append(0)
        new_list[x] = para_list[x].value
    # print(new_list)

    # 2对new_list应用算法，得到异常数据索引 result_list
    data_df = DataFrame(new_list)
    # print(data_df.isnull().sum())  # 查看空值情况
    data = data_df.dropna(axis=0, how='any')  # 去空，删除含有空值的行
    # print(data)
    kmeans = KMeans(n_clusters=k, max_iter=j)
    kmeans.fit(data)  # 训练模型
    data['cluster'] = kmeans.predict(data)  # 计算每个记录所属的簇
    cluster = data.cluster.value_counts()  # 查看每个簇的分布
    # print(cluster)  # 输出每个簇的分布情况

    cluster_dict = dict()
    for n in range(k):
        cluster_dict[str(n)] = []
    #     # cluster_dict[str(n)] = data[(data['cluster'] == n)]

    for n in range(0, k):
        res0Series = pd.Series(kmeans.labels_)
        res0 = res0Series[res0Series.values == n]
        cluster_dict[str(n)].extend(res0.index)
        if cluster[n] < i:  # 判断所有簇中的数据个数是否小于i
            res0Series = pd.Series(kmeans.labels_)
            res0 = res0Series[res0Series.values == n]
            # print(res0.index)

            '''
            #可以具体查看异常数据属于哪个簇和数据
            df = pd.DataFrame(para_list)
            print(res0)
            print(df.iloc[res0.index])
            print(res0.index, res0.values)
            '''
            result_list.extend(res0.index)

    for x in cluster_dict:
        cluster_dict[x] = [para_list[y].id for y in cluster_dict[x]]
    for x in range(k):
        cluster_dict['length_' + str(x)] = len(cluster_dict[str(x)])
    # print(result_list)

    # 3遍历result_list，从para_list中取出对应的对象p, 放入结果abnormal_list
    for y in result_list:
        abnormal_list.append(para_list[y])
    return abnormal_list, cluster_dict  # 返回异常数据的id

# if __name__ == '__main__':
#     datafile = 'E:/File/8.xlsx'  # 数据存放路径
#
#     para_list = []
#     data1 = pd.read_excel(datafile, usecols=['温度'])  # 读取列表数据
#
#     for x in range(len(data1.values)):
#         value = float(data1.values[x][0].split('P')[0]) if isinstance(data1.values[x][0], str) else data1.values[x][0]
#         p = Parameter(x + 1, value)
#         para_list.append(p)
#
#     k1 = 7  # 建议使用K值为7
#     i1 = 8
#     j1 = 10
#     a_l1 = kmeans_analysis(para_list, k1, i1, j1)
#     print(a_l1)  # 输出异常数据的id
