# showtime

用于爬取各种演出（话剧、音乐会、演唱会等）信息的爬虫。

信息来源：

- [x] 中票在线 [https://www.chinaticket.com](https://www.chinaticket.com/)

- [x] 北航晨兴音乐厅 [https://www.forqian.cn](https://www.forqian.cn/)

- [ ] 中国电影资料馆 [https://www.cfa.org.cn](https://www.cfa.org.cn/)

- [ ] 蜂巢剧场官网 [http://www.fengchaojuchang.org.cn](http://www.fengchaojuchang.org.cn/)

- [ ] 孟京辉官网 [http://www.mengjinghui.com.cn](http://www.mengjinghui.com.cn/)

- [ ] 大麦 [APP]

- [ ] 秀动 [APP]

- [ ] 摩天轮 [APP]

- [ ] 音乐节RSS [小程序]

## Requirements

- Python 3
- pip
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
        # 爬取show信息，默认多进程并且开cpu_num个进程，可以自行指定
        shows = spider.get_shows(is_parallel=False)
        for show in shows:
            # 打印show的简略信息
            print(show)
```

## TODO

- 支持待支持的信息来源