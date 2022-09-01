# _*_coding:utf-8_*_
# @Project: PROJECT
# @File_Name: main
# @Author: lyq
# @Software: Pycharm


from WindPy import w
import pandas as pd
import sys
import os
import datetime
import time
import Config


# 输出给定指数的名称和权重列表
def constituents_industry_dist(indexcode: str, date: str = '', med2: bool = False, type: str = '中信') -> list:
    """
    输出给定指数的名称和权重列表[[name1,name2,...],[weight1,weight2,...]]
    :param med2: bool
    :param date: str
    :param indexcode: str
    :param type: type
    :return: list
    """

    # 如果不输入日期，则使用最新日期
    if date == '':
        date = datetime.date.today().strftime("%Y-%m-%d")

    # 根据选择的行业分类调整api参数
    if type.lower() == 'wind1':
        s = 'windsectors'
    elif type.lower() == 'wind2':
        s = 'windsectors'
    elif type == '申万':
        s = 'swssectors'
    else:
        s = 'citicsectors'

    # 取出指数成分行业数据
    options = "windcode=" + indexcode + ";enddate=" + date + ";industry=" + s + ";field=name,weight"
    res = w.wset("constituentsindustrydist", options).Data

    # 取用失败则报错退出
    if not res:
        print("指数代码输入错误")
        exit(1)

    # 医药板块展开到二级板块
    if med2 and type == '中信' and '医药' in res[0]:
        # 删除医药一级行业数据
        i = res[0].index('医药')
        res[0].pop(i)
        res[1].pop(i)

        # 获取全部二级行业数据并保留医药行业的二级数据
        medlist = ['化学制药', '中药生产', '生物医药Ⅱ', '其他医药医疗']
        options = "windcode=" + indexcode + ";enddate=" + date + ";industry=citicindustrygroups;field=name,weight"
        [names, weights] = w.wset("constituentsindustrydist", options).Data

        for i, name in enumerate(names):
            if name in medlist:
                res[0].append(name)
                res[1].append(weights[i])

    # if med2 and type == '申万':
    #     ids = []
    #     industry1 = ['医药生物', '农林牧渔', '国防军工']

    return res


def get_my_constituents_industry_dist(indexes: list, theme: str, date: str = '', med2: bool = False,
                                      type: str = '中信') -> pd.DataFrame:
    """
    index:index codes
    columns:name of industries
    :param type:
    :param med2:
    :param theme:
    :param indexes:
    :param date:
    :return:
    """

    # 如果不输入日期，则使用最新日期
    if date == '':
        date = datetime.date.today().strftime("%Y-%m-%d")

    industries = []
    data = []

    for index in indexes:
        dic = {}
        [names, weights] = constituents_industry_dist(index, date, med2, type)
        for i, name in enumerate(names):
            if name not in industries:
                industries.append(name)
            dic[name] = weights[i]
        data.append(dic)

    # 空数据填充0
    df = pd.DataFrame(data, indexes, industries).fillna(0)
    df.index.name = "wind_code"
    # 保存数据
    df.to_excel(theme + "/多指数行业分布.xlsx")

    return df


def main_process(configs: Config.Config = None):
    # 参数更新
    global theme, filterlist, filterlist, custom_stockpool, indexlist, lastquarter, quarternum
    global threshold, auto, threshold2, qnum_1, qnum_2, idtype, alwaysfilter1, filter1only, med2

    if configs is None:
        # --------------配置参数---------------
        # 所有标点使用英文半角符号

        # 主题名称
        theme = "碳中和"
        # 填写wind中筛选方案名称
        # filterlist = ['三年主动', '一年半标准指数', '一年半增强指数', '次新基金']
        filterlist = ['三年主动']
        # 是否使用自定义股票池（1：是  0：否）
        custom_stockpool = 0
        # 填写各指数的wind代码，格式同筛选方案（如果使用自定义股票池可以忽略）
        indexlist = ['931755.CSI']
        # 最新季度末日期
        lastquarter = '20220630'
        # 需要计算的季度数量
        quarternum = 12
        # 初筛阈值(%)
        threshold = 40

        # 是否自动筛选
        # 1：自动筛选（保留符合多季度要求的基金） 0：不自动筛选（保留所有初筛得到的基金）
        auto = 1
        # 以下默认参数表示筛选 最新【4】个季度中至少有【3】个季度指数成分股持仓比例高于【50】%的基金
        # 复筛阈值(%)
        threshold2 = 50
        # 复筛条件
        qnum_1 = 4
        qnum_2 = 3

        # 行业
        idtype = '中信'
        # 是否每次运行都重新初筛（修改参数后需要修改为True）
        alwaysfilter1 = False
        # 只进行初筛，不进行后续计算
        filter1only = False
        # 展开中信医药二级行业（不建议修改）
        med2 = True

        # --------------配置参数---------------
    else:
        # 根据窗体控件获取配置数据
        alwaysfilter1 = configs.alwaysfilter1
        auto = configs.auto
        custom_stockpool = configs.custom_stockpool
        filter1only = configs.filter1only
        filterlist = configs.filterlist
        indexlist = configs.indexlist
        lastquarter = configs.lastquarter
        med2 = configs.med2
        qnum_1 = configs.qnum_1
        qnum_2 = configs.qnum_2
        quarternum = configs.quarternum
        theme = configs.theme
        threshold = configs.threshold
        threshold2 = configs.threshold2
        idtype = configs.type

    # 生成日期列表
    def cal_datelist(quarternum: int, lastquarter: str) -> list:
        datelist = []
        latest = lastquarter
        quarters = ['0331', '0630', '0930', '1231']
        for i in range(quarternum):
            datelist.append(latest)
            quarter_index = quarters.index(latest[-4:])
            if quarter_index == 0:
                date = str(int(latest[:4]) - 1) + quarters[quarter_index - 1]
            else:
                date = latest[:4] + quarters[quarter_index - 1]
            latest = date
        return datelist

    # 获得股票池
    def stockpool(custom: bool, indexlist: list, date: str, first: bool = False) -> list:
        # 如果使用自定义股票池则直接读取文件
        if custom:
            try:
                df = pd.read_excel("自定义股票池.xls", usecols=[0], names=None)
                df = df.values.tolist()
                res = []
                for s in df:
                    res.append(s[0])
                return res
            except FileNotFoundError:
                print('未找到"自定义股票池.xls"文件，开始自动股票池计算')
                return stockpool(False, indexlist, date, True)

        else:
            # 如果不使用自定义股票池则自动根据指数计算股票池
            if first and custom_stockpool == 0:
                # 首次
                get_my_constituents_industry_dist(indexlist, theme, date, med2, idtype)
                first = False
            stdlist = []
            for indexcode in indexlist:
                temp = w.wset("indexconstituent", "date=" + date + ";windcode=" + indexcode).Data
                if len(temp) < 2:
                    return []
                else:
                    stdlist += temp[1]
            stdlist = list(set(stdlist))
            df = pd.DataFrame(stdlist, columns=['wind_code'])
            # 将股票池保存在“股票池”文件夹
            if not os.path.exists(theme + "/股票池"):
                os.mkdir(theme + "/股票池")
            df.to_excel(theme + "/股票池/" + date + ".xlsx", index=False)
            return stdlist

    # 初筛
    def filter1(ft: str, codelist: list, date: str, threshold: int, indexlist: list) -> list:
        # 创建“初筛结果”文件夹
        if not os.path.exists(theme + "/初筛结果"):
            os.mkdir(theme + "/初筛结果")

        try:
            if alwaysfilter1:
                raise FileNotFoundError()
            # 如果已有初筛结果则直接读取文件数据
            df = pd.read_excel(theme + "/初筛结果/" + ft + lastquarter + ".xls", usecols=[0], names=None)
            print("检测到已有初筛结果")
            fl = []
            for f in df.values.tolist():
                fl.append(f[0])
            return fl
        except FileNotFoundError:
            # 如果没有初筛结果则开始初筛
            print("未检测到已有初筛结果文件，开始初筛，初筛阈值：" + str(threshold) + "%")

            # 获取指数成分股wind代码列表
            stdlist = stockpool(custom_stockpool == 1, indexlist, date, True)
            print("主题股票池数量：", len(stdlist))

            # 初始化结果列表
            final_list = []
            rate_list = []
            count = 0
            countall = len(codelist)

            # 遍历筛选方案中的所有基金
            for code in codelist:

                # 获取基金十大重仓股的代码和持股比例
                options = "rptdate=" + date + ";windcode=" + code + ";field=stock_code,proportiontototalstockinvestments"
                stock_data = w.wset("allfundhelddetail", options).Data

                # 如果wind中缺少基金重仓股等相关数据则剔除
                if len(stock_data) == 2:
                    stock_codelist = stock_data[0]
                    stock_ratelist = stock_data[1]
                else:
                    codelist.remove(code)
                    continue

                # 计算该基金十大重仓股中属于指数成分股的持股比例（持股市值占股票投资市值的比例）之和
                sum_rate = 0
                for i in range(len(stock_codelist)):
                    if stock_codelist[i] in stdlist:
                        sum_rate += stock_ratelist[i]

                # 如果持有指数成分股的比例高于设定的阈值，则加入结果列表
                if sum_rate >= threshold:
                    final_list.append(code)
                    rate_list.append(sum_rate)

                # 输出处理进度
                count += 1
                print('\r当前进度：' + str(count) + '/' + str(countall), end="")

            print()

            # 将初筛结果写入文件
            df = pd.DataFrame({'wind_code': final_list, '主题股覆盖率': rate_list})
            df.to_excel(theme + "/初筛结果/" + ft + date + ".xls", index=False)

            # 返回初筛结果
            return final_list

    # 计算指数成分股比例
    def cal(codelist: list, date: str, indexlist: list):
        # 获取指数成分股wind代码列表
        indexdata = stockpool(custom_stockpool == 1, indexlist, date, False)

        # 如果有当期指数成分股的数据就更新，否则采用最早一期的数据
        global stdlist
        if indexdata:
            stdlist = indexdata

        # 初始化结果列表
        sum_list = []
        count = 0
        countall = len(codelist)

        # 遍历所有初筛得到的基金
        for code in codelist:

            # 获取基金十大重仓股的代码和持股比例
            options = "rptdate=" + date + ";windcode=" + code + ";field=stock_code,proportiontototalstockinvestments"
            stock_data = w.wset("allfundhelddetail", options).Data

            # 如果wind中缺少基金重仓股等相关数据则将结果记为0
            if len(stock_data) >= 2:
                stock_codelist = stock_data[0]
                stock_ratelist = stock_data[1]
            else:
                sum_list.append(0)
                continue

            # 计算该基金十大重仓股中属于指数成分股的持股比例（持股市值占股票投资市值的比例）之和
            sum_rate = 0
            for i in range(len(stock_codelist)):
                if stock_codelist[i] in stdlist:
                    sum_rate += stock_ratelist[i]

            # 将结果加入结果列表
            sum_list.append(sum_rate)
            count += 1
            print('\r当前进度：' + str(count) + '/' + str(countall), end="")
        print()

        # 返回结果列表
        return sum_list

    # 按照跟踪的指数排序被动型基金
    def sort_passive(df: pd.DataFrame):
        indexes = list(df.index)
        idstr = ""
        for id in indexes:
            idstr += id + ','
        idstr += '\b'
        print(idstr)
        df2 = w.wss(idstr, "fund_trackindexcode", usedf=True)[1]
        df['trackcode'] = df2['FUND_TRACKINDEXCODE']
        df = df.sort_values(by='trackcode')
        df = df.drop(columns="trackcode")
        return df

    # 记录程序开始运行的时间
    starttime = time.time()

    # 连接wind
    w.start(waitTime=30)  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
    if not w.isconnected():  # 判断WindPy是否已经登录成功
        sys.exit("wind连接失败！请检查是否联网、是否安装wind并修复Python插件")

    # 获得日期列表
    datelist = cal_datelist(quarternum, lastquarter)

    # 创建主题目录
    if not os.path.exists(theme):
        os.mkdir(theme)

    # 遍历所有筛选方案
    for ft in filterlist:
        # 取出筛选方案中的基金列表
        codelist = w.weqs(ft).Codes

        print("------", ft, "(", len(codelist), "支)处理中------")

        # 如果此前进行过初筛，则直接读取文件，否则进行初筛
        filtered_codelist = filter1(ft, codelist, lastquarter, threshold, indexlist)

        print("初筛完成，共筛选出", len(filtered_codelist), "支基金")

        if filter1only:
            # 终止wind连接
            w.stop()
            # 计算程序结束时时间
            endtime = time.time()
            # 输出程序运行总时间
            print("运行完毕，总共用时%s秒" % str(round(endtime - starttime, 2)))
            return

        print("开始计算各季度数据：")

        # 计算各季度的指数成分股持股比例
        dct = {}
        for date in datelist:
            print(date, "计算中")
            dct[date] = cal(filtered_codelist, date, indexlist)
        df = pd.DataFrame(dct, index=filtered_codelist, columns=dct.keys())

        # 自动筛选
        if auto:
            print("筛选开始\n阈值:", threshold2)
            lines = []
            indexes = []
            for row in df.itertuples():
                count = qnum_1
                for i in range(1, 1 + qnum_1):
                    if 0 < row[i] < threshold2:
                        count -= 1
                if count >= qnum_2:
                    indexes.append(row[0])
                    lines.append(row[1:])
            df = pd.DataFrame(lines, index=indexes, columns=datelist)
        else:
            indexes = filtered_codelist

        # 将结果excel文件保存至“结果”文件夹中
        # df=df.ix[:,::-1]
        if '指' in ft or '被' in ft:
            df = sort_passive(df)
        df.index.name = 'wind_code'
        if not os.path.exists(theme + "/结果"):
            os.mkdir(theme + "/结果")
        df.to_excel(theme + "/结果/" + ft + lastquarter + ".xlsx")

        # 打印程序运行结果
        print("计算完毕,共筛选出" + str(len(indexes)) + "支基金")
        print()

    # 终止wind连接
    w.stop()

    # 计算程序结束时时间
    endtime = time.time()

    # 输出程序运行总时间
    print("运行完毕，总共用时%s秒" % str(round(endtime - starttime, 2)))


def industry_only(configs: Config.Config = None):
    print("开始生成多指数行业分布表")

    if configs is not None:

        # 记录程序开始运行的时间
        starttime = time.time()

        # 连接wind
        w.start(waitTime=30)  # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒
        if not w.isconnected():  # 判断WindPy是否已经登录成功
            sys.exit("wind连接失败！请检查是否联网、是否安装wind并修复Python插件")

        # 参数更新
        indexlist = configs.indexlist
        lastquarter = configs.lastquarter
        med2 = configs.med2
        theme = configs.theme
        idtype = configs.type

        # 执行
        get_my_constituents_industry_dist(indexlist, theme, lastquarter, med2, idtype)

        # 终止wind连接
        w.stop()

        # 计算程序结束时时间
        endtime = time.time()

        # 输出程序运行总时间
        print("运行完毕，总共用时%s秒" % str(round(endtime - starttime, 2)))


if __name__ == "__main__":
    main_process()
