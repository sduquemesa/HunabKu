from __future__ import print_function
import sys
from configparser import ConfigParser
from pymongo import MongoClient        
import pandas as pd


try:
    from .csv2json import csv2json
except (SystemError, ImportError):
    from csv2json import csv2json

class PDBLoader:
    def __init__(self,filename,dbname,dbcollection,dburi='mongodb://localhost:27017/'):
        if filename is None:
            print("Error: file is not provided!",file=sys.stderr)
            sys.exit(1)
        self.dbname   = dbname
        self.dbcollection = dbcollection
        self.dbclient = MongoClient(dburi)
        self.db       = self.dbclient[self.dbname]
        
        if filename[len(filename)-4:len(filename)].lower() == ".csv":
            data=pd.read_csv(filename).to_dict(orient = 'records')
            self.db[self.dbcollection].insert_many(data)
        else:
            print("file format "+filename[len(filename)-4:len(filename)].lower()+" not supported", file=sys.stderr)
            sys.exit(1) 
