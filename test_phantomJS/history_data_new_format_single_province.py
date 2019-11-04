#!/usr/bin/env python
#-*- coding:utf-8 -*-
#python 3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from urllib import request, error
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import datetime
import multiprocessing
import shutil

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}
#link='https://air-quality.com/place/china/dongsi/6ad84d7c?lang=zh-Hans&standard=aqi_cn'
#driver = webdriver.PhantomJS()
chrome_options=Options()
#chrome_options.headless=True
driver=webdriver.Chrome(options=chrome_options,executable_path='/home/fuhx/anaconda3/bin/chromedriver')

driver.implicitly_wait(15)
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
    print('>> 获取 '+city+' '+district+' '+item_name+' 中，请等待...',end='\r',flush=True)
    # !!! has to add action in every new page !!! otherwise will raise error
    action=ActionChains(driver)
    #use while loop to change variable i to repeat on error
    i=0
    while i < 30:
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
        if len(value)==0:
            continue 
        #date1=value.split(' ')[0]
        #time1=value.split(' ')[1][:-1]
        #value1=value.split(' ')[2]
        #print(value)
        date1=value.split(' ')[0][:-1]
        try:
            value1=value.split(' ')[1]
        except Exception as e:
            continue
        if value1[-1] == ',':
            return  
        result.append((city,district,date1,item_name,value1))
        print(city+' '+district+' '+date1+' '+item_name+' '+value1+' Done!')
        i+=1
    print('>> 获取 '+city+' '+district+' '+item_name+' 完成',end='\r',flush=True)
    return result 



def single_page_history(driver,link,name,AQI,file_indicator):
    if AQI=='' or AQI=='\n':
        return 
    #all_pollutant_combine里面存放着多个kv对，每个kv对是某时间城市地区组合下的所有污染物的汇总
    all_pollutant_combine={}
    while True:
        try:
            driver.get(link)
            time.sleep(5)
            driver.find_element_by_xpath('//*[@id="history-interval-dropdown"]/button/span[1]').click()
            time.sleep(3)
            driver.find_element_by_xpath('//*[@id="history-interval-dropdown"]/ul/li[2]').click()
            time.sleep(5)
            #action = ActionChains(driver)
            element=driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[8]/div[4]')
            #get AQI data
            AQI_history=get_one_item_history(driver,element)
            if AQI_history == None:
                continue
            else:
                break
        except Exception as e:
            continue 
    #print(AQI_history)
    #从写入文件改为写入到汇总里面
    for temp in AQI_history:
        try:
            all_pollutant_combine[(temp[0],temp[1],temp[2])]={temp[3]:temp[4]}
        except Exception as e:
            print("ERROR: save AQI to all_pollutant_combine failed!!!")
            continue
    #print(all_pollutant_combine)
    #    file_indicator.write(temp[0]+' '+temp[1]+' '+temp[2]+' '+temp[3]+' '+temp[4]+'\n')
    
    for i in range(2,9):
        driver.find_element_by_xpath('//*[@id="history-kind-dropdown"]/button/span[1]').click()
        try:
            driver.find_element_by_xpath('//*[@id="history-kind-dropdown"]/ul/li[{}]'.format(i)).click()
        except Exception as e:
            break 
            #return 'Success' 
        time.sleep(5)
        one_item=get_one_item_history(driver,element)
        #print(one_item)
        for temp in one_item:
            try:
                all_pollutant_combine[(temp[0],temp[1],temp[2])][temp[3]]=temp[4]
            except Exception as e:
                print("ERROR: save to all_pollutant_combine failed!!!")
                continue
            #file_indicator.write(temp[0]+' '+temp[1]+' '+temp[2]+' '+temp[3]+' '+temp[4]+'\n')
            #print(all_pollutant_combine)
    #有些地区可能污染物数目不足7个，下面的这个逻辑会将不存在的污染物自动填充为'--'
    for item in all_pollutant_combine:
        if not 'AQI (中国标准)' in all_pollutant_combine[item].keys():
            all_pollutant_combine[item]['AQI (中国标准)']='--'
        if not 'PM2.5' in all_pollutant_combine[item].keys():
            all_pollutant_combine[item]['PM2.5']='--'
        if not 'PM10' in all_pollutant_combine[item].keys():
            all_pollutant_combine[item]['PM10']='--'
        if not 'O3' in all_pollutant_combine[item].keys():
            all_pollutant_combine[item]['O3']='--'
        if not 'NO2' in all_pollutant_combine[item].keys():
            all_pollutant_combine[item]['NO2']='--'
        if not 'SO2' in all_pollutant_combine[item].keys():
            all_pollutant_combine[item]['SO2']='--'
        if not 'CO' in all_pollutant_combine[item].keys():
            all_pollutant_combine[item]['CO']='--'
    print('>> 最终爬取结果如下')
    print(all_pollutant_combine)
    if len(all_pollutant_combine)<25:
        print('>> 【ERROR】30天数据最终获取结果少于25天，请检查后再段点续传')
        exit()
    for item in all_pollutant_combine:
        try:
            file_indicator.write(item[0]+' '+item[1]+' '+item[2]+' '+all_pollutant_combine[item]['AQI (中国标准)']+' '+all_pollutant_combine[item]['PM2.5']+' '+all_pollutant_combine[item]['PM10']+' '+all_pollutant_combine[item]['O3']+' '+all_pollutant_combine[item]['NO2']+' '+all_pollutant_combine[item]['SO2']+' '+all_pollutant_combine[item]['CO']+'\n')
        except Exception as e:
            print("ERROR: can not write to file !!!!")
            continue 
    return 'Success'

def get_web_page(url,charset):
    i=0
    while True:
        req=request.Request(url,headers=headers)
        try:
            response=request.urlopen(req)
        except error.HTTPError as e:
            if str(e.code) == '502':
                continue 
        html=response.read()
        result=html.decode(charset)
        print(len(result))
        if not len(result)<25000:
            break
        i+=1
        if i == 20:
            print('【失败】尝试20次但是网页'+url+'无法访问')
            exit()
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

def get_root_folder_name(url,charset):
    while True:
        web_content=get_web_page(url,charset)
        soup=BeautifulSoup(web_content,features='lxml')
        title=soup.find('div',attrs={'class':'detail-title'})
        title_name=title.find('h2').string
        if not title_name==None:
            break
    return title_name 

def main(driver,url,charset,AQI):
    #从最上层开始，每一级都会创建一个目录，并且创建areas.txt记录下面所有的区域，方便段点续传
    area_name=get_root_folder_name(url,charset)
    print(area_name)
    if os.path.isdir(area_name):
        print('=== === === === === ===')
        print('>> 发现 {} 文件夹，开始段点续传'.format(area_name))
        os.chdir(area_name)
        if not os.path.isfile(area_name+'.txt'):
            if len(os.listdir('.'))<=1:
                if os.path.isfile(area_name+'.csv'):
                    print('>> 此区域已下载完成，返回上级目录')
                    os.chdir('..')
                    print(os.getcwd())
                    return 
                print('>> 文件夹内为空，删除文件夹从头开始')
                os.chdir('..')
                print(os.getcwd())
                shutil.rmtree(area_name)
                main(driver,url,charset,AQI)
            else:
                print('>> 此区域已下载完成，返回上级目录')
                os.chdir('..')
                print(os.getcwd())
                return 
        else:
            print('>> 本区域下载完成，检查子区域中')
            with open(area_name+'.txt','r') as f:
                sub_areas=f.readlines()
            print('>> 一共有{}个子区域'.format(len(sub_areas)))
            finished_subarea=0
            for sub_area in sub_areas:
                main(driver,sub_area.split(' ')[0],charset,sub_area.split(' ')[2])
                finished_subarea+=1
                if finished_subarea==len(sub_areas):
                    print('>> 【成功】 所有子区域历史数据获取完成，返回上一级目录...')
                    os.remove(area_name+'.txt')
                    os.chdir('..')
                    print(os.getcwd())
                    return
                with open(area_name+'.txt','w') as f:
                    for line in sub_areas[finished_subarea:]:
                        f.write(line)
            print('>> 所有子区域下载完成')
            return 
    if not os.path.isdir(area_name):
        print('=== === === === === ===')
        print('>> 没有发现 {} 文件夹，创建中...'.format(area_name))
        os.mkdir(area_name)
        os.chdir(area_name)
        print(os.getcwd())
        print('>> 进去文件夹，获取 {} 历史数据中...'.format(area_name))
        with open(area_name+'.csv','a') as f:
            f.write('city'+' '+'district'+' '+'date'+' '+'AQI'+' '+'PM25'+' '+'PM10'+' '+'O3'+' '+'NO2'+' '+'SO2'+' '+'CO'+'\n')
            history_data=single_page_history(driver,url,area_name,AQI,f)
            if history_data==None:
                os.chdir('..')
                print(os.getcwd())
                return
        if os.path.getsize(area_name+'.csv')<1500:
            print('【ERROR】文件大小过小，请检查后再段点续传')
            exit()
        print('>> 获取 {} 历史数据完成，查看子区域信息...'.format(area_name),end='\r',flush=True)
        sub_areas=get_single_page_locations(get_web_page(url,charset))
        if sub_areas==None:
            print('>> 没有找到子区域信息，返回上一级目录...')
            os.chdir('..')
            print(os.getcwd())
            return 
        for sub_area in sub_areas:
            with open(area_name+'.txt','a') as f:
                f.write(' '.join(sub_area)+'\n')
        print('>> 【成功】 获取子区域信息完成')
        print('>> 【成功】 一共有 '+str(len(sub_areas))+' 个子区域的数据需要爬取')
        print('=== === === === === ===')
        finished_subarea=0
        for sub_area in sub_areas:
            print('>> 开始获取 '+sub_area[1]+' 的数据，请等待')
            main(driver,sub_area[0],charset,sub_area[2])
            print(os.getcwd())
            finished_subarea+=1
            if finished_subarea==len(sub_areas):
                print('>> 【成功】 所有子区域历史数据获取完成，返回上一级目录...')
                os.remove(area_name+'.txt')
                os.chdir('..')
                print(os.getcwd())
                return 
            with open(area_name+'.txt','a') as f:
                for line in sub_areas[finished_subarea:]:
                    f.write(' '.join(line)+'\n')

us_embassy_test_link='https://air-quality.com/place/china/xuhui/a0217a2f?lang=zh-Hans&standard=aqi_cn'
link='http://testtest.com'
#single_page_history(driver,link,'test',33)
#main(driver,link,'utf-8')
main(driver,link,'utf-8',33)
driver.quit()
