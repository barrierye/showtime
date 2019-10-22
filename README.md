

# showtime

用于爬取各种演出（话剧、音乐会、演唱会等）信息的爬虫。

## Feature

- 支持多种信息来源，支持列表：
  - [x] 中票在线 [https://www.chinaticket.com](https://www.chinaticket.com/)
  - [x] 北航晨兴音乐厅 [https://www.forqian.cn](https://www.forqian.cn/)
  - [ ] 中国电影资料馆 [https://www.cfa.org.cn](https://www.cfa.org.cn/)
  - [ ] 蜂巢剧场官网 [http://www.fengchaojuchang.org.cn](http://www.fengchaojuchang.org.cn/)
  - [ ] 孟京辉官网 [http://www.mengjinghui.com.cn](http://www.mengjinghui.com.cn/)
  - [ ] 大麦 [APP]
  - [ ] 音乐节RSS [小程序]
- 支持单机多进程运行

## TODO

- 支持简单的本地存储/加载功能（可能使用protobuf）
- 支持未支持的信息来源
- 支持北航晨兴音乐厅的线上预定

## Requirements

- Python3.4+
- wheel

## Installation

```bash
python setup.py bdist_wheel
pip install dist/showtime-0.0.0-py3-none-any.whl
```

## Usage

```python
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
        # 爬取show信息，默认多进程并且开cpu_num个进程，可以自行指定进程数
        show_list = spider.get_show_list(is_parallel=False)
        for show in show_list:
            # 打印show的简略信息
            print(show)
```

## Contribute code

如果支持信息来源列表中没有你需要的，你可以帮忙编写贡献代码。

### WebSpider

![](https://tva1.sinaimg.cn/large/006y8mN6gy1g87bdn9ix7j30lp0gwjre.jpg)

信息来源为Web的爬虫类需要继承WebSpider父类，WebSpider提供了一些默认方法和多进程支持。

WebSpider是这样工作的：
1. 通过`_get_rough_url_list`方法获取简略的url列表`rough_info_url_list`，从这些url中可以得到每场演出的名称和具体信息的url。
2. 遍历`rough_info_url_list`中的url，通过`_get_rough_page`方法获取这些url对应的内容`rough_page`。`_get_rough_page`方法默认实现是GET。
3. 使用`_parse_for_rough_info`方法对每个`rough_page`进行解析，得到每场演出的名称和具体信息的url。
4. 对于每场演出具体信息的url，使用`_get_detailed_page`方法获取对应的内容`detailed_page`。`_get_detailed_page`方法默认实现是GET。
5. 使用`_parse_for_detailed_info`方法对每个`detailed_page`进行解析，得到每场演出的具体信息。

你至少需要：
- 重写类变量source，这是webspider在工厂类中自动注册的凭证
- 重写方法`_get_rough_url_list`
- 重写方法`_parse_for_rough_info`
- 重写方法`_parse_for_detailed_info`

### AppSpider

TODO

### WechatProgramSpider

TODO



