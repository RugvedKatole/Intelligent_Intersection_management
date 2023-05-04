import pandas as pd
conflict_matrix = {}
df = pd.read_csv("/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/conflict_matrix_4way.csv")
for i in df.columns:
    conflict_matrix[i]=[j for j in df[i] if j!= '0' or j!= 0]

def intersect(A: list, B:list):
    """ intersects two lists"""
    return [i if i ==j else 0 for i,j in zip(A,B)]

def remove_conflicts(output_list,conflict_matrix):
    cand_list = {}
    least_count = len(output_list) + 1
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
    return cand_list, frze_var

def intersection_manger(input_vehs,conflict_matrix):
    """THE ACTUAL ALGORITHM"""
    input_vehs= [".".join([i.split(".")[1],i.split(".")[0]]) for i in input_vehs]
    input_vehs = sorted(input_vehs)
    input_vehs = [".".join([i.split(".")[1],i.split(".")[0]]) for i in input_vehs]
    input = [i.split(".")[-1] if i != 0 else 0 for i in input_vehs]
    output_list = input
    cand_list = {}
    least_count = len(input) + 1
    interim_lst =[]
    #######################################################
    # Creates a list without conflicts 
    #######################################################
    cand_list , frze_var = remove_conflicts(output_list,conflict_matrix)
    #######################################################
    if least_count == len(input)-1:
        output_list = cand_list[frze_var]
        output_list = [k for k,j in zip(input_vehs,cand_list[frze_var]) if j!=0]
    else:
        least_count = len(input) + 1
    try:
        for j in cand_list[frze_var]:
            if j!= 0:
                for i in cand_list[frze_var]:
                    if i != j and i != 0:
                        interim = intersect(cand_list[i],cand_list[j])
                        if interim.count(0) <= least_count:
                            least_count = interim.count(0)
                            output_list = [k for k,j in zip(input_vehs,interim) if j!=0]
        for j in cand_list[frze_var]:
            if j!= 0:
                for i in cand_list[frze_var]:
                    if i != j and i != 0:
                        interim = intersect(cand_list[i],cand_list[j])
                        if interim.count(0) == least_count:
                            interim_lst.append(interim)
        if len(interim_lst) != 0:
            for i in range(len(interim_lst)):
                interim_lst[i] = [k for k,j in zip(input_vehs,interim_lst[i]) if j!=0]
            interim_lst = [sorted(i) for i in interim_lst]
            print(sorted(interim_lst))
            output_list = sorted(interim_lst)[0]
    except UnboundLocalError:
        pass
    return output_list, input_vehs

O,I = intersection_manger(['   '],conflict_matrix)

print(O)