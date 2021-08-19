#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '一元线性回归'
__author__ = 'changxin'
__mtime__ = '2021/8/19'
"""


def get_model(xlist, ylist):
    """
    获取w,b
    :param xlist:
    :param ylist:
    :return:
    """
    avgx = sum(xlist) / len(xlist)
    wtop, wbottom = 0, 0
    for i in range(len(xlist)):
        wtop += ylist[i] * (xlist[i] - avgx)
    wbottom = sum([x * x for x in xlist]) - sum(xlist) * sum(xlist) / len(xlist)
    w = wtop / wbottom
    b = sum(ylist[i] - w * xlist[i] for i in range(len(xlist))) / len(xlist)
    return w, b


def linear(w, b, x):
    return w * x + b


if __name__ == '__main__':
    x = list(range(1, 101))
    y = list(range(2, 102))
    w, b = get_model(x, y)
    print(linear(w, b, 5))
