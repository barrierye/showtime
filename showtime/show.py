#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0

class Show(list):
    """存储具体单个show的所有场次的类

    Attributes:
        name: show的名称
        url: show具体介绍的url
    
    Elements in self:
        至少包含'day_date', 'time_date', 'url', 'province', 'place',
        'in_sale_price', 'sold_out_price'字段的dict
    """
    def __check_params(self, requested_params, params):
        for param in requested_params:
            if params.get(param) is None:
                raise Exception('%s is requested param, but not found.', param)
    def __init__(self, params):
        """类Show的构造函数

        Args:
            params: 至少包含'name'和'url'的dict，其中，
                        name - show的名字
                        url - show具体介绍的url

        Raises:
            Exception: 当params中不存在'name'或'url'时会抛出异常
        """
        super(Show, self).__init__()
        self.__check_params(['name', 'url'], params)
        for attr, value in params.items():
            setattr(self, attr, value)
    def add_event(self, detailed_info):
        """向Show中添加一个场次

        Args:
            detailed_info: 至少包含'day_date', 'time_date', 'url', 'province',
                           'place', 'in_sale_price', 'sold_out_price'，其中，
                                day_date - 该场具体日期
                                time_date - 该场当天具体时间
                                url - 该场购票详细地址
                                province - 该场所在省份
                                place - 该场具体位置
                                in_sale_price - 仍在销售中的价格
                                sold_out_price - 已经卖完的价格

        Raises:
            Exception: 当params中不存在'day_date', 'time_date', 'url', 'province',
                       'place', 'in_sale_price', 'sold_out_price'时会抛出异常
        """
        self.__check_params(['day_date', 'time_date', 'url', 'province', 'place', 'in_sale_price', 'sold_out_price'], detailed_info)
        self.append(detailed_info)
    def add_events(self, detailed_infos):
        for info in detailed_infos:
            self.add_event(info)
    def __str__(self):
        return '[%s] %s' % (self.name, self.url)
    def detailed_info(self):
        info_str = '[%s] %s\n' % (self.name, self.url)
        for info in self:
            for item, value in info.items():
                info_str += '<%s>: %s\n' % (item, str(value))
            info_str += '- - - - - - - - - - - - - - - - - - - - - - - - - -\n'
        return info_str
