#!usr/bin/env python3

import os
import sys
import glob
from extraction import get_time
from multiprocessing import Pool

for j in ["300","600","900","1200"]:
# def func(j):
    for i in range(20):
        os.system('python3 /home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/AIM.py {}'.format(j))

        with open('/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/comp.csv','a+') as f:
                avg,var,c,total,percent = get_time()
                while var > 20:
                    os.system('python3 /home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/AIM.py {}'.format(j))
                    avg,var,c,total,percent = get_time()
                f.write("Four_way,{},{},{},{},{},{} \n".format(j,avg,var,c,total,percent))

# if __name__ == '__main__':
#     post=["300","600","900","1200"]
#     # for i in post:
#     #     main(i)
#     #using 6 cores for processing 
#     for i in post:
        #   func(post)