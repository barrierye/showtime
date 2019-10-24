#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import re
import sys
import html
import json
import asyncio
import aiohttp
import requests
import multiprocessing
import multiprocessing.dummy
from urllib.parse import urlencode

# Do not import Show class and ShowList class directly,
# in case the factory class incorrectly registers the
# webspider classes.
from showtime import show_type
from showtime import utils

class WebSpider(object):
    # # PAY ATTITION THAT `source` need be rewrite
    source = None
    def __init__(self):
        self._session = requests.Session()
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
    def get_page_by_GET(self, url, browser_type='Chrome'):
        return self._session.get(url, headers=self._get_default_header(browser_type)).content.decode('utf-8')
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
    def _warpper_for_get_and_parse_for_rough_info(self, url):
        return self._parse_for_rough_info(self._get_rough_page(url))
    def _warpper_for_get_and_parse_for_detailed_info(self, url):
        return self._parse_for_detailed_info(self._get_detailed_page(url))
    def get_show_list(self, is_parallel=True, thread_num=None):
        showlist = show_type.ShowList(self.source)
        urls = self._get_rough_url_list()

        # get rough infos
        tnum = utils.get_process_num(is_parallel, thread_num, len(urls))
        rough_show_infos = []
        if tnum == 1:
            for url in urls:
                rough_show_infos += self._parse_for_rough_info(self._get_rough_page(url))
        else:
            pool = multiprocessing.dummy.Pool(processes=tnum)
            for infos in pool.map(self._warpper_for_get_and_parse_for_rough_info, urls):
                rough_show_infos += list(infos)
            pool.close()
        showlist.add_shows([show_type.Show(info) for info in rough_show_infos])

        # get detailed infos
        tnum = utils.get_process_num(is_parallel, thread_num, len(showlist))
        need_be_del = []
        if tnum == 1:
            for i, show in enumerate(showlist):
                infos = self._parse_for_detailed_info(self._get_detailed_page(show.url))
                if not infos:
                    need_be_del.append(i)
                    continue
                for j, info in enumerate(infos):
                    if info.get('url') is None:
                        infos[j]['url'] = showlist[i].url
                    utils.padding_dict(showlist[i].extra_fields, infos[j],
                            ['date', 'time', 'city', 'address', 'in_sale_prices', 'sold_out_prices'])
                showlist[i].add_events(infos)
        else:
            pool = multiprocessing.dummy.Pool(processes=tnum)
            urls = [show.url for show in showlist]
            infos_list = pool.map(self._warpper_for_get_and_parse_for_detailed_info, urls)
            pool.close()
            for i, show in enumerate(showlist):
                if not infos_list[i]:
                    need_be_del.append(i)
                    continue
                for j, infos in enumerate(infos_list[i]):
                    if infos.get('url') is None:
                        infos_list[i][j]['url'] = show.url
                    utils.padding_dict(show.extra_fields, infos_list[i][j],
                            ['date', 'time', 'city', 'address', 'in_sale_prices', 'sold_out_prices'])
                showlist[i].add_events(infos_list[i])
        del_cnt = 0
        for index in need_be_del:
            del showlist[index - del_cnt]
            del_cnt += 1
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
        whole_s_ticket_list_page_regex = re.compile(
                r'<div class="s_ticket_list_page">(.*?)</div>', re.DOTALL)
        whole_s_ticket_list_page = whole_s_ticket_list_page_regex.findall(text)[0]
        s_ticket_list_page_regex = re.compile(r'<a href="(?P<url>.*?)">\d*</a>')
        # 这里需要url解码，否则访问失败
        # see: https://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1
        urls = [html.unescape(x) \
                for x in s_ticket_list_page_regex.findall(whole_s_ticket_list_page)]
        return [url] + urls
    def _parse_for_rough_info(self, text):
        rough_info_regex = re.compile(r'<img src="(?P<image>.*?)".*?/>\s*<a '
                                      r'href="(?P<url>.*?)".*?>(?P<name>.*?)</a>')
        regex_res = rough_info_regex.findall(text)
        infos = [{'image': x[0],
                  'url': x[1].strip(),
                  'name': x[2].strip()} for x in regex_res]
        return infos
    def _parse_for_detailed_info(self, text):
        detailed_info_regex = re.compile(
                r'<li class="f_lb_list_shijian">\s*?(?P<date>\d*\.\d*\.\d*).*?<span '
                r'class="f14">(?P<week_date>.*?)</span> (?P<time>\d*:\d*).*?<a href="'
                r'(?P<address_url>.*?)">.*?\[(?P<city>.*?)\]</span><br />  (?P<address>.*?)'
                r'</a></li>.*?(?P<total_price><span.*?>.*?</span>)\s*?</li>', re.DOTALL)
        regex_res = detailed_info_regex.findall(text)
        detailed_infos = [{'date': x[0].replace('.', '-'), \
                           'week_date': x[1], \
                           'time': x[2], \
                           'address_url': x[3], \
                           'city': x[4], \
                           'address': x[5], \
                           'total_price': x[6]} for x in regex_res]
        in_sale_prices_regex = re.compile(r'<span>(.*?)</span>')
        sold_out_prices_regex = re.compile(r'<span class="ys">(.*?)</span>')
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
        rough_info_regex = re.compile(
                r'<div class="col-xs-4">.*?<a href="(?P<url>.*?)">.*?<p class='
                r'"text-nowrap title-performance">(?P<name>.*?)</p>', re.DOTALL)
        regex_res = rough_info_regex.findall(text)
        infos = [{'url': self._home_url + x[0], 'name': x[1].strip()} for x in regex_res]
        return infos
    def _parse_for_detailed_info(self, text):
        detailed_info_regex = re.compile(
                r'【演出时间】(?P<date>\d*?年\d*?月\d*)日(?P<time>\d*?:\d*).*?'
                r'【网上售票时间】(?P<reminder_time>\d*?年\d*?月\d*)日.*?【演出地点】'
                r'(?P<address>.*?)</span>.*?【票价】(?P<total_price>.*?)</span>', re.DOTALL)
        regex_res = detailed_info_regex.findall(text)
        detailed_infos = [{'date': x[0].replace('年', '-').replace('月', '-'), \
                           'time': x[1], \
                           'reminder_time': x[2].replace('年', '-').replace('月', '-'), \
                           'address': x[3], \
                           'total_price': x[4], \
                           'city': '北京'} for x in regex_res]
        in_sale_prices_regex = re.compile(r'(\d*?)[/元]')
        for i, info in enumerate(detailed_infos):
            detailed_infos[i]['in_sale_prices'] = \
                    [float(x) for x in in_sale_prices_regex.findall(info['total_price'])]
            detailed_infos[i]['sold_out_prices'] = []
            detailed_infos[i].pop('total_price')
        return detailed_infos

class MengJingHui(WebSpider):
    source = 'MengJingHuiWebsite'
    def __init__(self):
        super(MengJingHui, self).__init__()
        self._home_url = 'http://www.mengjinghui.com.cn'
    def _get_rough_url_list(self):
        return ['http://www.wanshe.cn/rest/vc/event_list_all']
    def _get_rough_page(self, url):
        params = {'user_id': '181'}
        response = self._session.get(url, headers=self._get_default_header(), params=params)
        play_list_json_obj = response.json()[0]['list']
        return json.dumps(play_list_json_obj)
    def _parse_for_rough_info(self, text):
        play_list = json.loads(text)
        params_mapping = {'address': 'address',
                          'cityName': None,
                          'create_time': None,
                          'date': None,
                          'detail': None,
                          'event_logo': 'image',
                          'is_mailing': None,
                          'is_seat': None,
                          'price': None,
                          'provinceName': 'city',
                          'source': None,
                          'title': 'name',
                          'topicName': None,
                          'url': 'url'}
        rough_infos = []
        for play in play_list:
            rough_infos.append({v: play[k] for k, v in params_mapping.items() if v is not None})
        return rough_infos
    def __various_get_urls_and_events(self, href, url_type, text, eid):
        if url_type == '已售罄':
            return None
        elif url_type == '选座购票':
            page_aid_regex = re.compile(r'<li aid="(?P<erid>\d*?)".*?>'
                                        r'(?P<date>\d{1,2}-\d{1,2}).*?(?P<time>\d{1,2}:\d{2})</li>')
            regex_res = page_aid_regex.findall(text)
            events = [{'erid': x[0],
                       'date': '%s-%s'%(utils.judge_this_year(x[1].split('-')[0], x[1].split('-')[1]), x[1]),
                       'time': x[2]} for x in regex_res]
            base_url = 'http://www.wanshe.cn/orders/querySeatMap'
            urls = [base_url + '?' + urlencode({'eid': eid,
                                                'erid': event['erid'],
                                                'tzid': 0}) for event in events]
        elif url_type == '直接购票':
            # http://www.wanshe.cn/orders/buy?eid=30940&ufid=0
            url = 'http://www.wanshe.cn' + href
            print('[TODO] 直接购票: ', url)
            return None
            #TODO
        else:
            raise Exception('unknow url type<%s>' % url_type)
        return [urls, events]
    def __various_get_prices(self, url_type, page):
        if url_type == '选座购票':
            try:
                seat_info_list = json.loads(page)
            except Exception as e:
                print('[TODO] 暂时不支持该种选座页面')
                return None
            in_sale = set()
            total = set()
            for seat_info in seat_info_list:
                fare = seat_info['fare']
                status = seat_info['status']
                if status == 0:
                    in_sale.add(fare)
                total.add(fare)
            in_sale_prices = [float(x) for x in list(in_sale)]
            sold_out_prices = [float(x) for x in list(total - in_sale)]
        elif url_type == '直接购票':
            return None
            #TODO
        else:
            raise Exception('unknow url type<%s>' % url_type)
        return [in_sale_prices, sold_out_prices]
    def _get_detailed_page(self, url):
        # 由于网站比较特殊，故在这里完成get和parse，并返回一个json_str
        eid = url.split('/')[-1]

        text = self.get_page_by_GET(url)
        url_type_regex = re.compile(r'<li>不同场次以现有价格为准.*?<a href="(?P<href>.*?)">'
                                    r'(?P<url_type>.*?)</a>.*?<div class="tgbg">', re.DOTALL)
        href, url_type = url_type_regex.findall(text)[0]
        urls_and_events = self.__various_get_urls_and_events(href, url_type, text, eid)
        if urls_and_events is None:
            return None
        urls, events = urls_and_events

        page_lsit = []
        # see: https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [utils.async_get_page_by_GET(url, index, page_lsit) \
                for index, url in enumerate(urls)]
        loop.run_until_complete(asyncio.wait(tasks))
        page_lsit.sort(key=lambda e: e[0])
        
        detailed_infos = []
        for i, event in enumerate(events):
            date = event['date']
            time = event['time']
            page = page_lsit[i][1]
            prices = self.__various_get_prices(url_type, page)
            if not prices:
                return None
            [in_sale_prices, sold_out_prices] = prices
            detailed_infos.append({'date': date,
                                   'time': time,
                                   'in_sale_prices': in_sale_prices,
                                   'sold_out_prices': sold_out_prices})
        return json.dumps(detailed_infos)
    def _parse_for_detailed_info(self, text):
        if text is None:
            return None
        return json.loads(text)
