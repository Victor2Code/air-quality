#!/usr/bin/env python
#-*- coding:utf-8 -*-
#python 3

import os
from termcolor import colored

def checker():
    folder_name=input('Please indicate full address of your folder: \n')
    for a,b,c in os.walk(folder_name):
        if os.path.getsize(a+'/'+c[0]) < 1500:
            print(colored(a+'/'+c[0]+': '+str(os.path.getsize(a+'/'+c[0]))+' bytes','red'))
        else:
            print(a+'/'+c[0]+': '+str(os.path.getsize(a+'/'+c[0]))+' bytes')

checker()
