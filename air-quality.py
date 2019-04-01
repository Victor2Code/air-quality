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

def get_single_page_quality(web_content,AQI):
    #因为网站返回的pollutant标签没有顺序，所以函数返回的结果是一个dictionary，11个key分别为[city,district,date,time,AQI,PM2.5,PM10,O3,NO2,CO,SO2]
    #这个函数用于在recursion_body中进行打印到文件
    result={}
    result['AQI']=AQI
    soup=BeautifulSoup(web_content,features="lxml")
    #首先通过更新时间判断这个链接里面有没有信息，没有直接退出。1970-01-01是判断标准。
    update_time=soup.find('div',attrs={'class':'update-time'}).string
    date=update_time.split(' ')[0]
    time=update_time.split(' ')[1]
    if date=='1970-01-01':
        return 
    else:
        result['date']=date
        result['time']=time 
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
        result[name]=value 
    return result 

def get_single_page_locations(web_content):
    #获取网页中“包含的地点”里面所有位置对应的链接，名字以及AQI
    #在recursive_body中作为是否退出的判断(返回None)，同时也是进入下一层递归的入口
    result=[]
    soup=BeautifulSoup(web_content,features='lxml')
    entrance=soup.find('div',text='包含的地点')
    if entrance==None:
        return
    block=entrance.find_next('div')
    all_locations=block.find_all('a')
    for location in all_locations:
        link=location.attrs['href']
        name=location.find('div',attrs={'class':'title'}).string
        #test_tag用来判断有些没有AQI指数的地名
        test_tag=location.find('div',attrs={'class':'value'})
        if test_tag==None:
            AQI=''
        else:
            AQI=test_tag.string.split(' ')[1]
        result.append((link,name,AQI))
    return result 

def recursion_body(url,AQI):
    #从第一层开始，对每一层首先打印出空气质量信息，然后找到“包含的地点”并递归调用本函数
    #一直到找不到“包含的地点”，函数退出
    pass

blank_url='https://air-quality.com/place/china/enshi/9f5f58a6?lang=zh-Hans&standard=aqi_cn'
url='https://air-quality.com/place/china/dongcheng/7319628a?lang=zh-Hans&standard=aqi_cn'
charset='utf-8'
main_url='https://air-quality.com/country/china/ce4c01d6?lang=zh-Hans&standard=aqi_cn'
deepest_url='https://air-quality.com/place/china/hongkou/6a93e3c5?lang=zh-Hans&standard=aqi_cn'
shanghai='https://air-quality.com/place/china/shanghai/90868c5d?lang=zh-Hans&standard=aqi_cn'

web_content=get_web_page(shanghai,charset)
result=get_single_page_quality(web_content,'')
#result=get_single_page_locations(web_content)
print(result)

