from flask import (
    Flask,
    json,
    request,
    render_template,
    send_from_directory
)

from pymongo import MongoClient
import socket
from pandas import DataFrame

from bson import ObjectId
import logging

import os
from shutil import rmtree
import subprocess
import glob
import time
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
        self.apidoc_dir = 'apidoc'
        self.plugins = []
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.set_info_level(info_level)
        self.app = Flask('hanubku', static_folder='static',static_url_path='/',template_folder='templates')
        self.load_plugins()
        self.generate_doc()
    

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
            plugin = {}
            plugin['name'] = name
            plugin['path'] = path
            plugin['spec'] = spec
            plugin['instance'] = instance
            self.plugins.append(plugin)

    def generate_doc(self,timeout=1,maxtries=5):
        '''
        this method allows to generated apidocs documentation parsing plugin files
        '''
        self.logger.warning('-----------------------')
        self.logger.warning('------ Creating documentation')
        self.logger.warning('------ Apidocs at http://{}:{}/apidoc/index.html'.format(self.ip,self.port))

        try:
            os.mkdir('static')
            print(" * Static Directory " , self.apidoc_dir ,  " created ") 
        except FileExistsError:
            #Is this is happening then restart the microservices in the folder
            print(" * Warning! Static Directory " , self.apidoc_dir ,  " already exists")

        rmtree('static/'+self.apidoc_dir)
        args=['apidoc']
        for plugin in self.plugins:
            args.append('-f')
            args.append(plugin['path'])
        args.append('-o')
        args.append('static/'+self.apidoc_dir)
        process = subprocess.Popen(args, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
        counter=0
        while process.poll() is None:
            time.sleep(timeout)
            counter = counter+1
            if counter == maxtries:
                process.kill()
                break



    def start(self):
        '''
        Method to start server
        '''
        self.app.run(host=self.ip, port=self.port, debug=True)
