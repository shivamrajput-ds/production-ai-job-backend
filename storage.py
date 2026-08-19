import json

def load_data():
    with open ("data.json","r") as file:
        data = json.load(file)
    return data  

def dump_data(data):
    with open("data.json","w") as file:
        json.dump(data,file) 