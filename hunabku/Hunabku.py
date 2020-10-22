from flask import (
    Flask
)

from pymongo import MongoClient

import logging

import os
from shutil import rmtree
import subprocess
import glob
import time
import pathlib
import sys
import importlib


class Hunabku:
    """
    Class to serve papers information store in a mongodb database throught an API using flask.

    example:
    http://0.0.0.0:5000/data/redalyc?init=1&end&apikey=pl0ok9ij8uh7yg
    """

    def __init__(
            self,
            apikey,
            dburi='mongodb://localhost:27017/',
            ip='127.0.0.1',
            port=8080,
            log_file='hunabku.log',
            info_level=logging.DEBUG):
        """
        Contructor to initialize configuration options.

        Args:
            apikey: apikey to access the data
            ip (str): ip to start the server
            port (int): port for the server
            info_level (logging.DEBUG/INFO etc..): enable/disable debug mode with extra messages output.
        """
        self.dburi = dburi
        self.dbclient = MongoClient(dburi)
        self.ip = ip
        self.port = port
        self.info_level = info_level
        self.apikey = apikey
        self.apidoc_dir = 'apidoc'
        self.plugins = []
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.set_info_level(info_level)
        self.app = Flask(
            'hanubku',
            static_folder='static',
            static_url_path='/',
            template_folder='templates')
        self.load_plugins()
        self.generate_doc()

    def set_info_level(self, info_level):
        """
        Information level for debug or verbosity of the application (https://docs.python.org/3.1/library/logging.html)
        """
        if info_level != logging.DEBUG:
            logging.basicConfig(filename=self.log_file, level=info_level)
        self.info_level = info_level

    def load_plugins(self):
        """
        This method return the plugins found in the folder plugins.
        """
        self.logger.warning('-----------------------')
        self.logger.warning('------ Loagind Plugins:')
        for path in glob.glob(
                str(pathlib.Path(__file__).parent.absolute()) + "/plugins/*.py"):
            name = path.split(os.path.sep)[-1].replace('.py', '')
            print('------ Loading plugin: ' + name)
            spec = importlib.util.spec_from_file_location(name, path)
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

    def check_apidoc_syntax(self, plugin_file):
        """
        Allows to check in the syntaxis in the docstring comment is right
        for apidoc  files generation.
        The the syntax is wrong, the Hunabku server can not start.
        """
        process = subprocess.run(['apidoc',
                                  '-c',
                                  'etc/',
                                  '--simulate',
                                  '-f',
                                  plugin_file],
                                 stdout=subprocess.PIPE)
        if process.returncode != 0:
            self.logger.error('------ERROR: parsing docstring for apidocs in plugin ' + plugin_file)
            self.logger.error('             server can not start until apidocs syntax is fixed')
            sys.exit(1)

    def generate_doc(self, timeout=1, maxtries=5):
        """
        this method allows to generated apidocs documentation parsing plugin files
        """
        self.logger.warning('-----------------------')
        self.logger.warning('------ Creating documentation')
        self.logger.warning(
            '------ Apidocs at http://{}:{}/apidoc/index.html'.format(self.ip, self.port))

        try:
            os.mkdir('static')
            print(" * Static Directory ", self.apidoc_dir, " created ")
        except FileExistsError:
            # Is this is happening then restart the microservices in the folder
            print(
                " * Warning! Static Directory ",
                self.apidoc_dir,
                " already exists")

        rmtree('static/' + self.apidoc_dir, ignore_errors=True)
        args = ['apidoc', '-c', 'etc']

        for plugin in self.plugins:
            self.check_apidoc_syntax(plugin['path'])
            args.append('-f')
            args.append(plugin['path'])
        args.append('-o')
        args.append('static/' + self.apidoc_dir)
        process = subprocess.Popen(args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        counter = 0
        while process.poll() is None:
            time.sleep(timeout)
            counter = counter + 1
            if counter == maxtries:
                process.kill()
                break

    def start(self):
        """
        Method to start server
        """
        self.app.run(host=self.ip, port=self.port, debug=True)
