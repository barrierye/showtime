#-*- coding:utf8 -*-
# Copyright (c) 2019 barriery
# Python release: 3.7.0
from showtime.showspider import ChinaTicket

if __name__ == '__main__':
    s = ChinaTicket()
    shows = s.get_detailed_show_infos()
    for show in shows:
        print(show)
        print('===================================================')
