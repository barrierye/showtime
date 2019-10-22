#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import showtime
from showtime.showspider_factory import ShowSpiderFactory

def print_info(show_list, rough=True):
    for show in show_list:
        print(show)
        if not rough:
            for e in show:
                print(e)

if __name__ == '__main__':
    # 获取showspider的工厂实例
    spider_factory = ShowSpiderFactory()
    # 获取目前已经支持的资源列表
    support_sources = spider_factory.support_sources()
    # 获取资源对应的spider实例
    spider = spider_factory.get_spider(support_sources[0])
    # 爬取show信息，默认多进程并且开cpu_num个进程，可以自行指定进程数
    #  show_list = spider.get_show_list(is_parallel=False)
    show_list = spider.get_show_list()
    # 打印show_list的简略信息
    print_info(show_list, rough=True)
    # 将结果存储到本地
    show_list.save('show_list.data')
    # 从本地文件加载show_list
    #  show_list = showtime.show_type.ShowList.load('show_list.data')
