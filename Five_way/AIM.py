#!usr/bin/env python3
#!/usr/bin/env python

#5-way

import os
import sys
from math import sqrt
import time
import pandas as pd
import random
#from utils import communicate


from itertools import product
#
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
from plexe import Plexe, ACC

def add_single_platoon(plexe, step, lane):
    vid = "v%d.%s" %(step/ADD_PLATOON_STEP, lane)
    routeID = lane   # route 0~11, one-to-one map with lane
    traci.vehicle.add(vid, routeID, typeID="vtypeauto")        
    plexe.set_path_cacc_parameters(vid, DISTANCE, 2, 1, 0.5)
    # plexe.set_cc_desired_speed(vid, random.randint(4,10))
    plexe.set_cc_desired_speed(vid, 10)
    plexe.set_acc_headway_time(vid, 1.5)
    plexe.use_controller_acceleration(vid, False)
    plexe.set_fixed_lane(vid, lane, False) #changed code for plexe because no lanes exits in our case change plexe_sumo_exlipse.py line 116
    traci.vehicle.setSpeedMode(vid, 0)
    plexe.set_active_controller(vid, ACC)


def add_platoons(plexe,step):
    for lane in LANE_NUM:    # lane 0~11
        if random.random() < ADD_PLATOON_PRO:
            add_single_platoon(plexe,step, lane)

def intersect(A: list, B:list):
    """ intersects two lists"""
    return [i if i ==j else 0 for i,j in zip(A,B)]

def intersection_manger(input_vehs,conflict_matrix):
    """THE ACTUAL ALGORITHM"""
    input = [i.split(".")[-1] if i != 0 else 0 for i in input_vehs]
    output_list = input
    cand_list = {}
    least_count = len(input) + 1
    for i in output_list:
        temp = []
        for j in output_list:
            if i==0:
                temp.append(0)
            elif j not in conflict_matrix[i]:
                temp.append(j)
            else:
                temp.append(0)
        cand_list[i] = temp
        count = temp.count(0)
        if count < least_count:
            frze_var = i
            least_count = count
    
    if least_count == len(input)-1:
        output_list = cand_list[frze_var]
    else:
        least_count = len(input) + 1
    try:
        for j in cand_list[frze_var]:
            if j!= 0:
                for i in cand_list[frze_var]:
                    if i != j and i != 0:
                        interim = intersect(cand_list[i],cand_list[j])
                        if interim.count(0) < least_count:
                            least_count = interim.count(0)
                            output_list = interim
    except UnboundLocalError:
        # print("OUTPUT_IM")
        pass
    return output_list

# def Get_first_veh(id_list):


def main():
    
    sumo_cmd = ['sumo', '--duration-log.statistics', '--tripinfo-output', '/home/arms04/autonomous_driving_stack/Sushant_MTP/sushant_MTP/Practice/five_way/my_output_file.xml', '-c', '/home/arms04/autonomous_driving_stack/Sushant_MTP/sushant_MTP/Practice/five_way/my_confg.sumo.cfg']
    
    traci.start(sumo_cmd)
    plexe = Plexe()
    traci.addStepListener(plexe)

    step = 0
    topology = []
    serving_list = []  
    action_list = []
    input_vehs =[0,0,0,0,0]
    while step < 100000:  # 1 hour       
        
        traci.simulationStep()

        if step % ADD_PLATOON_STEP == 0:  # add new platoon every X steps
            add_platoons(plexe,step) 

        topology = list(traci.vehicle.getIDList())
        c=0
        try:
            for veh in topology:            
                odometry = traci.vehicle.getDistance(veh)
                if (veh not in serving_list) and (492-30 <= odometry < 492-6): 
                    serving_list.append(veh)
                    plexe.set_cc_desired_speed(veh, 0.0) 
                # if (veh in serving_list) and (492-10 <= odometry < 492-6):
                #     traci.vehicle.setSpeed(veh, 1.0)  
                if (508<odometry) and (veh in serving_list):
                    serving_list.remove(veh)

            #serving_list[:] = [element for element in serving_list if element in topology]
            for veh in topology:
                odometry = traci.vehicle.getDistance(veh)
                if (492 - 6 <= odometry <= 492) :

                    if (veh not in output_list_ids):
                        plexe.set_cc_desired_speed(veh, 0.0)


                    if veh not in action_list:
                        action_list.append(veh)
                    
                    if (veh in output_list_ids) and (veh in action_list):
                        plexe.set_cc_desired_speed(veh, 10.0)

                if (odometry > 492 ) and (veh in action_list):
                    action_list.remove(veh)

                if odometry>492 and veh not in action_list:
                    plexe.set_cc_desired_speed(veh, 10.0)

                if (492 < odometry <= 508):
                    #plexe.set_cc_desired_speed(veh,10.0)
                    c+=1
            # print(action_list)
            

            if c==0:
                #output_list_ids = [0, 0, 0, 0]
                output_list = intersection_manger(action_list,conflict_matrix)
                if output_list==None:
                    output_list=[0,0,0,0]
                output_list_ids = [k for k,j in zip(action_list,output_list) if j!=0]

            # print('output_list_ids',output_list_ids)
            # print(c)

            for veh in output_list_ids:
                if veh!=0:
                    plexe.set_cc_desired_speed(veh, 10.0)
                    # print(veh,traci.vehicle.getSpeed(veh))
            #         if traci.vehicle.getSpeed(veh) == 0 and traci.vehicle.getDistance(veh) > 487.5:
            #             traci.vehicle.remove(veh)
            #             if veh in output_list_ids:
            #                 output_list_ids.remove(veh)
            #             if veh in action_list:
            #                 action_list.remove(veh)
            #             if veh in serving_list:
            #                 serving_list.remove(veh)
            # for veh in action_list:
            #     if traci.vehicle.getSpeed(veh) == 0 and traci.vehicle.getDistance(veh) > 487.5:
            #         traci.vehicle.remove(veh)
            #         if veh in output_list_ids:
            #             output_list_ids.remove(veh)
            #         if veh in action_list:
            #             action_list.remove(veh)
            #         if veh in serving_list:
            #             serving_list.remove(veh)
        except traci.exceptions.TraCIException:
            # print(traci.exceptions.TraCIException)
            if veh in serving_list:
                serving_list.remove(veh)
            if veh in output_list_ids:
                output_list_ids.remove(veh)
            if veh in action_list:
                action_list.remove(veh)

        step += 1
        print(step)
    traci.close()
        
        


if __name__ == "__main__":

    conflict_matrix = {}
    df = pd.read_csv("/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Five_way/conflict_matrix_5way.csv")
    for i in df.columns:
        conflict_matrix[i]=[j for j in df[i] if j!= ' ']
    APPROACHING_SPEED = 2
    # VEHICLE_LENGTH = 4
    DISTANCE = 6  # inter-vehicle distance
    DETECTION_RGN = 5
    APPROACHING_RGN = 20 + DETECTION_RGN
    LANE_NUM = list(df.columns)
    SPEED = 16.6  # m/s
    ADD_PLATOON_PRO = 0.2
    ADD_PLATOON_STEP = int(sys.argv[1])
    N = 5 #nway junction
    main()
