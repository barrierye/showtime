# showtime

用于爬取各种演出（话剧、音乐会、演唱会等）信息的爬虫。

目前支持网站/APP/小程序：

- 中票在线 [https://www.chinaticket.com](https://www.chinaticket.com/)

待支持网站/APP/小程序：

- 北航晨兴音乐厅 [https://www.forqian.cn](https://www.forqian.cn/)
- 中国电影资料馆 [https://www.cfa.org.cn](https://www.cfa.org.cn/)
- 蜂巢剧场官网 [http://www.fengchaojuchang.org.cn](http://www.fengchaojuchang.org.cn/)
- 孟京辉官网 [http://www.mengjinghui.com.cn](http://www.mengjinghui.com.cn/)
- 大麦 [APP]
- 秀动 [APP]
- 摩天轮 [APP]
- 音乐节RSS [小程序]

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
    spider_factory = ShowSpiderFactory()
    support_sources = spider_factory.support_sources()
    for source in support_sources:
        spider = spider_factory.get_spider(source)
        shows = spider.get_shows()
        for show in shows:
            print(show)
```

## TODO

- 多进程支持
- 待支持网站/APP/小程序