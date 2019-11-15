showtime
========

|Python version| |release| |PyPI|

Life is generally simple and boring for science and engineering students
who keep running between dormitory, laboratory and teaching building. In
order to add some **cultural presence** on the life, showtime is
designed, which is a tool based on network spider technology to crawl
information for numerous shows such as dramas and concerts.

Feature
-------

-  Support multiple types of information sources

   1. website source:

      -  ☒ `China Ticket <https://www.chinaticket.com/>`__

      -  ☒ `Beihang Sunrise Concert Hall <https://www.forqian.cn/>`__

      -  ☐ `永乐票务 <https://www.228.com.cn/>`__

      -  ☒ `PKU Hall <http://www.pku-hall.com>`__

      -  ☒ `MengJingHui website <http://www.mengjinghui.com.cn/>`__

      -  ☐
         `北京国际青年戏剧节 <http://www.mengjinghui.com.cn/qxj.html?from=singlemessage&isappinstalled=0>`__

   2. APP source:

   -  ☐ 大麦

   3. applet source:

      -  ☐ 音乐节RSS

-  Stand-alone parallel support

   When the program is executing, several processes will be launched.
   Each process processes one data source, and at the same time use of
   multiple threads to handle multiple requests in a process. For some
   exceptional sources(such as ``MengJingHuiWebsite``), more
   fine-grained coroutines is implemented.

-  Simple local storage and loading capabilities by using protobuf

   .. code:: protobuf

      syntax = "proto3";

      message ShowList {
        string source = 1;
        repeated Show shows = 2;
      }

      message Show {
        string name = 1;
        string url = 2;
        repeated Event events = 3;
        map<string, string> extra_fields = 4;
      }

      message Event {
        string date = 1; // YYYY-mm-dd
        string time = 2; // HH:MM
        string url = 3; // http-url or https-url
        string city = 4; // 34个省级行政区域以及一线，新一线和二线城市，不带'省'和'市'等后缀，2-3个字
        string address = 5;
        Price prices = 6;
        map<string, string> extra_fields = 7;
      }

      message Price {
        repeated float in_sale = 1;
        repeated float sold_out = 2;
      }

Requirements
------------

Python3.5+

Installation
------------

-  Install with pip

   .. code:: bash

      pip install show-time

-  Install from source

   .. code:: bash

      pip install wheel
      python setup.py bdist_wheel
      pip install dist/show-time-0.0.4-py3-none-any.whl

Usage
-----

.. code:: python

   import os
   import logging
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
       logging.basicConfig(level=logging.INFO)

       data_path = 'data'
       if not os.path.exists(data_path):
           os.makedirs(data_path)

       # 获取showspider的工厂实例
       spider_factory = ShowSpiderFactory()

       # 获取目前已经支持的资源列表
       support_sources = spider_factory.support_sources()

       # 多进程获取所有资源对应spider的show_list，同时在每个spider内部开线程池
       total_show_list = spider_factory.get_total_show_list(support_sources, is_parallel=True)

       for show_list in total_show_list:
           # 将结果存储到本地
           show_list.save('%s/%s.data' % (data_path, show_list.source))

Issue
-----

If you encounter problems, please describe the problem recurrence
process in issue.

TODO
----

1. 为了项目的可持续发展，需要尽快完善注释和文档（资源种类太多，且每种资源的一些设定还是异构的）。
2. 支持尚未支持的Web信息来源
3. 频繁爬取数据，服务器拒绝访问&&偶尔会崩
4. 思考AppSpider的基类架构
5. 思考AppletSpider的基类架构
6. 支持北航晨兴音乐厅的线上预定

.. |Python version| image:: https://img.shields.io/badge/Python-3.5+-brightgreen.svg
   :target: https://github.com/barrierye/showtime#requirements
.. |release| image:: https://img.shields.io/github/v/tag/barrierye/showtime?label=release
   :target: https://github.com/barrierye/showtime/releases
.. |PyPI| image:: https://img.shields.io/pypi/v/show-time
   :target: https://pypi.org/project/show-time/#files
