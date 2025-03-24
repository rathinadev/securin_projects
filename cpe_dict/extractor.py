
from pymongo import MongoClient
import xmltodict
import json
with open('lavanya.xml') as f:
    data_dict = xmltodict.parse(f.read());

json_data = json.dumps(data_dict)
with open('drone.json','w') as jsonfile:
    jsonfile.write(json_data)
    
for i in range(5):
    print(json_data[i])



