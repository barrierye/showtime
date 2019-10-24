#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
import re
import multiprocessing

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
