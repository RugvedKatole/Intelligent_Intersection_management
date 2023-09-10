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
    plexe.set_path_cacc_parameters(vid, DISTANCE, 2, 1, 0.5)
    # plexe.set_cc_desired_speed(vid, random.randint(4,10))
    # plexe.set_cc_desired_speed(vid, 10)
    plexe.set_acc_headway_time(vid, 1.5)
    plexe.use_controller_acceleration(vid, False)
    plexe.set_fixed_lane(vid, lane, False) #changed code for plexe because no lanes exits in our case change plexe_sumo_exlipse.py line 116
    traci.vehicle.setSpeedMode(vid, 0)
    plexe.set_active_controller(vid, ACC)


def add_platoons(plexe,step):
    grouped_lanes = group_keys(LANE_NUM)
    for i in range(len(group_keys(LANE_NUM))):
        spawn_vehs = np.random.poisson(TRAFFIC_DENSITY[i])
        Manuevers = random.sample(grouped_lanes[i],spawn_vehs)
        for lane in Manuevers:
            add_single_platoon(plexe,step, lane)

def group_keys(keys):
    grouped_dict = {}
    for key in keys:
        starting_letter = key[0]
        if starting_letter in grouped_dict:
            grouped_dict[starting_letter].append(key)
        else:
            grouped_dict[starting_letter] = [key]
    
    grouped_list = list(grouped_dict.values())
    return grouped_list

def intersect(A: list, B:list):
    """ intersects two lists"""
    return [i if i ==j else 0 for i,j in zip(A,B)]

def intersection_manger(input_vehs,G: nx.graph):
    """THE ACTUAL ALGORITHM"""
    incoming = {}
    for i in input_vehs:
        incoming[i.split(".")[1]] = i.split(".")[0]
    # input_vehs= [".".join([i.split(".")[1],i.split(".")[0]]) for i in input_vehs]
    # input_vehs = sorted(input_vehs)
    # input_vehs = [".".join([i.split(".")[1],i.split(".")[0]]) for i in input_vehs]
    input = incoming.keys()
    output_list = input
    Gs = G.subgraph(input)
    output_list = sorted(sorted(list(nx.find_cliques(Gs)),key=len,reverse=True),key=lambda clique: sorted(clique,key=lambda man: man.split("_")[0]))
    if len(output_list) != 0:
        output_list = [".".join([incoming[j],j]) for j in output_list[0]]
    return output_list, input_vehs




def main():
    directory = "/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way"
    sumo_cmd = ['sumo', '--duration-log.statistics', '--tripinfo-output',
                 '{}/{}'.format(directory,sys.argv[2]),
                 '-c', '{}/SUMO_CFG/my_confg.sumo.cfg'.format(directory)]
    
    traci.start(sumo_cmd)
    plexe = Plexe()
    traci.addStepListener(plexe)

    step = 0
    topology = []
    serving_list = []  
    action_list = []
    input_vehs = [0,0,0,0,0]
    while step < 360000:  # *0.01 hour       
        
        traci.simulationStep()
        print(step/100)
        if step % ADD_PLATOON_STEP == 0:  # add new platoon every X steps
            add_platoons(plexe,step) 

        topology = list(traci.vehicle.getIDList())
        c=0
        try:
            for veh in topology:            
                odometry = traci.vehicle.getDistance(veh)
                if (veh not in serving_list) and (JUNC_BOUND-APPROACHING_RGN <= odometry < JUNC_BOUND-DETECTION_RGN): 
                    serving_list.append(veh)
                    plexe.set_cc_desired_speed(veh, 10.0) 

                if (508<odometry) and (veh in serving_list):
                    serving_list.remove(veh)

            for veh in topology:
                odometry = traci.vehicle.getDistance(veh)
                if (JUNC_BOUND - DETECTION_RGN <= odometry <= JUNC_BOUND) :

                    if (veh not in output_list_ids):
                        plexe.set_cc_desired_speed(veh, 0.0)


                    if veh not in action_list and len(action_list) < N:
                        action_list.append(veh)
                    
                    if (veh in output_list_ids) and (veh in action_list):
                        plexe.set_cc_desired_speed(veh, 20.0)

                if (odometry > 506 ) and (veh in action_list):
                    action_list.remove(veh)

                if odometry>JUNC_BOUND and veh not in action_list:
                    plexe.set_cc_desired_speed(veh, 20.0)

                if (JUNC_BOUND < odometry <= 508):
                    c+=1
                
            for veh in serving_list:
                odometry = traci.vehicle.getDistance(veh)
                if JUNC_BOUND - DETECTION_RGN <= odometry + VEHICLE_LENGTH and veh not in serving_list:
                    #c += 1 #block the junction until the vehicle in vincity arrives in for decision making
                    serving_list.append(veh)

                if JUNC_BOUND <= odometry +  VEHICLE_LENGTH/2 and veh in action_list:
                    c += 1 
                    plexe.set_cc_desired_speed(veh,50)

                # if veh in output_list_ids and odometry < 492:  #Centralized condition avoids jamming
                #     c+=1

            if c==0:
                output_list_ids,action_list = intersection_manger(action_list,G)
                if output_list_ids==None:
                    output_list_ids=[0,0,0,0]
                # output_list_ids = [k for k,j in zip(action_list,output_list) if j!=0]
            
            # print(c,output_list_ids,"output",action_list,"Serve",serving_list)
            for veh in output_list_ids:
                if veh!=0:
                    plexe.set_cc_desired_speed(veh, 10.0)
        except traci.exceptions.TraCIException:
            # print(traci.exceptions.TraCIException)
            if veh in serving_list:
                serving_list.remove(veh)
            if veh in output_list_ids:
                output_list_ids.remove(veh)
            if veh in action_list:
                action_list.remove(veh)

        step += 1
        # print(step)
    traci.close()
        
        


if __name__ == "__main__":

    conflict_matrix = {}
    df = pd.read_csv("/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/conflict_matrix_4way_compliment.csv")
    for i in df.columns:
        conflict_matrix[i]=[j for j in df[i] if j!= '0' or j!= 0]

    G = nx.Graph()
    G.add_nodes_from(df.columns)
    # print(G.nodes)
    for i in df.columns:
        for j in df[i]:
            if j != "0":
                G.add_edge(i,j)
    APPROACHING_SPEED = 2
    JUNC_BOUND = 490
    VEHICLE_LENGTH = 4
    DISTANCE = 6  # inter-vehicle distance
    DETECTION_RGN = 5
    APPROACHING_RGN = 20 + DETECTION_RGN
    # LANE_NUM = list(df.columns)
    LANE_NUM = sorted(conflict_matrix.keys())
    SPEED = 16.6  # m/s
    N = 4  #nway junctionN = 4  #nway junction
    TRAFFIC_DENSITY = np.array([0.4,0.4,0.1,0.1])*(int(sys.argv[1])*N/3600) # density in PCU/hr/lane dvide by 3600 to get per second
    ADD_PLATOON_PRO = 0.50
    ADD_PLATOON_STEP = 100 # int(sys.argv[1])
    
    main()
