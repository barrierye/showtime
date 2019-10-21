#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
from showtime import webspider

class ShowSpiderFactory(object):
    def __new__(self, *args, **kwargs):
        if not hasattr(self, '_instance'):
            self._instance = super(ShowSpiderFactory, self).__new__(self, *args, **kwargs)
        return self._instance

    def __init__(self):
        self._spider_type = ['web']
        self._web_spiders = {'https://www.chinaticket.com': webspider.ChinaTicket(),
                             'https://www.forqian.cn': webspider.BeihangSunriseConcertHall(),}
       
        self._spiders = None
        for t in self._spider_type:
            s = getattr(self, '_%s_spiders' % t)
            if self._spiders is None:
                self._spiders = s.copy()
            else:
                self._spiders.update(s)

    def support_sources(self):
        return [s for s in self._spiders]

    def get_spider(self, source):
        return self._spiders.get(source)
