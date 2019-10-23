#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import re
import sys
import html
import requests
import multiprocessing

# Do not import Show class and ShowList class directly,
# in case the factory class incorrectly registers the
# webspider classes.
from showtime import show_type

class WebSpider(object):
    # # PAY ATTITION THAT `source` need be rewrite
    source = None
    def __init__(self):
        self._session = requests.Session()
        self._regex_pool = {}
    def get_regex_pattern(self, attr, regex_str, flag=0):
        if regex_str not in self._regex_pool:
            self._regex_pool[regex_str] = re.compile(regex_str, flag)
        return self._regex_pool[regex_str]
    def _is_url_begin_with_http(self, url):
        http_regex = self.get_regex_pattern('http_regex',
                r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.'
                '[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$')
        return http_regex.match(url) is not None
    def _get_default_header(self, browser_type='Chrome'):
        header = None
        if browser_type == 'Chrome':
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit'
                                    '/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
        elif 'IE': # Internet Explorer 10
            header = {'User-Agent': 'Mozilla/5.0 (MSIE 10.0; Windows NT 6.1; Trident/5.0)'}
        elif 'iOS': # iPhone6
            header = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit'
                                    '/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'}
        elif 'Android': # Android KitKat
            header = {'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit'
                                    '/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'}
        elif 'Firefox': # Mac Firefox 33
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0'}
        elif 'Opera': # Opera 12.14
            header = {'User-Agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14'}
        elif 'Safari': # Mac Safari 7
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14'
                                    ' (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'}
        return header
    def get_page_by_GET(self, url):
        return self._session.get(url, headers=self._get_default_header()).content.decode('utf-8')
    def _get_rough_url_list(self):
        ''' 获取url列表，从这些url中可以获取每场演出的简略信息 '''
        raise NotImplementedError
    def _get_rough_page(self, url):
        ''' 获取给定url（从self._get_rough_url_list的搭配的url）的内容，default是直接GET '''
        return self.get_page_by_GET(url)
    def _parse_for_rough_info(self, text):
        ''' 解析html内容（从self._get_rough_page得到的），返回值为[{'url': xxx, 'name': yyy}, ...] '''
        raise NotImplementedError
    def _get_detailed_page(self, url):
        ''' 获取给定url（包含演出详细信息的url）的内容，default是直接GET '''
        return self.get_page_by_GET(url)
    def _parse_for_detailed_info(self, text):
        ''' 解析html内容（从self._get_detailed_page得到的） '''
        raise NotImplementedError
    def _get_process_num(self, is_parallel, process_num, item_num):
        if process_num is None:
            if is_parallel:
                process_num = multiprocessing.cpu_count()
            else:
                process_num = 1
        if process_num > item_num:
            process_num = item_num
        if process_num <= 0:
            process_num = 1
        return process_num
    def _warpper_for_get_and_parse_for_rough_info(self, url):
        return self._parse_for_rough_info(self._get_rough_page(url))
    def _warpper_for_get_and_parse_for_detailed_info(self, url):
        return self._parse_for_detailed_info(self._get_detailed_page(url))
    def get_show_list(self, is_parallel=True, process_num=None):
        showlist = show_type.ShowList(self.source)
        urls = self._get_rough_url_list()

        pnum = self._get_process_num(is_parallel, process_num, len(urls))
        
        # get rough infos
        rough_show_infos = []
        if pnum == 1:
            for url in urls:
                rough_show_infos += self._parse_for_rough_info(self._get_rough_page(url))
        else:
            pool = multiprocessing.Pool(processes=pnum)
            for infos in pool.map(self._warpper_for_get_and_parse_for_rough_info, urls):
                rough_show_infos += list(infos)
            pool.close()
        showlist.add_shows([show_type.Show(info) for info in rough_show_infos])

        # get detailed infos
        pnum = self._get_process_num(is_parallel, process_num, len(showlist))
        if pnum == 1:
            for i, show in enumerate(showlist):
                showlist[i].add_events(self._parse_for_detailed_info(self._get_detailed_page(show.url)))
        else:
            pool = multiprocessing.Pool(processes=pnum)
            urls = [show.url for show in showlist]
            pool_outputs = pool.map(self._warpper_for_get_and_parse_for_detailed_info, urls)
            pool.close()
            for i, show in enumerate(showlist):
                showlist[i].add_events(pool_outputs[i])
        return showlist

class ChinaTicket(WebSpider):
    source = 'ChinaTicket'
    def __init__(self):
        super(ChinaTicket, self).__init__()
        self._home_url = 'https://www.chinaticket.com'
    def _get_rough_url_list(self):
        show = 'wenyi' # only for art-shows
        url = '%s/%s'%(self._home_url, show)
        text = self.get_page_by_GET(url)
        whole_s_ticket_list_page_regex = self.get_regex_pattern('whole_s_ticket_list_page_regex',
                r'<div class="s_ticket_list_page">(.*?)</div>', flag=re.DOTALL)
        whole_s_ticket_list_page = whole_s_ticket_list_page_regex.findall(text)[0]
        s_ticket_list_page_regex = self.get_regex_pattern('s_ticket_list_page_regex',
                r'<a href="(?P<url>.*?)">\d*</a>')
        # 这里需要url解码，否则访问失败
        # see: https://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1
        urls = [html.unescape(x) \
                for x in s_ticket_list_page_regex.findall(whole_s_ticket_list_page)]
        return [url] + urls
    def _parse_for_rough_info(self, text):
        rough_info_regex = self.get_regex_pattern('rough_info_regex',
                r'<img src="(?P<image>.*?)".*?/>\s*<a href="(?P<url>.*?)".*?>(?P<name>.*?)</a>')
        regex_res = rough_info_regex.findall(text)
        infos = [{'image': x[0], 'url': x[1].strip(), 'name': x[2].strip()} for x in regex_res]
        return infos
    def _parse_for_detailed_info(self, text):
        detailed_info_regex = self.get_regex_pattern('detailed_info_regex',
                r'<li class="f_lb_list_shijian">\s*?(?P<day_date>\d*\.\d*\.\d*).*?<span '
                r'class="f14">(?P<week_date>.*?)</span> (?P<time_date>\d*:\d*).*?<a href="'
                r'(?P<place_url>.*?)">.*?\[(?P<province>.*?)\]</span><br />  (?P<place>.*?)'
                r'</a></li>.*?(?P<total_price><span.*?>.*?</span>)\s*?</li>', flag=re.DOTALL)
        regex_res = detailed_info_regex.findall(text)
        detailed_infos = [{'day_date': x[0].replace('.', '-'), \
                           'week_date': x[1], \
                           'time_date': x[2], \
                           'place_url': x[3], \
                           'province': x[4], \
                           'place': x[5], \
                           'total_price': x[6]} for x in regex_res]
        in_sale_prices_regex = self.get_regex_pattern('in_sale_prices_regex',
                r'<span>(.*?)</span>')
        sold_out_prices_regex = self.get_regex_pattern('sold_out_prices_regex',
                r'<span class="ys">(.*?)</span>')
        for i, info in enumerate(detailed_infos):
            detailed_infos[i]['in_sale_prices'] = \
                    [float(x) for x in in_sale_prices_regex.findall(info['total_price'])]
            detailed_infos[i]['sold_out_prices'] = \
                    [float(x) for x in sold_out_prices_regex.findall(info['total_price'])]
            detailed_infos[i].pop('total_price')
        return detailed_infos

class BeihangSunriseConcertHall(WebSpider):
    source = 'BeihangSunriseConcertHall'
    def __init__(self):
        super(BeihangSunriseConcertHall, self).__init__()
        self._home_url = 'https://www.forqian.cn'
    def _get_rough_url_list(self):
        return [self._home_url]
    def _parse_for_rough_info(self, text):
        rough_info_regex = self.get_regex_pattern('rough_info_regex',
                r'<div class="col-xs-4">.*?<a href="(?P<url>.*?)">.*?<p class='
                r'"text-nowrap title-performance">(?P<name>.*?)</p>', flag=re.DOTALL)
        regex_res = rough_info_regex.findall(text)
        infos = [{'url': self._home_url + x[0], 'name': x[1].strip()} for x in regex_res]
        return infos
    def _parse_for_detailed_info(self, text):
        detailed_info_regex = self.get_regex_pattern('detailed_info_regex',
                r'【演出时间】(?P<day_date>\d*?年\d*?月\d*)日(?P<time_date>\d*?:\d*).*?'
                r'【网上售票时间】(?P<reminder_time>\d*?年\d*?月\d*)日.*?【演出地点】'
                r'(?P<place>.*?)</span>.*?【票价】(?P<total_price>.*?)</span>', flag=re.DOTALL)
        regex_res = detailed_info_regex.findall(text)
        detailed_infos = [{'day_date': x[0].replace('年', '-').replace('月', '-'), \
                           'time_date': x[1], \
                           'reminder_time': x[2].replace('年', '-').replace('月', '-'), \
                           'place': x[3], \
                           'total_price': x[4], \
                           'province': '北京'} for x in regex_res]
        in_sale_prices_regex = self.get_regex_pattern('in_sale_prices_regex', r'(\d*?)[/元]')
        for i, info in enumerate(detailed_infos):
            detailed_infos[i]['in_sale_prices'] = \
                    [float(x) for x in in_sale_prices_regex.findall(info['total_price'])]
            detailed_infos[i]['sold_out_prices'] = []
            detailed_infos[i].pop('total_price')
        return detailed_infos
