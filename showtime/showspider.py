#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import re
import sys
import html
import requests

class Spider(object):
    def __init__(self):
        self.session = requests.Session()
    def get_regex_pattern(self, attr, regex_str, flag=0):
        if not hasattr(self, attr):
            setattr(self, attr, re.compile(regex_str, flag))
        return getattr(self, attr)
    def _is_url_begin_with_http(self, url):
        http_regex = self.get_regex_pattern('http_regex', r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$')
        return http_regex.match(url) is not None
    def _get_default_header(self, browser_type='Chrome'):
        if browser_type == 'Chrome':
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
        elif 'IE': # Internet Explorer 10
            header = {'User-Agent': 'Mozilla/5.0 (MSIE 10.0; Windows NT 6.1; Trident/5.0)'}
        elif 'iOS': # iPhone6
            header = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'}
        elif 'Android': # Android KitKat
            header = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'}
        elif 'Firefox': # Mac Firefox 33
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0'}
        elif 'Opera': # Opera 12.14
            header = {'User-Agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14'}
        elif 'Safari': # Mac Safari 7
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'}
        else:
            header = None
        return header
    def get_content_use_GET(self, url):
        return self.session.get(url, headers=self._get_default_header()).content.decode('utf-8')
    def _get_rough_info_url_list(self):
        ''' 获取url列表，从这些url中可以获取每场演出的简略信息 '''
        raise Exception('Illegal call, this function is an interface function')
    def _get_url_content_for_rough_info(self, url):
        ''' 获取给定url（从self._get_rough_info_url_list的搭配的url）的内容，default是直接GET '''
        return self.get_content_use_GET(url)
    def _parse_html_for_rough_info(self, text):
        ''' 解析html内容（从self._get_url_content_for_rough_info得到的），返回值为[{'url': xxx, 'name': yyy}, ...] '''
        raise Exception('Illegal call, this function is an interface function')
    def _get_url_content_for_detailed_info(self, url):
        ''' 获取给定url（包含演出详细信息的url）的内容，default是直接GET '''
        return self.get_content_use_GET(url)
    def _parse_html_for_detailed_info(self, text):
        ''' 解析html内容（从self._get_url_content_for_detailed_info得到的） '''
        raise Exception('Illegal call, this function is an interface function')
    def _get_rough_show_infos(self):
        ''' 获取演出的简略信息 '''
        urls = self._get_rough_info_url_list()
        rough_show_infos = []
        for url in urls:
            rough_show_infos += self._parse_html_for_rough_info(self._get_url_content_for_rough_info(url))
        return rough_show_infos
    def get_shows(self):
        rough_show_infos = self._get_rough_show_infos()
        shows = [Show(info) for info in rough_show_infos]
        for i, show in enumerate(shows):
            #  print('[parse] %s: %s' % (show.name, show.url))
            shows[i].add_events(self._parse_html_for_detailed_info(self._get_url_content_for_detailed_info(show.url)))
        return shows

class ChinaTicket(Spider):
    def __init__(self):
        super(ChinaTicket, self).__init__()   
        self.url_home = 'https://www.chinaticket.com'
    def _get_rough_info_url_list(self):
        show = 'wenyi' # only for art-shows
        url = '%s/%s'%(self.url_home, show)
        text = self.get_content_use_GET(url)
        whole_s_ticket_list_page_regex = self.get_regex_pattern('whole_s_ticket_list_page_regex', r'<div class="s_ticket_list_page">(.*?)</div>', flag=re.DOTALL)
        whole_s_ticket_list_page = whole_s_ticket_list_page_regex.findall(text)[0]
        s_ticket_list_page_regex = self.get_regex_pattern('s_ticket_list_page_regex', r'<a href="(?P<url>.*?)">\d*</a>')
        # 这里需要url解码，否则访问失败
        # see: https://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1
        urls = [html.unescape(x) for x in s_ticket_list_page_regex.findall(whole_s_ticket_list_page)]
        return [url] + urls
    def _parse_html_for_rough_info(self, text):
        rough_info_regex = self.get_regex_pattern('rough_info_regex', r'<img src="(?P<image>.*?)".*?/>\s*<a href="(?P<url>.*?)".*?>(?P<name>.*?)</a>')
        regex_res = rough_info_regex.findall(text)
        infos = [{'image': x[0], 'url': x[1].strip(), 'name': x[2].strip()} for x in regex_res]
        return infos
    def _parse_html_for_detailed_info(self, text):
        detailed_info_regex = self.get_regex_pattern('detailed_info_regex', r'<li class="f_lb_list_shijian">\s*?(?P<day_date>\d*\.\d*\.\d*).*?<span class="f14">(?P<week_date>.*?)</span> (?P<time_date>\d*:\d*).*?<a href="(?P<url>.*?)">.*?\[(?P<province>.*?)\]</span><br />  (?P<place>.*?)</a></li>.*?(?P<total_price><span.*?>.*?</span>)\s*?</li>', flag=re.DOTALL)
        regex_res = detailed_info_regex.findall(text)
        detailed_infos = [{'day_date': x[0], 'week_date': x[1], 'time_date': x[2], 'url': x[3], 'province': x[4], 'place': x[5], 'total_price': x[6]} for x in regex_res]
        in_sale_price_regex = self.get_regex_pattern('in_sale_price_regex', r'<span>(.*?)</span>')
        sold_out_price_regex = self.get_regex_pattern('sold_out_price_regex', r'<span class="ys">(.*?)</span>')
        for i, info in enumerate(detailed_infos):
            detailed_infos[i]['in_sale_price'] = in_sale_price_regex.findall(info['total_price'])
            detailed_infos[i]['sold_out_price'] = sold_out_price_regex.findall(info['total_price'])
            detailed_infos[i].pop('total_price')
        return detailed_infos

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
                raise Exception('%s is requested, but not int detailed_info', param)
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
        info_str = '[%s] %s\n' % (self.name, self.url)
        for info in self:
            for item, value in info.items():
                info_str += '<%s>: %s\n' % (item, str(value))
            info_str += '- - - - - - - - - - - - - - - - - - - - - - - - - -\n'
        return info_str

