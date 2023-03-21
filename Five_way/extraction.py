#from typing import final
import bs4
from bs4 import BeautifulSoup as bs
import statistics
def get_time():
    content = []
    # Read the XML file
    with open("/home/arms04/autonomous_driving_stack/Sushant_MTP/sushant_MTP/Practice/five_way/my_output_file.xml", "r") as file:
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
    for i in result:
        if i["vaporized"] == "":
            fop= i['waitingtime']
            final.append(float(fop))
        else:
            print(i["vaporized"])
        #print(fop)
    avg = statistics.mean(final)
    var = statistics.variance(final)
    return avg, var

print(get_time())

