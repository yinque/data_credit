import random
import pandas as pd
import sys


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


def continuous_analysis(para_list: list, n: int):
    """
    检测一列参数中哪些数据出现了连续n次连续不变的异常
    :param para_list:Parameter类型的数据列
    :param n: 要检测的数据连续个数
    :return:Parameter类型的数据列，内容为出现了异常的Parameter类型变量
    """
    abnormal_list = []
    head = 0
    for tail in range(len(para_list)):
        if para_list[tail].value == para_list[head].value:
            if tail - head == n - 1:
                for y in range(head, tail + 1):
                    abnormal_list.append(para_list[y])
                head += 1
        else:
            head = tail
    return list(set(abnormal_list))  # 进行了一次去重，后续可以通过优化算法去掉去重的步骤，提高效率


if __name__ == '__main__':
    p_l1 = []
    for x in range(1, 101):
        p_l1.append(Parameter(x, random.randint(1, 200)))

    for x in range(6, 12):
        p_l1[x].value = 6

    a_l1 = continuous_analysis(p_l1, 5)
    print('当检测连续数量为"{}"时，数据列1中异常数据个数为"{}"\n'.format(5, len(a_l1)))

    p_l2 = []
    for x in range(1, 101):
        p_l2.append(Parameter(x, random.randint(1, 99)))
    for x in range(5, 15):
        p_l2[x].value = 6
    for x in range(22, 33):
        p_l2[x].value = 8
    a_l2 = continuous_analysis(p_l2, 10)
    a_l3 = continuous_analysis(p_l2, 11)
    print('当检测连续数量为"{}"时，数据列2中异常数据个数为"{}"\n'.format(10, len(a_l2)))
    print('当检测连续数量为"{}"时，数据列2中异常数据个数为"{}"\n'.format(11, len(a_l3)))

    datafile = '采蒲台数据.xls'  # 数据存放路径
    # datafile = sys.argv[1]  # 读取命令行参数

    para_list = []
    data1 = pd.read_excel(datafile, usecols=['水温(℃)'])  # 读取列表数据
    for x in range(len(data1.values)):
        value = float(data1.values[x][0].split('P')[0]) if isinstance(data1.values[x][0], str) else data1.values[x][0]
        p = Parameter(x + 1, value)
        para_list.append(p)
    result = continuous_analysis(para_list, 5)
    print('当检测连续数量为"{}"时，采蒲台数据.xls中温度列异常数据个数为"{}"\n'.format(5, len(result)))

"""
当检测连输数量为"5"时，数据列1中异常数据个数为"6"

当检测连输数量为"10"时，数据列2中异常数据个数为"21"

当检测连输数量为"11"时，数据列2中异常数据个数为"11"

当检测连续数量为"5"时，采蒲台数据.xls中温度列异常数据个数为"332"
"""
