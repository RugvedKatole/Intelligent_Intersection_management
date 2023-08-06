#!usr/bin/env python3

#4-way

import os
import sys
from math import sqrt
import numpy as np
import pandas as pd
import random
#from utils import communicate
import networkx as nx

from itertools import product
#
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
from plexe import Plexe, ACC, CACC

def add_single_platoon(plexe, step, lane):
    vid = "v%d.%s" %(step/ADD_PLATOON_STEP, lane)
    routeID = lane   # Lanes as per the conflict matrix
    traci.vehicle.add(vid, routeID, typeID="vtypeauto")        
    traci.vehicle.setSpeedMode(vid, 31)        
    traci.vehicle.setColor(vid, (255,255,255, 255))  # red


def add_platoons(plexe,step):
    spawn_vehs = np.random.poisson(TRAFFIC_DENSITY*N)
    Manuevers = random.sample(LANE_NUM,spawn_vehs)
    for lane in Manuevers:
        add_single_platoon(plexe,step, lane)


def main():

    directory = "/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/adaptive_trafic_lights"
    sumo_cmd = ['sumo', '--duration-log.statistics', '--tripinfo-output',
                 '{}/{}'.format(directory,sys.argv[2]),
                 '-c', '{}/SUMO_CFG/my_confg.sumo.cfg'.format(directory)]
    
    traci.start(sumo_cmd)
    plexe = Plexe()
    traci.addStepListener(plexe)

    step = 0

    while step < 360000:  # 1 hour       

        traci.simulationStep()
        print(step/100)
        if step % ADD_PLATOON_STEP == 0:  # add new platoon every X steps
            add_platoons(plexe,step) 
        


        step += 1

    traci.close()


if __name__ == "__main__":

    conflict_matrix = {}
    df = pd.read_csv("/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/conflict_matrix_4way_compliment.csv")
    for i in df.columns:
        conflict_matrix[i]=[j for j in df[i] if j!= '0' or j!= 0]

    # LANE_NUM = list(df.columns)
    LANE_NUM = conflict_matrix.keys()
    SPEED = 16.6  # m/s
    TRAFFIC_DENSITY = int(sys.argv[1])/3600 # density in PCU/hr/lane dvide by 3600 to get per second
    ADD_PLATOON_STEP = 100 # int(sys.argv[1])
    N = 4  #nway junction
    main()
