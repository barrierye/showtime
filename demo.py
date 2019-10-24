#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import showtime
from showtime.showspider_factory import ShowSpiderFactory

def print_info(show_list, rough=True):
    for show in show_list:
        print(show)
        if rough:
            continue
        for e in show:
            print(e)

def load_file(filename):
    return showtime.show_type.ShowList.load(filename)

if __name__ == '__main__':
    # 获取showspider的工厂实例
    spider_factory = ShowSpiderFactory()

    # 获取目前已经支持的资源列表
    support_sources = spider_factory.support_sources()

    # 多进程获取所有资源对应spider的show_list，同时在每个spider内部开线程池
    total_show_list = spider_factory.get_total_show_list(support_sources, is_parallel=True)

    # 打印show_list的简略信息
    for show_list in total_show_list:
        print_info(show_list, rough=True)
        # 将结果存储到本地
        show_list.save('%s.data' % show_list.source)
