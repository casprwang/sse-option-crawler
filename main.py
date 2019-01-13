#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Song Wang"
__email__ = "wangsongiam@gmail.com"

# expireDate
# http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay?date=201706
# FRONTROW = [
#     'Date', 'ExpireDate', 'OptionType', 'Strike', 'Contract Name', 'Last',
#     'Bid', 'Ask', 'Change', '%Change', 'Volume', 'OpenInterest',
#     'ImpliedVolatility', 'UnderlyingPrice'
# ]

import urllib.request
import json
import csv
import datetime
FRONTROW = [
    'Date', '买量', '买价bid', '最新价last', '卖价ask', '卖量', '振幅%change', '涨跌幅change',
    '行权strike', '买量', '买价', '最新价', '卖价', '卖量', '振幅', '涨跌幅', '行权'
]


def match_twins(month: int) -> list:
    prefix = 'http://hq.sinajs.cn/list=OP_'
    # suffix = '_51005017'
    suffix = '_510050'
    url1 = f'{prefix}UP{suffix}{str(month)}'
    url2 = f'{prefix}DOWN{suffix}{str(month)}'
    return get_paried_urls([url1, url2])


def get_paried_urls(twin_list: list) -> list:
    urls = []
    paired_url = []
    for url in twin_list:
        content = urllib.request.urlopen(url, None).read().decode('GBK')
        paired_url.append(get_all_name(content))
    return (re_pair(paired_url))


def get_all_name(content) -> list:
    quo_pos = content.find('"')
    seg = content[quo_pos + 1:-3]
    stock_list = seg.split(',')
    return stock_list[:-1]


def re_pair(li) -> list:
    finished_pair = []
    for i in range(len(li[0])):
        middle_pair = []
        middle_pair.append(li[0][i])
        middle_pair.append(li[1][i])
        finished_pair.append(middle_pair)

    return finished_pair


# PAIR to DATA
def data_parser(double_query):
    prefix = 'http://hq.sinajs.cn/list='

    row = []
    for code in double_query:
        url = prefix + code
        data = urllib.request.urlopen(url, None).read().decode('GBK')

        eq_pos = data.find('=')
        params_seg = data[eq_pos + 2:-3]
        params = params_seg.split(',')
        row.extend(params[0:8])
    return row


# url->
def get_expire_url(month: str) -> str:
    prefixDate = 'http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay?date='
    url = f'{prefixDate}{str(month)}'
    return url


def get_expire_date(url_link: str) -> str:
    with urllib.request.urlopen(url_link) as url:
        data = json.loads(url.read().decode())
        # print(data)
        return (data['result']['data']['expireDay'])


# Writing to CSV
with open('sing_stock_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')

    print('started checking and saving data, it might take a few minutes')
    for i in range(12):
        date_string = ''.join(
            (datetime.date.today() +
             datetime.timedelta(i * 365 / 12)).isoformat().split('-'))
        date = get_expire_date(get_expire_url(date_string[:6]))

        if len(match_twins(date_string[2:6])) == 0:
            print(f'no data found in month {date_string[4:6]}')
        else:
            writer.writerow([f'{date_string[:6]}'])
            print(f'found data from month {date_string[4:6]}, start saving')
            writer.writerow(FRONTROW)
        for pairs in match_twins(date_string[2:6]):
            writer.writerow([date] + data_parser(pairs))
        writer.writerow([])
        print(f'done with data from month {date_string[4:6]}')
