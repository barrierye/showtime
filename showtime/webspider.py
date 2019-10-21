#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import re
import sys
import html
import requests
import multiprocessing
from showtime.show import Show

class WebSpider(object):
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
    def _get_and_parse_for_rough_info_warpper(self, url):
        return self._parse_html_for_rough_info(self._get_url_content_for_rough_info(url))
    def _get_rough_show_infos(self, is_parallel=True, process_num=None):
        ''' 获取演出的简略信息 '''
        urls = self._get_rough_info_url_list()
        rough_show_infos = []
        process_num = self._get_process_num(is_parallel, process_num, len(urls))
        if process_num == 1:
            for url in urls:
                rough_show_infos += self._parse_html_for_rough_info(self._get_url_content_for_rough_info(url))
        else:
            pool = multiprocessing.Pool(processes=process_num)
            pool_outputs = pool.map(self._get_and_parse_for_rough_info_warpper, urls)
            pool.close()
            pool.join()
            for res in pool_outputs:
                rough_show_infos += list(res)
        return rough_show_infos
    def _get_and_parse_for_detailed_info_warpper(self, url):
        return self._parse_html_for_detailed_info(self._get_url_content_for_detailed_info(url))
    def get_shows(self, is_parallel=True, process_num=None):
        rough_show_infos = self._get_rough_show_infos(is_parallel, process_num)
        shows = [Show(info) for info in rough_show_infos]
        process_num = self._get_process_num(is_parallel, process_num, len(shows))
        if process_num == 1:
            for i, show in enumerate(shows):
                shows[i].add_events(self._parse_html_for_detailed_info(self._get_url_content_for_detailed_info(show.url)))
        else:
            urls = [show.url for show in shows]
            pool = multiprocessing.Pool(processes=process_num)
            pool_outputs = pool.map(self._get_and_parse_for_detailed_info_warpper, urls)
            pool.close()
            pool.join()
            for i, show in enumerate(shows):
                shows[i].add_events(pool_outputs[i])
        return shows

class ChinaTicket(WebSpider):
    def __init__(self):
        super(ChinaTicket, self).__init__()   
        self.source_url = 'https://www.chinaticket.com'
    def _get_rough_info_url_list(self):
        show = 'wenyi' # only for art-shows
        url = '%s/%s'%(self.source_url, show)
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
        detailed_infos = [{'day_date': x[0], \
                           'week_date': x[1], \
                           'time_date': x[2], \
                           'url': x[3], \
                           'province': x[4], \
                           'place': x[5], \
                           'total_price': x[6]} for x in regex_res]
        in_sale_price_regex = self.get_regex_pattern('in_sale_price_regex', r'<span>(.*?)</span>')
        sold_out_price_regex = self.get_regex_pattern('sold_out_price_regex', r'<span class="ys">(.*?)</span>')
        for i, info in enumerate(detailed_infos):
            detailed_infos[i]['in_sale_price'] = in_sale_price_regex.findall(info['total_price'])
            detailed_infos[i]['sold_out_price'] = sold_out_price_regex.findall(info['total_price'])
            detailed_infos[i].pop('total_price')
        return detailed_infos

class BeiHangSunriseConcertHall(WebSpider):
    def __init__(self):
        super(BeiHangSunriseConcertHall, self).__init__()
        self.source_url = 'https://www.forqian.cn'
    def _get_rough_info_url_list(self):
        return [self.source_url]
    def _parse_html_for_rough_info(self, text):
        rough_info_regex = self.get_regex_pattern('rough_info_regex', r'<div class="col-xs-4">.*?<a href="(?P<url>.*?)">.*?<p class="text-nowrap title-performance">(?P<name>.*?)</p>', flag=re.DOTALL)
        regex_res = rough_info_regex.findall(text)
        infos = [{'url': self.source_url + x[0], 'name': x[1].strip()} for x in regex_res]
        return infos
    def _parse_html_for_detailed_info(self, text):
        detailed_info_regex = self.get_regex_pattern('detailed_info_regex', r'【演出时间】(?P<day_date>\d*?年\d*?月\d*日)(?P<time_date>\d*?:\d*).*?【网上售票时间】(?P<reminder_time>\d*?年\d*?月\d*日).*?【演出地点】(?P<place>.*?)</span>.*?【票价】(?P<total_price>.*?)</span>', flag=re.DOTALL)
        regex_res = detailed_info_regex.findall(text)
        detailed_infos = [{'day_date': x[0], \
                           'time_date': x[1], \
                           'reminder_time': x[2], \
                           'place': x[3], \
                           'total_price': x[4], \
                           'province': '北京'} for x in regex_res]
        in_sale_price_regex = self.get_regex_pattern('in_sale_price_regex', r'(\d*?)[/元]')
        for i, info in enumerate(detailed_infos):
            detailed_infos[i]['in_sale_price'] = in_sale_price_regex.findall(info['total_price'])
            detailed_infos[i]['sold_out_price'] = []
            detailed_infos[i].pop('total_price')
        return detailed_infos
