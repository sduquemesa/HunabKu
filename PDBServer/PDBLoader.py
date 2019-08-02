from __future__ import print_function
import sys
from pymongo import MongoClient        
import pandas as pd
import numpy as np


class PDBLoader:
    def __init__(self,dbname='colav',dburi='mongodb://localhost:27017/',dbdrop=True):
        self.dbname   = dbname
        self.dbclient = MongoClient(dburi)
        self.db       = self.dbclient[self.dbname]
        if dbdrop:
            self.dbclient.drop_database(dbname)
        
    def load(self,filename,dbcollection):    
        if filename is None:
            print("Error: file is not provided!",file=sys.stderr)
            sys.exit(1)
            
        if filename[len(filename)-4:len(filename)].lower() == ".csv":
            data = pd.read_csv(filename)
            data["_id"]=np.arange(data.shape[0])
            print(data["_id"])
            data = data.to_dict(orient = 'records')
            self.db[dbcollection].insert_many(data)
        elif filename[len(filename)-5:len(filename)].lower() == ".json":
            data = pd.read_csv(filename)
            data["_id"]=np.arange(data.shape[0])
            print(data["_id"])
            data = data.to_dict(orient = 'records')
            self.db[dbcollection].insert_many(data)
        elif filename[len(filename)-5:len(filename)].lower() == ".xlsx":
            data = pd.read_excel(filename)
            data["_id"]=np.arange(data.shape[0])
            print(data["_id"])
            data = data.to_dict(orient = 'records')
            self.db[dbcollection].insert_many(data)
        else:
            print("file format "+filename[len(filename)-4:len(filename)].lower()+" not supported", file=sys.stderr)
            sys.exit(1) 
