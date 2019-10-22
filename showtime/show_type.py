#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
'''
该模块包含了Show类的定义
'''
import re
from showtime import show_pb2

def check_params(requested_params, params):
    for param in requested_params:
        if params.get(param) is None:
            raise Exception('%s is requested param, but not found.', param)

class ShowList(list):
    def __init__(self, source):
        super(ShowList, self).__init__()
        self.souce = source
    def add_show(self, show):
        if not isinstance(show, Show):
            raise TypeError('Show type requested, but get %s.' % type(show))
        self.append(show)
    def add_shows(self, shows):
        for show in shows:
            self.add_show(show)
        

class Show(list):
    """存储具体单个show的所有场次的类
    Attributes:
        name: show的名称
        url: show具体介绍的url
    """
    def __init__(self, params):
        """类Show的构造函数
        Args:
            params: 至少包含'name'和'url'的dict，其中，
                        - name: show的名字
                        - url: show具体介绍的url
        """
        super(Show, self).__init__()
        if not isinstance(params, dict):
            raise TypeError('dict type requested, but get %s.' % type(params))
        check_params(['name', 'url'], params)
        for attr, value in params.items():
            setattr(self, attr, value)
    
    def add_event(self, detailed_info):
        """向Show中添加一个场次
        Args:
            detailed_info: 至少包含'day_date', 'time_date', 'province',
                           'place', 'in_sale_price', 'sold_out_price'.
                           若不包含'url'字段则用self.url填充
        """
        if 'url' not in detailed_info:
            detailed_info['url'] = self.url
        self.append(Event(detailed_info))

    def add_events(self, detailed_infos):
        for info in detailed_infos:
            self.add_event(info)

    def __str__(self):
        return '[%s] %s' % (self.name, self.url)


class Event(dict):
    def __init__(self, params):
        """类Event的构造函数
        Args:
            params: 至少包含'day_date', 'time_date', 'url', 'province', 'place',
                    'in_sale_price', 'sold_out_price'的dict，其中，
                          - day_date: 该场具体日期
                            <format>: YYYY-mm-dd
                          - time_date: 该场当天具体时间
                            <format>: HH:MM
                          - url: 该场购票详细地址(这项如果拿不到，则用self.url填充)
                            <format>: url should begin with 'http' or 'https'
                          - province: 该场所在省份
                            <format>: 34个省级行政区域以及一线，新一线和二线城市，
                                      不带'省'和'市'等后缀，2-3个字
                          - place: 该场具体位置
                            <format>: pass
                          - in_sale_price: 仍在销售中的价格
                            <format>: the list of float elements
                          - sold_out_price: 已经卖完的价格
                            <format>: the list of float elements
        Raises:
            Exception: 当params中不存在'day_date', 'time_date', 'url', 'province',
                       'place', 'in_sale_price', 'sold_out_price'或数据格式不正确
                       时会抛出异常
        """
        super(Event, self).__init__()
        if not isinstance(params, dict):
            raise TypeError('dict type requested, but get %s.' % type(params))
        requested_params = ['day_date', 'time_date', 'url', 'province', 'place', 'in_sale_price', 'sold_out_price']
        check_params(requested_params, params)
        for param in requested_params:
            valid_param = getattr(self, '_valid_%s'%param)
            if not valid_param(params.get(param)):
                raise Exception('The format of [%s]<%s> is incorrect.' % (param, str(params.get(param))))
        for key in params:
            self[key] = params[key]

    def _valid_day_date(self, day_date):
        return re.match(r'\d{4}-\d{1,2}-\d{1,2}', day_date) is not None
    
    def _valid_time_date(self, time_date):
        return re.match(r'\d{1,2}:\d{2}', time_date) is not None
    
    def _valid_url(self, url):
        return re.match(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$', url) is not None
    
    def _valid_province(self, province):
        # data from: https://baike.baidu.com/item/中国城市新分级名单?fr=aladdin
        if not hasattr(self, 'valid_provinces'):
            self.valid_provinces = set(['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', \
                                        '吉林', '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', \
                                        '山东', '河南', '湖北', '湖南', '广东', '海南', '四川', \
                                        '贵州', '云南', '陕西', '甘肃', '青海', '台湾', '内蒙古', \
                                        '广西', '西藏', '宁夏', '新疆', '香港', '澳门']) | \
                                   set(['北京', '上海', '广州', '深圳']) | \
                                   set(['成都', '杭州', '重庆', '武汉', '西安', '苏州', '天津', \
                                        '南京', '长沙', '郑州', '东莞', '青岛', '沈阳', '宁波', '昆明']) | \
                                   set(['无锡', '佛山', '合肥', '大连', '福州', '厦门', '哈尔滨', \
                                        '济南', '温州', '南宁', '长春', '泉州', '石家庄', '贵阳', \
                                        '南昌', '金华', '常州', '南通', '嘉兴', '太原', '徐州', \
                                        '惠州', '珠海', '中山', '台州', '烟台', '兰州', '绍兴', \
                                        '海口', '扬州'])
        return province in self.valid_provinces
    
    def _valid_place(self, place):
        return True
    
    def _valid_prices(self, prices):
        if not isinstance(prices, list):
            return False
        for price in prices:
            if not isinstance(price, float):
                return False
        return True
    
    def _valid_in_sale_price(self, prices):
        return self._valid_prices(prices)
    
    def _valid_sold_out_price(self, prices):
        return self._valid_prices(prices)
    
    def __str__(self):
        info_str = ''
        for item, value in self.items():
            info_str += '<%s>: %s\n' % (item, str(value))
        return info_str
