
from pymongo import MongoClient
import pprint
import xmltodict
import json
with open('main.xml') as f:
    data_dict = xmltodict.parse(f.read());

json_data = json.dumps(data_dict)
with open('xml.json','w') as jsonfile:
    jsonfile.write(json_data)
    pprint.pprint(json_data)

