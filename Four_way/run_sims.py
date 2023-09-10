#!usr/bin/env python3

import os
import sys
import glob
from extraction import get_time
from multiprocessing import Pool
import time
from pytz import timezone 
from datetime import datetime

Main_dir ="/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/"

for j in ["150","200","250","300","350"]:
# def func(j):
    ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S.%f')
    results_dir = '../results/unbalanced_1hour_41/{}_Four_way.xml'.format(j)
    os.system('python3 {}AIM.py {} {}'.format(Main_dir,j,results_dir))
    
    with open('/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/comp.csv','a+') as f:
            avg,var,c,total,percent = get_time(results_dir)
            # while var > 20:
            # os.system('python3 /home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/AIM.py {}'.format(j))
            f.write("Four_way,{},{},{},{},{},{},{} \n".format(j,avg,var,c,total,percent,ind_time))
os.system('notify-send "Simulation completed for {} PCUs/lane/hr"'.format(j))