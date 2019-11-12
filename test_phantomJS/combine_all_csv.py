#!/usr/bin/env python
#-*- coding:utf-8 -*-
#python 3

import os
from termcolor import colored

def combiner():
    folder_name=input('Please indicate full address of your folder: \n')
    with open('combined_result.csv','a') as f:
        f.write('city'+' '+'district'+' '+'date'+' '+'AQI'+' '+'PM25'+' '+'PM10'+' '+'O3'+' '+'NO2'+' '+'SO2'+' '+'CO'+'\n')
        print('Below cities do not match result size requirement:')
        for a,b,c in os.walk(folder_name):
            if len(c)==0:
                continue
            if os.path.getsize(a+'/'+c[0]) < 1500:
                print(colored(a+'/'+c[0]+': '+str(os.path.getsize(a+'/'+c[0]))+' bytes','red'))
            else:
                with open(a+'/'+c[0]) as temp:
                    temp_list=temp.readlines()
                    for item in temp_list[1:]:
                        f.write(item)
    print("Combination Done!!")

combiner()
