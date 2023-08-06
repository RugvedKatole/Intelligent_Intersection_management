import networkx as nx
import pandas as pd
conflict_matrix = {}
df = pd.read_csv("/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/Four_way/conflict_matrix_4way_compliment.csv")
for i in df.columns:
    conflict_matrix[i]=[j for j in df[i] if j!= '0' or j!= 0]

G = nx.Graph()
G.add_nodes_from(df.columns)
print(G.nodes)
for i in df.columns:
    for j in df[i]:
        if j != "0":
            G.add_edge(i,j)

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
    print(sorted(list(nx.find_cliques(Gs)),key=len,reverse=True))
    output_list = sorted(sorted(list(nx.find_cliques(Gs)),key=len,reverse=True),key=lambda clique: sorted(clique,key=lambda man: man.split("_")[0]))
    # for i in range(len(output_list)):
    #     output_list[i] = sorted(output_list[i],key=lambda student: student.split("_")[0])
    #     output_list[i] = [".".join([incoming[j],j]) for j in output_list[i]]
    output_list = [".".join([incoming[j],j]) for j in output_list[0]]
    return output_list, input_vehs

# intersection_manger(['v1264.a_3', 'v1260.b_2', 'v1262.c_3', 'v1263.d_2'],G)
print(intersection_manger(['v191.b_3', 'v191.c_2'],G))