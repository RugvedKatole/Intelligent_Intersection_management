#from typing import final
import bs4
from bs4 import BeautifulSoup as bs
import statistics
def get_time():
    content = []
    # Read the XML file
    with open("/home/arms04/autonomous_driving_stack/Intelligent_Intersection_management/three_way/SUMO_CFG/my_output_file.xml", "r") as file:
        # Read each line in the file, readlines() returns a list of lines
        content = file.read()
        # Combine the lines in the list into a string
        content = "".join(content)
        bs_content = bs(content, "lxml")

    result = list(bs_content.find_all("tripinfo"))
    #print(result)
    #waiting_time = bs_content.find("tripinfo")
    #print(result)
    final=[]
    c=0
    for i in result:
        if i["vaporized"] == "":
            fop= i['waitingtime']
            final.append(float(fop))
        else:
            print(i["vaporized"])
            c+=1
    avg = statistics.mean(final)
    var = statistics.variance(final)
    vaporised = c
    total = c+len(final)
    return avg, var, vaporised, total, c/total
