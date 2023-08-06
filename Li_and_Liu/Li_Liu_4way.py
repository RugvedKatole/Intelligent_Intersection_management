#!/usr/bin/env python

import os
import sys
from math import sqrt
import numpy as np
import random
from utils import communicate

#路径
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
from plexe import Plexe, ACC, CACC
import pandas as pd


def add_single_platoon(plexe, topology, step, lane):
    for i in range(PLATOON_SIZE):
        vid = "v%d.%s" %(step/ADD_PLATOON_STEP, lane)
        routeID = lane   # route 0~11, one-to-one map with lane
        traci.vehicle.add(vid, routeID, typeID="vtypeauto")        
        plexe.set_path_cacc_parameters(vid, DISTANCE, 2, 1, 0.5)
        plexe.set_cc_desired_speed(vid, SPEED)
        plexe.set_acc_headway_time(vid, 1.5)
        plexe.use_controller_acceleration(vid, False)
        plexe.set_fixed_lane(vid, lane, False)
        traci.vehicle.setSpeedMode(vid, 0)
        if i == 0:
            plexe.set_active_controller(vid, ACC)
            traci.vehicle.setColor(vid, (255,255,255,255))  # red
            topology[vid] = {}
        else:
            plexe.set_active_controller(vid, CACC)
            traci.vehicle.setColor(vid, (200,200,0, 255)) # yellow
            topology[vid] = {"front": "v%d.%s" %(step/ADD_PLATOON_STEP, lane), "leader": "v%d.%s" %(step/ADD_PLATOON_STEP, lane)}



def add_platoons(plexe, topology, step):
    spawn_vehs = np.random.poisson(TRAFFIC_DENSITY*N)
    Manuevers = random.sample(LANE_NUM,spawn_vehs)
    for lane in Manuevers:
        add_single_platoon(plexe, topology, step, lane)


def compute_leaving_time(veh):
    distance = 400 + PLATOON_LENGTH + STOP_LINE - traci.vehicle.getDistance(veh)
    speed = traci.vehicle.getSpeed(veh) + 0.00001
    return distance*1.0/speed



def main():
    sumo_cmd = ['sumo', '--duration-log.statistics', '--tripinfo-output', '{}/{}'.format(directory,sys.argv[2]),
                 '-c', '{}/cfg/my_confg.sumo.cfg'.format(directory)]
    traci.start(sumo_cmd)
    # 每次traci.simulationStep()之后都调用一次plexe 
    plexe = Plexe()
    traci.addStepListener(plexe)

    step = 0
    topology = {}
    serving_list = []  # each element: [veh, route, leaving_time, priority]
    serving_list_veh_only = []  # each element: veh

    while step < 360000:  # 1 hour       
        
        traci.simulationStep()

        if step % ADD_PLATOON_STEP == 0:  # add new platoon every X steps
            add_platoons(plexe, topology, step) 
        

        # check all leaders to decide whether add to serving list or delete from topology
        deleted_veh = []
        try:
            for key, value in list(topology.items()):            
                if value == {}:  # if it is a leader
                    odometry = traci.vehicle.getDistance(key)
                    # for the first time V2I communication
                    if (not key in serving_list_veh_only) and (400-V2I_RANGE <= odometry < 400-V2I_RANGE+100): 
                        # add to serving list and initialize by simply setting leaving_time=0, priority=1.
                        serving_list.append([key, key.split(".")[1], 0, 1])
                        serving_list_veh_only.append(key)
                    # record the platoon which has almost finished the route
                    if odometry > 800:
                        deleted_veh.append(key)     

            # delete the platoon which has almost finished the route
            for veh in deleted_veh:
                veh_time = veh.split(".")[0]
                veh_route = veh.split(".")[1]
                for i in range(PLATOON_SIZE):                
                    veh_id = veh_time + "." + veh_route
                    del topology[veh_id]
                

            # delete vehcles from the list which has already passed the intersection
            serving_list[:] = [element for element in serving_list if traci.vehicle.getDistance(element[0]) < 400 + PLATOON_LENGTH + STOP_LINE]  
            serving_list_veh_only = [element[0] for element in serving_list]  

            
            # update leaving_time for priority 0 and update speed for priority 1
            for i in range(len(serving_list)):  # serving_list element = [veh, route, leaving_time, priority]
                veh_i = serving_list[i][0]  # veh_ID = "v.time.route.num"
                route_i = veh_i.split(".")[1]
                priority = serving_list[i][3]
                if priority == 0: # for priority=0, only need to update leaving_time
                    serving_list[i][2] = compute_leaving_time(veh_i)                
                else:
                    # find the max leaving time in conflict routes  
                    # initialize the time by a small value 
                    max_leaving_time = 0.00001            
                    for j in range(i):
                        veh_j = serving_list[j][0]
                        route_j = veh_j.split(".")[1]
                        leaving_time_j = serving_list[j][2]
                        if (route_j in conflict_matrix[route_i]) and (leaving_time_j > max_leaving_time):
                            max_leaving_time = leaving_time_j

                    # if no conflict any more, reset the veh to run as expected.
                    if max_leaving_time == 0.00001:
                        serving_list[i][3] = 0
                        distance = 400 + PLATOON_LENGTH + STOP_LINE - traci.vehicle.getDistance(veh_i)
                        desired_speed = sqrt(2 * MAX_ACCEL * distance + (traci.vehicle.getSpeed(veh_i))**2)
                        plexe.set_cc_desired_speed(veh_i, desired_speed)
                        serving_list[i][2] = (desired_speed - traci.vehicle.getSpeed(veh_i)) / MAX_ACCEL
                        #serving_list[i][2] = compute_leaving_time(veh_i)
                    # otherwise, adjust the speed to make sure the veh arrives after max_leaving_time
                    else:
                        distance_to_stop_line = 400 - STOP_LINE - traci.vehicle.getDistance(veh_i)
                        # print("max_leaving_time: ", max_leaving_time)
                        # print("distance_to_stop_line: ", distance_to_stop_line)
                        current_speed = traci.vehicle.getSpeed(veh_i) + 0.00001  # add a small number to avoid division by zero
                        decel = 2 * (current_speed * max_leaving_time - distance_to_stop_line)/(max_leaving_time **2)
                        desired_speed = current_speed - decel * max_leaving_time
                        #desired_speed = (distance_to_stop_line) / max_leaving_time
                        plexe.set_cc_desired_speed(veh_i, desired_speed)
                        serving_list[i][2] = (distance_to_stop_line + PLATOON_LENGTH + 2*STOP_LINE)/current_speed
                        """
                        traci.vehicle.getSpeed(veh_i) + 0.00001  # add a small number to avoid division by zero
                        arrive_time = distance_to_stop_line / speed
                        if arrive_time < max_leaving_time:
                            desired_speed = speed * distance_to_stop_line/(V2I_RANGE-STOP_LINE)
                            if speed - desired_speed > DECEL * 0.01:
                                desired_speed = speed - DECEL * 0.01
                            traci.vehicle.slowDown(veh_i, desired_speed, 0.01)
                            #traci.vehicle.setSpeed(veh_i, desired_speed)
                        elif arrive_time > max_leaving_time + 0.5:
                            #desired_speed = speed + DECEL*0.01
                            #if desired_speed > SPEED:
                            #    desired_speed = SPEED
                            #traci.vehicle.slowDown(veh_i, desired_speed, 0.01) 
                            reset_veh(plexe, veh_i)
                            #traci.vehicle.setSpeed(veh_i, desired_speed)                   
                        serving_list[i][2] = (distance_to_stop_line + PLATOON_LENGTH + 2*STOP_LINE)*1.0/speed
                        """

            if step % 10 == 1:
                # simulate vehicle communication every 0.1s
                communicate(plexe, topology)
        except traci.exceptions.TraCIException as e:
            print(e)
            if key in serving_list:
                serving_list.remove(key)
            if key in topology.keys():
                del topology[key]
            if key not in deleted_veh:
                deleted_veh.append(key)
            # traci.close()
        step += 1


    traci.close()


if __name__ == "__main__":
    directory = "/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Li_and_Liu"
    conflict_matrix = {}
    df = pd.read_csv("{}/conflict_matrix_4way.csv".format(directory))
    for i in df.columns:
        conflict_matrix[i]=[j for j in df[i] if j!= '0' or j!= 0]
    # print(conflict_matrix)
    # conflict_matrix = {
    # 0:[], 
    # 1:[4, 8, 10, 11], 
    # 2:[4, 5, 7, 11], 
    # 3:[], 
    # 4:[1, 2, 7, 11], 
    # 5:[2, 7, 8, 10],
    # 6:[],
    # 7:[2, 4, 5, 10],
    # 8:[1, 5, 10, 11],
    # 9:[],
    # 10:[1, 5, 7, 8],
    # 11:[1, 2, 4, 8]
    # }
    VEHICLE_LENGTH = 4
    DISTANCE = 6  # inter-vehicle distance
    LANE_NUM = conflict_matrix.keys()
    PLATOON_SIZE = 1
    SPEED = 16.6  # m/s
    V2I_RANGE = 200 
    PLATOON_LENGTH = VEHICLE_LENGTH * PLATOON_SIZE + DISTANCE * (PLATOON_SIZE - 1)
    TRAFFIC_DENSITY = int(sys.argv[1])/3600
    ADD_PLATOON_PRO = 0.25  
    ADD_PLATOON_STEP = 300
    MAX_ACCEL = 2.6
    #DECEL = SPEED**2/(2*(V2I_RANGE-25))  
    #DECEL = 3.5
    STOP_LINE = 20.0
    N=4
    main()
