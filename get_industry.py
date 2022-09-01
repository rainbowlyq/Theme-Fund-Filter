# _*_coding:utf-8_*_
# @Project: main.py
# @File_Name: get_industry
# @Author: lyq
# @Time: 2022-08-24 17:13
# @Software: Pycharm
from functools import singledispatch
from WindPy import w
import datetime


@singledispatch
def get_industry(code, date=datetime.date.today().strftime("%Y%m%d"), type='中信'):
    print(f'代码输入格式错误')


@get_industry.register(str)
def _(code, date=datetime.date.today().strftime("%Y%m%d"), type='中信') -> str:
    res = w.wss(code, "industry_citic,industry_sw_2021,industry_gics",
                "tradeDate=" + date + ";industryType=1")
    if type == '申万':
        id = 1
    elif type.lower() == 'wind':
        id = 2
    else:
        id = 0
    if res.Data[0][0]:
        return res.Data[id][0]
    else:
        raise ValueError("代码错误")


@get_industry.register(list)
def _(code, date=datetime.date.today().strftime("%Y%m%d"), type='中信') -> list:
    res = w.wss(code, "industry_citic,industry_sw_2021,industry_gics",
                "tradeDate=" + date + ";industryType=1")
    if type == '申万':
        id = 1
    elif type.lower() == 'wind':
        id = 2
    else:
        id = 0
    if res.Data[0]:
        return res.Data[id]
    else:
        raise ValueError("代码错误")
