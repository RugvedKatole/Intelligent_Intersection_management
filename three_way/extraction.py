#from typing import final
import bs4
from bs4 import BeautifulSoup as bs
import statistics
def get_time(path):
    content = []
    # Read the XML file
    with open("/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/three_way/{}".format(path), "r") as file:
        # Read each line in the file, readlines() returns a list of lines
        content = file.read()
        # Combine the lines in the list into a string
        content = "".join(content)
        bs_content = bs(content, "lxml")

    result = list(bs_content.find_all("tripinfo"))
    #print(result)
    #waiting_time = bs_content.find("tripinfo")
    #print(result)
    final_waiting={"a":[],"b":[],"c":[]}
    avg ={}
    var =[]
    c=0
    b=0
    for i in result:
        if i["vaporized"] == "":
            final_waiting[i["id"].split(".")[1].split("_")[0]].append(i['waitingtime'])
            # fop= i['waitingtime']
            # final_waiting.append(float(fop))
            b+=1
        else:
            print(i["vaporized"])
            c+=1

    for i in final_waiting.keys():
        final_waiting[i] = map(float,final_waiting[i])
        avg[i]=statistics.mean(final_waiting[i])
        # var=statistics.mean(list(avg.items()))
        # var.append(statistics.variance(final_waiting[i]))
    
    vaporised = c
    total = c+b
    return avg, var, vaporised, total, c/total

if __name__ == "__main__":
    print(get_time('Results/250_three_way.xml'))