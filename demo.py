#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
from showtime.showspider_factory import ShowSpiderFactory

if __name__ == '__main__':
    # 获取showspider的工厂实例
    spider_factory = ShowSpiderFactory()
    # 获取目前已经支持的资源列表
    support_sources = spider_factory.support_sources()
    for source in support_sources:
        print('[process]: %s' % source)
        # 获取每个资源对应的spider实例
        spider = spider_factory.get_spider(source)
        # 爬取show信息，默认多进程并且开cpu_num个进程，可以自行指定
        shows = spider.get_shows(is_parallel=False)
        for show in shows:
            # 打印show的简略信息
            print(show)
