#!/usr/bin/env python
#-*- coding:utf-8 -*-
#python 3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from urllib import request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import datetime
import multiprocessing

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
#link='https://air-quality.com/place/china/dongsi/6ad84d7c?lang=zh-Hans&standard=aqi_cn'
#driver = webdriver.PhantomJS()
chrome_options=Options()
chrome_options.headless=True
driver=webdriver.Chrome(options=chrome_options,executable_path='/home/fuhx/anaconda3/bin/chromedriver')

driver.implicitly_wait(10)
#driver.get(link)
#time.sleep(2)
#action = ActionChains(driver)
# element1=driver.find_element_by_xpath('//*[@id="item_0"]')
# element2=driver.find_element_by_xpath('//*[@id="item_1"]')
# element3=driver.find_element_by_xpath('//*[@id="item_14"]')
# element=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[8]/div[4]')
# for i in range(0,100):
    #action.move_to_element(locals()[name]).perform()
    #try:
        #action.move_to_element(driver.find_element_by_id('item_'+str(i))).perform()
    #目前这个会报错：1.用xpath找到的和页面上显示的最早时间不一致；2.不能用71最为最大值，需要自动去判断
    #except Exception as e:
        #break
    #value=element.text
    #print(value)
#driver.quit()

def get_one_item_history(driver,element):
    result=[]
    item_name=driver.find_element_by_xpath('//*[@id="history-kind-dropdown"]/button/span[1]').text
    city=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/p').text
    district=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/h2').text 
    print('>> 获取 '+item_name+' 中，请等待...')
    # !!! has to add action in every new page !!! otherwise will raise error
    action=ActionChains(driver)
    for i in range(0,100):
        try:
            action.move_to_element(driver.find_element_by_id('item_'+str(i))).perform()
        except Exception as e:
            if i==0:
                time.sleep(3)
                action.move_to_element(driver.find_element_by_id('item_'+str(i))).perform()
            else:
                #print(e)
                break
        value=element.text
        #date1=value.split(' ')[0]
        #time1=value.split(' ')[1][:-1]
        #value1=value.split(' ')[2]
        date1=value.split(' ')[0][:-1]
        value1=value.split(' ')[1]
        result.append((city,district,date1,item_name,value1))
        print(city+' '+district+' '+date1+' '+item_name+' '+value1+' Done!')
    return result 



def single_page_history(driver,link,name,AQI,file_indicator):
    if AQI=='':
        return 
    #all_pollutant_combine里面存放着多个kv对，每个kv对是某时间城市地区组合下的所有污染物的汇总
    all_pollutant_combine={}
    driver.get(link)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="history-interval-dropdown"]/button/span[1]').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="history-interval-dropdown"]/ul/li[2]').click()
    time.sleep(1)
    #action = ActionChains(driver)
    element=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[8]/div[4]')
    #get AQI data
    AQI_history=get_one_item_history(driver,element)
    #从写入文件改为写入到汇总里面
    for temp in AQI_history:
        try:
            all_pollutant_combine[(temp[0],temp[1],temp[2])]={temp[3]:temp[4]}
        except Exception as e:
            continue

    #    file_indicator.write(temp[0]+' '+temp[1]+' '+temp[2]+' '+temp[3]+' '+temp[4]+'\n')
    
    for i in range(2,8):
        driver.find_element_by_xpath('//*[@id="history-kind-dropdown"]/button/span[1]').click()
        try:
            driver.find_element_by_xpath('//*[@id="history-kind-dropdown"]/ul/li[{}]'.format(i)).click()
        except Exception as e:
            return 'Success' 
        time.sleep(2)
        one_item=get_one_item_history(driver,element)
        for temp in one_item:
            try:
                all_pollutant_combine[(temp[0],temp[1],temp[2])][temp[3]]=temp[4]
            except Exception as e:
                continue
            #file_indicator.write(temp[0]+' '+temp[1]+' '+temp[2]+' '+temp[3]+' '+temp[4]+'\n')
    print('>> 最终爬取结果如下')
    print(all_pollutant_combine)
    for item in all_pollutant_combine:
        try:
            file_indicator.write(item[0]+' '+item[1]+' '+item[2]+' '+all_pollutant_combine[item]['AQI (中国标准)']+' '+all_pollutant_combine[item]['PM2.5']+' '+all_pollutant_combine[item]['PM10']+' '+all_pollutant_combine[item]['O3']+' '+all_pollutant_combine[item]['NO2']+' '+all_pollutant_combine[item]['SO2']+' '+all_pollutant_combine[item]['CO']+'\n')
        except Exception as e:
            continue
    return 'Success'

def get_web_page(url,charset):
    req=request.Request(url,headers=headers)
    response=request.urlopen(req)
    html=response.read()
    result=html.decode(charset)
    return result

def str_to_datetime(str):
    #因为网站上的时间只是到分钟，并没有到秒，所以下面没有%S
    timestamp=time.mktime(time.strptime(str,'%Y-%m-%d %H:%M'))
    utc_8=datetime.datetime.fromtimestamp(timestamp)+datetime.timedelta(hours=8)
    return utc_8.strftime('%Y-%m-%d %H:%M')

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


def recursion_body(driver,url,name,AQI,file_indicator):
    #从第一层开始，对每一层首先打印出空气质量信息，然后找到“包含的地点”并递归调用本函数
    #一直到找不到“包含的地点”，函数退出
    web_content=get_web_page(url,'utf-8')
    #quality=get_single_page_quality(web_content,AQI)
    history_data=single_page_history(driver,url,name,AQI,file_indicator)
    if history_data==None:
       return
    #print(quality['city']+'-'+quality['district']+' Done!')
    #file_indicator.write(quality['city']+' '+quality['district']+' '+quality['date']+' '+quality['time']+' '+quality['AQI']+' '+quality['PM2.5']+' '+quality['PM10']+' '+quality['O3']+' '+quality['NO2']+' '+quality['CO']+' '+quality['SO2']+'\n')
    locations=get_single_page_locations(web_content)
    if locations==None:
        return
    for location in locations:
        recursion_body(driver,location[0],location[1],location[2],file_indicator)


def main(driver,url,charset):
    #参数为主页面的url和charset，对返回的所有地名进行迭代输出，每个省一个文件，文件名为省的名字
    #首先会检查provinces.txt文件是否存在，存在则段点续传，不存在则重新获取链接，从第一个省开始传
    if not os.path.isfile('provinces.txt'):
        print('=== === === === === ===')
        print('>> 没有发现 provinces.txt 文件，获取中...')
        provinces=get_single_page_locations(get_web_page(url,charset))
        for province in provinces:
            with open('provinces.txt','a') as f:
                f.write(' '.join(province)+'\n')
        print('>> 【成功】 获取 provinces.txt 完成')
    print('=== === === === === ===')
    print('>> 获取待爬取数据信息')
    with open('provinces.txt','r') as f:
        total_provinces=f.readlines()
        province_number=len(total_provinces)
        print('>>【成功】 一共有 '+str(province_number)+' 个省的数据需要爬取')
    print('=== === === === === ===')
    finished_province=0
    for province in total_provinces:
        print('>> 开始获取 '+province.split(' ')[1]+'省 的数据，请等待')
        if os.path.isfile(province.split(' ')[1]+'.csv'):
            os.remove(province.split(' ')[1]+'.csv')
            print('>> 发现过去残留文件 '+province.split(' ')[1]+'.csv ，已删除')
        with open(province.split(' ')[1]+'.csv','a') as f:
            f.write('city'+' '+'district'+' '+'date'+' '+'AQI'+' '+'PM25'+' '+'PM10'+' '+'O3'+' '+'NO2'+' '+'SO2'+' '+'CO'+'\n')
            recursion_body(driver,province.split(' ')[0],province.split(' ')[1],province.split(' ')[2],f)
        finished_province+=1
        with open('provinces.txt','w') as f:
           for line in total_provinces[finished_province:]:
                f.write(line)
us_embassy_test_link='https://air-quality.com/place/china/xuhui/a0217a2f?lang=zh-Hans&standard=aqi_cn'
link='https://air-quality.com/country/china/ce4c01d6?lang=zh-Hans&standard=aqi_cn'
#single_page_history(driver,link,'test',33)
main(driver,link,'utf-8')
driver.quit()
