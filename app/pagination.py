#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2018/11/29'
"""
import math


class Pagination:
    """
    用来进行分页的类
    """
    page = None
    items_all = None
    per_page = None
    pages_count = None

    @staticmethod
    def get_page_data(data, per_page: int, page: int):
        """
        获取分页后的数据
        :param data:要进行分页的数据
        :param per_page:每页显示的条数
        :param page:页数
        :return:截取后的数据
        """
        return data[per_page * (page - 1):(per_page * page)]

    def __init__(self, items_all: list, page: int, per_page: int):
        """

        :param items_all:要进行分页的数据
        :param page: 页数
        :param per_page:每页条数
        """
        self.items_all = items_all
        self.per_page = per_page
        self.page = page
        self.pages_count = math.ceil(len(items_all) / per_page)

    @property
    def item_count(self):
        return len(self.items_all)

    @property
    def has_prev(self):
        """
        是否有前一页
        :return:
        """
        return 1 < self.page if 0 < self.page < self.pages_count + 1 else False

    @property
    def prev_num(self):
        """
        前一页的页码
        :return:
        """
        return self.page - 1 if 0 < self.page < self.pages_count + 1 else None

    @property
    def pages(self):
        """
        所有页的页码
        :return:
        """
        return list(range(1, int(self.pages_count + 1)))

    @property
    def has_next(self):
        """
        是否有下一页
        :return:
        """
        return self.page < self.pages_count if 0 < self.page < self.pages_count + 1 else False

    @property
    def next_num(self):
        """
        下一页的页码
        :return:
        """
        return self.page + 1 if 0 < self.page < self.pages_count + 1 else None

    @property
    def items(self):
        """
        获取该页的数据
        :return:
        """
        items = Pagination.get_page_data(self.items_all, self.per_page, self.page)
        if len(items) > 0 and hasattr(items[0], 'show_dict'):
            items = [x.show_dict for x in items]
        return items

    @property
    def enough_page(self):
        return len(self.items_all) > self.per_page

    def get_dict(self):
        """
        转换为字典
        :return:
        """
        return {
            'widget': {
                'page': self.page,
                'has_prev': self.has_prev,
                'prev_num': self.prev_num,
                'pages': self.pages,
                'has_next': self.has_next,
                'next_num': self.next_num,
                'enough_page': self.enough_page
            },
            'items': self.items
        }

    def __repr__(self):
        return "<分页> 元素数：{},总页数：{},页码：{}".format(len(self.items), self.pages_count, self.page)
