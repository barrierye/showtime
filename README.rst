showtime
========

|Python version| |release| |PyPI|

用于爬取各种演出（话剧、音乐会、演唱会等）信息的爬虫，\ **生活需要一点情调**\ 。

Feature
-------

-  支持多种信息来源，支持列表：

   -  ☒ 中票在线
      `https://www.chinaticket.com <https://www.chinaticket.com/>`__
   -  ☒ 北航晨兴音乐厅
      `https://www.forqian.cn <https://www.forqian.cn/>`__
   -  ☐ 永乐票务 `https://www.228.com.cn <https://www.228.com.cn/>`__
   -  ☒ 北京大学百周年纪念讲堂
      `www.pku-hall.com <http://www.pku-hall.com>`__
   -  ☒ 孟京辉官网
      `http://www.mengjinghui.com.cn <http://www.mengjinghui.com.cn/>`__
   -  ☐ 大麦 [APP]
   -  ☐ 音乐节RSS [小程序]

-  支持单机并行

   spider间多进程并行，spider内粗粒度多线程并行。一些特殊spider内（如\ ``MengJingHuiWebsite``\ ）细粒度协程并行。

-  支持简单的本地存储/加载功能

   为了使得数据清晰简单，采用protobuf支持human-friendly/序列化存储，数据格式：

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

直接安装（如果你更换了pip源，可能需要加上\ ``-i https://pypi.python.org/simple``\ 参数）

.. code:: bash

   pip install show-time

源码安装

.. code:: bash

   pip install wheel
   python setup.py bdist_wheel
   pip install dist/show-time-0.0.3-py3-none-any.whl

Usage
-----

.. code:: python

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

       for show_list in total_show_list:
           # 打印show_list的简略信息
           print_info(show_list, rough=True)
           # 将结果存储到本地
           show_list.save('%s.data' % show_list.source)

Contribution
------------

如果支持信息来源列表中没有你需要的，你可以根据下面的文档进行拓展开发，并提交PR贡献代码。

WebSpider
~~~~~~~~~

|image3|

信息来源为Web的爬虫类需要继承WebSpider基类，WebSpider提供了一些默认方法和并行支持。

WebSpider是这样工作的： 1.
通过\ ``_get_rough_url_list``\ 方法获取简略的url列表\ ``rough_url_list``\ ，从这些url中可以得到每场演出的名称和具体信息的url。

2. 遍历\ ``rough_url_list``\ 中的url，通过\ ``_get_rough_page``\ 方法获取这些url对应的内容\ ``rough_page``\ 。

   ``_get_rough_page``\ 方法默认实现是GET，如果页面需要登陆等操作则需要重写该方法。

3. 使用\ ``_parse_for_rough_info``\ 方法对每个\ ``rough_page``\ 进行解析，得到每场演出的名称和具体信息的url的列表\ ``detailed_url_list``\ 。

4. 遍历\ ``detailed_url_list``\ 中的url，使用\ ``_get_detailed_page``\ 方法获取对应的内容\ ``detailed_page``\ 。

   ``_get_detailed_page``\ 方法默认实现是GET，如果页面需要登陆等操作则需要重写该方法。

5. 使用\ ``_parse_for_detailed_info``\ 方法对每个\ ``detailed_page``\ 进行解析，得到每场演出的具体信息。

添加一个无需登录等操作的webspider，你至少需要： -
重写类变量source（资源来源），这是webspider在工厂类中自动注册的凭证 -
重写方法\ ``_get_rough_url_list`` - 重写方法\ ``_parse_for_rough_info``
- 重写方法\ ``_parse_for_detailed_info``

AppSpider
~~~~~~~~~

TODO

AppletSpider
~~~~~~~~~~~~

TODO

Bug
---

如果在使用过程中遇到问题，欢迎在issue中描述问题复现过程。

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
.. |image3| image:: https://tva1.sinaimg.cn/large/006y8mN6gy1g87bdn9ix7j30lp0gwjre.jpg

