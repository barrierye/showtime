#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
from showtime.showspider_factory import ShowSpiderFactory

if __name__ == '__main__':
    spider_factory = ShowSpiderFactory()
    support_sources = spider_factory.support_sources()
    for source in support_sources:
        spider = spider_factory.get_spider(source)
        shows = spider.get_shows()
        for show in shows:
            print(show)
