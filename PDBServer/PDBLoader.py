from __future__ import print_function
import sys
from pymongo import MongoClient        
import pandas as pd
import numpy as np


class PDBLoader:
    def __init__(self,filename,dbname,dbcollection,dburi='mongodb://localhost:27017/',dbdrop=True):
        if filename is None:
            print("Error: file is not provided!",file=sys.stderr)
            sys.exit(1)
        self.dbname   = dbname
        self.dbcollection = dbcollection
        self.dbclient = MongoClient(dburi)
        self.db       = self.dbclient[self.dbname]
        if dbdrop:
            self.dbclient.drop_database(dbname)
        
        if filename[len(filename)-4:len(filename)].lower() == ".csv":
            data = pd.read_csv(filename)
            data["_id"]=np.arange(data.shape[0])
            print(data["_id"])
            data = data.to_dict(orient = 'records')
            self.db[self.dbcollection].insert_many(data)
        else:
            print("file format "+filename[len(filename)-4:len(filename)].lower()+" not supported", file=sys.stderr)
            sys.exit(1) 
