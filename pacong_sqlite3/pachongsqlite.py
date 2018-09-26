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



# 分析网页函数
def getNowPlayingMovie_list():
    resp = urllib.request.Request('https://movie.douban.com/nowplaying/hangzhou/')
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
        print ("Opened database successfully")
    except:
        print ("Opened database fail")
        conn.commit()
        conn.close()
    #c.execute("drop table MOVIE_POSTER_URL;")
    c = conn.cursor()
    try:
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='MOVIE_POSTER_URL';")
        sqliteTables = c.fetchall()
        print (sqliteTables)
        for sqlitetablesname in sqliteTables:
            for tablesname in sqlitetablesname:
                print (tablesname)
                if tablesname != 0:
                    print ("数据库中MOVIE_POSTER_URL表已存在，无需重新创建")
                    break
                else:
                    print ("数据库中MOVIE_POSTER_URL表不存在，需要创建")
                    c.execute('''CREATE TABLE MOVIE_POSTER_URL
                    (ID INTEGER PRIMARY KEY autoincrement,
                    NAME           TEXT    NOT NULL,
                    ADDRESS        CHAR(50));''')
    except:
        print ("Create tables failed")

    conn.commit()
    conn.close()


def shuju_insert(moviename, moviePosterurl):
    conn = sqlite3.connect('pacongsqlite.db')
    c = conn.cursor()

    try:
        c.execute("SELECT count(*) FROM MOVIE_POSTER_URL WHERE NAME='{0}' or ADDRESS='{1}';".format(moviename,
                                                                                                    moviePosterurl))
        sqliteTables = c.fetchall()
        print (sqliteTables)
        for sqlitetablesname in sqliteTables:
            for tablesname in sqlitetablesname:
                if tablesname != 0:
                    print ("数据库中", moviename, "已存在，无需重新插入")
                    break
                else:
                    print ("数据库中", moviename, "不存在，需要插入")
                    c.execute("INSERT INTO MOVIE_POSTER_URL (ID, NAME, ADDRESS) VALUES (null, '{0}', '{1}')".format(moviename, moviePosterurl))
                    print ("电影【", moviename, "】数据插入成功")
        # null写死 主键自增 剩下两个字段读取字典循环写入？？
    except:
        print ("电影【", moviename, "】数据插入失败")

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
        print ("查询MOVIE_POSTER_URL表中的数据失败")
    return moviePoster_alldata


def download_pic(movie_name, pic_url):
    try:
        f1 = urllib.request.urlopen(pic_url, timeout=5)
        data = f1.read()
    except urllib.HTTPError as e:
        return 'download err', e
    except urllib.URLError as e:
        return 'download err', e
    else:
        f2 = movie_name+'.jpg'
        with open(f2, "wb") as code:
            code.write(data)
            print ("【", movie_name, "】海报下载成功")


def main():
    creatNewSqlite()
    keyvalue_dict_list = getNowPlayingMovie_list()
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


