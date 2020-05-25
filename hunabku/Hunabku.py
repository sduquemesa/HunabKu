from flask import (
    Flask,
    json,
    request
)

from pymongo import MongoClient
import socket
from pandas import DataFrame

from bson import ObjectId
import logging

import os
import glob
import pathlib
import sys, inspect
import importlib

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)



class Hunabku:
    '''
    Class to serve papers information store in a mongodb database throught an API using flask.
    
    example:
    http://0.0.0.0:5000/data/redalyc?init=1&end&apikey=pl0ok9ij8uh7yg
    '''
    def __init__(self,apikey,dburi='mongodb://localhost:27017/', ip='0.0.0.0',port=8080, log_file='hunabku.log', info_level=logging.DEBUG):
        '''
        Contructor to initialize configuration options.
        
        Args:
            apikey: apikey to access the data
            ip (str): ip to start the server 
            port (int): port for the server
            info_level (logging.DEBUG/INFO etc..): enable/disable debug mode with extra messages output.
        '''
        self.dburi        = dburi
        self.dbclient     = MongoClient(dburi)
        self.ip = ip
        self.port = port
        self.info_level = info_level
        self.apikey = apikey
        self.plugins = {}
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.set_info_level(info_level)
        self.app = Flask('hanubku', template_folder='templates')
        self.load_plugins()

    def set_info_level(self, info_level):
        '''
        Information level for debug or verbosity of the application (https://docs.python.org/3.1/library/logging.html)
        '''
        if info_level != logging.DEBUG:
            logging.basicConfig(filename=self.log_file, level=info_level)
        self.info_level = info_level

    def load_plugins(self):
        '''
        This method return the plugins found in the folder plugins.
        '''
        self.logger.warning('-----------------------')
        self.logger.warning('------ Loagind Plugins:')
        for path in glob.glob(str(pathlib.Path(__file__).parent.absolute())+"/plugins/*.py"):
            name = path.split(os.path.sep)[-1].replace('.py','') 
            print('------ Loading plugin: '+name)
            spec = importlib.util.spec_from_file_location(name,path)
            module = spec.loader.load_module()
            plugin_class = getattr(module, name)
            instance = plugin_class(self)
            instance.register_endpoints()
            self.plugins['name'] = name
            self.plugins['path'] = path
            self.plugins['spec'] = spec
            self.plugins['instance'] = instance

    def start(self):
        '''
        Method to start server
        '''
        self.app.run(host=self.ip, port=self.port, debug=True)
