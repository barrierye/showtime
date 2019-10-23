#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
'''
该模块包含了ShowList，Show，Event类的定义
'''
import re
from showtime import show_type_pb2
from google.protobuf import text_format

def check_params(requested_params, params):
    for param in requested_params:
        if params.get(param) is None:
            raise Exception('%s is requested param, but not found.', param)

class ShowList(list):
    def __init__(self, source):
        super(ShowList, self).__init__()
        self.source = source
        self.proto = None
    def add_show(self, show):
        if not isinstance(show, Show):
            raise TypeError('Show type requested, but get %s.' % type(show))
        self.append(show)
    def add_shows(self, shows):
        for show in shows:
            self.add_show(show)
    def save(self, filename, display_chinese=True):
        self.gen_proto()
        with open(filename, 'w') as f:
            # set as_utf8 to True can correctly displays Chinese characters
            # see: https://github.com/protocolbuffers/protobuf/issues/4062
            f.write(text_format.MessageToString(self.proto, as_utf8=display_chinese))
    def serialize_save(self, filename):
        self.gen_proto()
        with open(filename, 'wb') as f:
            f.write(self.proto.SerializeToString())
    @staticmethod
    def load(filename):
        proto = show_type_pb2.ShowList()
        with open(filename, 'r') as f:
            text_format.Parse(f.read(), proto)
        return ShowList.parse_from_proto(proto)
    @staticmethod
    def serialize_load(self, filename):
        proto = show_type_pb2.ShowList()
        with open(filename, 'rb') as f:
            proto.ParseFromString(f.read())
        return ShowList.parse_from_proto(proto)
    def gen_proto(self):
        if self.proto is not None:
            return self.proto
        self.proto = show_type_pb2.ShowList()
        self.proto.source = self.source
        for show in self:
            self.proto.shows.append(show.gen_proto())
        return self.proto
    @staticmethod
    def parse_from_proto(proto):
        showlist = ShowList(proto.source)
        for show in proto.shows:
            showlist.append(Show.parse_from_proto(show))
        return showlist  

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
        requested_params = ['name', 'url']
        check_params(requested_params, params)
        self.name = params['name']
        self.url = params['url']
        for param in requested_params:
            params.pop(param)
        self.extra_fields = params
    def add_event(self, detailed_info):
        """向Show中添加一个场次
        Args:
            detailed_info: 至少包含'day_date', 'time_date', 'province',
                           'place', 'in_sale_prices', 'sold_out_prices'.
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
    def gen_proto(self):
        proto = show_type_pb2.Show()
        proto.name = self.name
        proto.url = self.url
        for key, value in self.extra_fields.items():
            proto.extra_fields[key] = value
        for event in self:
            proto.events.append(event.gen_proto())
        return proto
    @staticmethod
    def parse_from_proto(proto):
        params = {'name': proto.name, 'url': proto.url}
        for extra in proto.extra_fields:
            params[extra.key] = extra.value
        show = Show(params)
        for event in proto.events:
            show.append(Event.parse_from_proto(event))
        return show

class Event(dict):
    def __init__(self, params):
        """类Event的构造函数
        Args:
            params: 至少包含'day_date', 'time_date', 'url', 'province', 'place',
                    'in_sale_prices', 'sold_out_prices'的dict，其中，
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
                          - in_sale_prices: 仍在销售中的价格
                            <format>: the list of float elements
                          - sold_out_prices: 已经卖完的价格
                            <format>: the list of float elements
        Raises:
            Exception: 当params中不存在'day_date', 'time_date', 'url', 'province',
                       'place', 'in_sale_prices', 'sold_out_prices'或数据格式不正确
                       时会抛出异常
        """
        super(Event, self).__init__()
        if not isinstance(params, dict):
            raise TypeError('dict type requested, but get %s.' % type(params))
        requested_params = ['day_date', 'time_date', 'url', 'province',
                            'place', 'in_sale_prices', 'sold_out_prices']
        check_params(requested_params, params)
        for param in requested_params:
            valid_param = getattr(self, '_valid_%s'%param)
            if not valid_param(params.get(param)):
                raise Exception('The format of [%s]<type: %s><value: %s> is incorrect.'
                        % (param, type(params.get(param)), str(params.get(param))))
        for key in requested_params:
            self[key] = params[key]
            params.pop(key)
        self.extra_fields = params
    def _valid_day_date(self, day_date):
        return re.match(r'\d{4}-\d{1,2}-\d{1,2}', day_date) is not None
    def _valid_time_date(self, time_date):
        return re.match(r'\d{1,2}:\d{2}', time_date) is not None
    def _valid_url(self, url):
        return re.match(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.'
                r'[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$', url) is not None
    def _valid_province(self, province):
        # data from: https://baike.baidu.com/item/中国城市新分级名单?fr=aladdin
        valid_provinces = set(['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', \
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
        return province in valid_provinces
    def _valid_place(self, place):
        return True
    def _valid_prices(self, prices):
        if not isinstance(prices, list):
            return False
        for price in prices:
            if not isinstance(price, float):
                return False
        return True
    def _valid_in_sale_prices(self, prices):
        return self._valid_prices(prices)
    def _valid_sold_out_prices(self, prices):
        return self._valid_prices(prices)
    def __str__(self):
        info_str = ''
        for item, value in self.items():
            info_str += '<%s>: %s\n' % (item, str(value))
        return info_str
    def gen_proto(self):
        proto = show_type_pb2.Event()
        proto.day_date = self['day_date']
        proto.time_date = self['time_date']
        proto.url = self['url']
        proto.province = self['province']
        proto.place = self['place']
        proto.in_sale_prices.extend(self['in_sale_prices'])
        proto.sold_out_prices.extend(self['sold_out_prices'])
        for key, value in self.extra_fields.items():
            proto.extra_fields[key] = value
        return proto
    @staticmethod
    def parse_from_proto(proto):
        params = {'day_date': proto.day_date,
                  'time_date': proto.time_date,
                  'url': proto.url,
                  'province': proto.province,
                  'place': proto.place,
                  'in_sale_prices': list(proto.in_sale_prices),
                  'sold_out_prices': list(proto.sold_out_prices)}
        for key, value in proto.extra_fields.items():
            params[key] = value
        event = Event(params)
        return event
