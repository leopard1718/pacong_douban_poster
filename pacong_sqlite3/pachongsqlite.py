# coding:utf-8

import warnings
import jieba  # 分词包
import numpy  # numpy计算包
import codecs  # codecs提供的open方法来指定打开的文件的语言编码，它会在读取的时候自动转换为内部unicode
import re
import pandas as pd
import matplotlib
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import urllib.request
import xml.etree.ElementTree as ET
import sys
from wordcloud import WordCloud  # 词云包
import json
import sqlite3
from imp import reload

# matplotlib.rcParams['figure.figsize'] = (10.0, 5.0)
warnings.filterwarnings("ignore")

header = {
'Cookie': 'bid=pArJsgRATKM; douban-fav-remind=1; __utmz=223695111.1577960207.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; dbcl2="218241843:VnfGfKNHlqM"; ck=hbx0; push_doumail_num=0; push_noty_num=0; __utma=30149280.1657488056.1577441166.1590719021.1592373846.5; __utmc=30149280; __utmz=30149280.1592373846.5.5.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/register; __utmt=1; __utmv=30149280.21824; __utmb=30149280.14.10.1592373846; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1592374174%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D_rSEnhsCCJduZ-8-BPSzRzAFwS2ye64agnRGlvX70H3FBws8PG_GjY6wJ4WKw4CUJP3DebHSnO-omuJvl1bFt_%26wd%3D%26eqid%3Df3572c8a0007311c000000065e0dc092%22%5D; _pk_id.100001.4cf6=eeeb8cbd05cfd405.1577960207.2.1592374174.1577960207.; _pk_ses.100001.4cf6=*; __utma=223695111.2052048094.1577960207.1577960207.1592374174.2; __utmb=223695111.0.10.1592374174; __utmc=223695111',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
}



# 分析网页函数
def getNowPlayingMovie_list():
    resp = urllib.request.Request('https://movie.douban.com/nowplaying/hangzhou/', headers=header)
    response = urllib.request.urlopen(resp)
    html_data = response.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')
    nowplaying_movie = soup.find_all('div', id='nowplaying')
    nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')
    nowplaying_list = []
    for item in nowplaying_movie_list:
        nowplaying_dict = {}
        nowplaying_dict['name'] = item['data-title']
        for tag_img_item in item.find_all('img'):
            nowplaying_dict['img_src'] = tag_img_item['src']
            nowplaying_list.append(nowplaying_dict)
    return nowplaying_list


def creatNewSqlite():
    try:
        conn = sqlite3.connect('pacongsqlite.db')
        print("Opened database successfully")
    except:
        print("Opened database fail")
        conn.commit()
        conn.close()
    #c.execute("drop table MOVIE_POSTER_URL;")
    c = conn.cursor()
    try:
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='MOVIE_POSTER_URL';")
        sqliteTables = c.fetchall()
        # print(sqliteTables)
        for sqlitetablesname in sqliteTables:
            for tablesname in sqlitetablesname:
                # print(tablesname)
                if tablesname != 0:
                    print("数据库中MOVIE_POSTER_URL表已存在，无需重新创建")
                    break
                else:
                    print("数据库中MOVIE_POSTER_URL表不存在，需要创建")
                    c.execute('''CREATE TABLE MOVIE_POSTER_URL
                    (ID INTEGER PRIMARY KEY autoincrement,
                    NAME           TEXT    NOT NULL,
                    ADDRESS        CHAR(50));''')
    except:
        print("Create tables failed")

    conn.commit()
    conn.close()


def shuju_insert(moviename, moviePosterurl):
    conn = sqlite3.connect('pacongsqlite.db')
    c = conn.cursor()

    try:
        c.execute("SELECT count(*) FROM MOVIE_POSTER_URL WHERE NAME='{0}' or ADDRESS='{1}';".format(moviename,
                                                                                                    moviePosterurl))
        sqliteTables = c.fetchall()
        # print(sqliteTables)
        for sqlitetablesname in sqliteTables:
            for tablesname in sqlitetablesname:
                if tablesname != 0:
                    print("数据库中", moviename, "已存在，无需重新插入")
                    break
                else:
                    print("数据库中", moviename, "不存在，需要插入")
                    c.execute("INSERT INTO MOVIE_POSTER_URL (ID, NAME, ADDRESS) VALUES (null, '{0}', '{1}')".
                              format(moviename, moviePosterurl))
                    print("电影【", moviename, "】数据插入成功")
        # null写死 主键自增 剩下两个字段读取字典循环写入？？
    except:
        print("电影【", moviename, "】数据插入失败")

    conn.commit()
    conn.close()


def shuju_select():
    conn =sqlite3.connect('pacongsqlite.db')
    c = conn.cursor()
    try:
        c.execute("SELECT NAME, ADDRESS  FROM MOVIE_POSTER_URL;")
        moviePoster_alldata = c.fetchall()
        # print moviePoster_alldata
    except:
        print("查询MOVIE_POSTER_URL表中的数据失败")
    return moviePoster_alldata


def download_pic(movie_name, pic_url):
    try:
        f1 = urllib.request.urlopen(pic_url, timeout=5)
        data = f1.read()
    except urllib.error.HTTPError as e:
        return 'download err', e
    except urllib.error.URLError as e:
        return 'download err', e
    else:
        f2 = movie_name+'.jpg'
        with open(f2, "wb") as code:
            code.write(data)
            print("【", movie_name, "】海报下载成功")


def main():
    creatNewSqlite()
    keyvalue_dict_list = getNowPlayingMovie_list()
    print(keyvalue_dict_list)
    for keyvalue_dict in keyvalue_dict_list:
        moviename = keyvalue_dict['name']
        moviePosterurl = keyvalue_dict['img_src']
        shuju_insert(moviename, moviePosterurl)
    nameandpic_alldata = shuju_select()
    for i in nameandpic_alldata:
        movie_name = i[0]
        pic_url = i[1]
        download_pic((movie_name), pic_url)

main()
