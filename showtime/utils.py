#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import re
import time
import asyncio
import aiohttp
import datetime
import multiprocessing

async def async_get_page_by_GET(url, index, page_lsit):
    async with aiohttp.ClientSession() as session:
        async with session.request('GET', url) as resp:
            page = await resp.text()
            page_lsit.append((index, page))

def async_get_pages_by_GET(urls):
    page_lsit = []
    # see: https://stackoverflow.com/questions/46727787/runtimeerror-there-is-no-current-event-loop-in-thread-in-async-apscheduler
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [async_get_page_by_GET(url, index, page_lsit) \
                for index, url in enumerate(urls)]
    loop.run_until_complete(asyncio.wait(tasks))
    page_lsit.sort(key=lambda e: e[0])
    return [page for index, page in page_lsit]

def judge_this_year(month, day):
    current_year = datetime.datetime.now().strftime('%Y')
    current_date = time.mktime(time.strptime(get_current_date().__str__(), '%Y-%m-%d'))
    give_date = time.mktime(time.strptime('%s-%s-%s'%(current_year, month, day), '%Y-%m-%d'))
    if current_date <= give_date:
        return current_year
    return (get_current_date()+datetime.timedelta(days=365)).strftime('%Y')
 
def get_current_date():
    return datetime.date.today()

def padding_dict(src, dist, requested_params):
    for param in requested_params:
        if param in src and param not in dist:
            dist[param] = src.get(param)

def get_process_num(is_parallel, process_num, item_num):
    if process_num is None:
        if is_parallel:
            process_num = multiprocessing.cpu_count()
        else:
            process_num = 1
    if process_num > item_num:
        process_num = item_num
    if process_num <= 0:
        process_num = 1
    return process_num

def is_url_begin_with_http(url):
    http_regex = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.'
                            r'[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$')
    return http_regex.match(url) is not None
