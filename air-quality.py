#!/usr/bin/env python
#-*- coding:utf-8 -*-
#python 3

from urllib import request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import time
import multiprocessing

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

def get_web_page(url,charset):
    req=request.Request(url,headers=headers)
    response=request.urlopen(req)
    html=response.read()
    result=html.decode(charset)
    return result

def get_single_page_quality(url,charset):
    #因为网站返回的pollutant标签没有顺序，所以函数返回的结果是一个dictionary，6个key分别为[PM2.5,PM10,O3,NO2,CO,SO2]
    result={}
    page=get_web_page(url,charset)
    soup=BeautifulSoup(page,features="lxml")
    
    #首先通过更新时间判断这个链接里面有没有信息，没有直接退出。1970-01-01是判断标准。
    update_time=soup.find('div',attrs={'class':'update-time'}).string
    date=update_time.split(' ')[0]
    time=update_time.split(' ')[1]
    if date=='1970-01-01':
        return 

    #根据soup来分别获取地理信息以及污染物信息，并更新到result字典里面
    location=soup.find('div',attrs={'class':'detail-title'})
    city=location.find('p').string 
    district=location.find('h2').string 
    result['city']=city
    result['district']=district 
    pollutants=soup.find_all('div',attrs={'class':re.compile(r'pollutant-item.*')})
    for pollutant in pollutants:
        name=pollutant.find('div',attrs={'class':'name'}).string
        value=pollutant.find('div',attrs={'class':'value'}).string
        result[name+'_'+date+'_'+time]=value 
    return result 




blank_url='https://air-quality.com/place/china/enshi/9f5f58a6?lang=zh-Hans&standard=aqi_cn'
url='https://air-quality.com/place/china/dongcheng/7319628a?lang=zh-Hans&standard=aqi_cn'
charset='utf-8'

result=get_single_page_quality(blank_url,charset)
print(result)

