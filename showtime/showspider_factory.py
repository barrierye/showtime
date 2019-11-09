#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import sys
import logging
import inspect
import multiprocessing

from showtime import webspider
from showtime import utils

_LOGGER = logging.getLogger(__name__)

class ShowSpiderFactory(object):
    def __new__(self, *args, **kwargs):
        if not hasattr(self, '_instance'):
            self._instance = super(ShowSpiderFactory, self).__new__(self, *args, **kwargs)
            
            self._spider_types = ['webspider']
            self._spiders = {}
            for spider_type in self._spider_types:
                specific_spiders = {}
                for name, obj in inspect.getmembers(sys.modules['showtime.%s'%spider_type]):
                    # get all class in module 'showtime.%s'%spider_type
                    if inspect.isclass(obj):
                        if obj.source is not None:
                            specific_spiders[obj.source] = obj()
                # Shallow copy may causing problems if value in `specific_spiders` be modified
                setattr(self, '_%ss'%spider_type, specific_spiders)
                self._spiders.update(specific_spiders)

        return self._instance

    def support_sources(self):
        return [s for s in self._spiders]

    def get_spider(self, source):
        return self._spiders.get(source)
    
    def get_show_list(self, source, is_parallel=True, thread_num=None):
        timer = utils.TimeRecorder()
        showlist = self.get_spider(source).get_show_list(is_parallel, thread_num)
        timer.release()
        #  _LOGGER.info('[%s] time without sleep: %f', source, timer.count_without_sleep())
        _LOGGER.info('[%s] time: %f', source, timer.count())
        return showlist

    def get_total_show_list(self, source_list, is_parallel=True, process_num=None):
        timer = utils.TimeRecorder()

        pnum = utils.get_process_num(is_parallel, process_num, len(source_list))
        if pnum == 1:
            total_show_list = [self.get_show_list(source, is_parallel=is_parallel) for source in source_list]
        else:
            pool = multiprocessing.Pool(processes=pnum)
            total_show_list = pool.map(self.get_show_list, source_list)
            pool.close()
    
        timer.release()
        #  _LOGGER.info('total time without sleep: %f', timer.count_without_sleep())
        _LOGGER.info('total time: %f', timer.count())
        return total_show_list
