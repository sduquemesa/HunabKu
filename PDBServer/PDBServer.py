from flask import (
    Flask,
    json,
    request
)

from pymongo import MongoClient
import socket
from pandas import DataFrame

app = Flask(__name__, template_folder="templates")


class PDBServer:
    '''
    Class to serve papers information store in a mongodb database throught an API using flask.
    
    example:
    http://0.0.0.0:5000/data/redalyc?init=1&end&apikey=pl0ok9ij8uh7yg
    '''
    def __init__(self,dbname,dbapikey="colavudea",dburi='mongodb://localhost:27017/', ip='0.0.0.0',port=5000,debug=True):
        '''
        Contructor to initialize configuration options.
        
        Args:
            ip (str): ip to start the server 
            port (int): port for the server
            debug (bool): enable/disable debug mode with extra messages output.
        '''
        self.dbname       = dbname
        self.dbclient     = MongoClient(dburi)
        self.db           = self.dbclient[self.dbname]
        self.ip = ip
        self.port = port
        self.debug = debug

        # Create the application endpoints
        @app.route('/data/redalyc',methods = ['GET'])
        def data_redalyc():
            """

            :return:        json with data 
            """
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['data_redalyc'].find({"_id": {"$gte": int(init),"$lte":int(end)}})
                print(cursor)
                data=[]
                for i in cursor:
                    data.append(i)
                    print(data)
                response = app.response_class(
                    response=json.dumps(data),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({"error":"invalid apikey"}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            
        @app.route('/stage/redalyc/submit',methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_redalyc():
            """

            :return:        json with data 
            """
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                self.db['stage_redalyc'].insert(json.loads(data))
                response = app.response_class(
                    response=json.dumps({}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({"error":"invalid apikey"}),
                    status=200,
                    mimetype='application/json'
                )
                return response

        @app.route('/stage/redalyc/read',methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_redalyc_read():
            '''
            write something meanful here
            '''
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['stage_redalyc'].find({"_id": {"$gte": int(init),"$lte":int(end)}})
                data=[]
                for i in cursor:
                    data.append(i)
                response = app.response_class(
                    response=json.dumps(data),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({"error":"invalid apikey"}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            
        @app.route('/stage/redalyc/cites/read',methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_redalyc_cites_read():
            '''
            write something meanful here
            '''
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['stage_cites_redalyc'].find({"_id": {"$gte": int(init),"$lte":int(end)}})
                data=[]
                for i in cursor:
                    data.append(i)
                response = app.response_class(
                    response=json.dumps(data),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({"error":"invalid apikey"}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
    
        @app.route('/stage/redalyc/cites/submit',methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_cites_redalyc():
            """

            :return:        json with data 
            """
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                self.db['stage_cites_redalyc'].insert(json.loads(data))
                response = app.response_class(
                    response=json.dumps({}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({"error":"invalid apikey"}),
                    status=200,
                    mimetype='application/json'
                )
                return response

        @app.route('/stage/redalyc/checkpoint',methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_checkpoint_redalyc():
            """

            :return:        json with data 
            """
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                count = self.db['stage_redalyc'].find({}).sort([('_id', -1)]).limit(1) #fixed this, is the last id not the number of entries
                count = list(count)
                if len(count) != 0:
                    #for i in cursor:
                    #count = self.db['stage_redalyc'].find().count()
                    response = app.response_class(
                        response=json.dumps({"checkpoint":count[0]['_id']}),
                        status=200,
                        mimetype='application/json'
                    )
                else:
                    response = app.response_class(
                        response=json.dumps({"checkpoint":0}),
                        status=200,
                        mimetype='application/json'
                    )

                return response    
            else:
                response = app.response_class(
                    response=json.dumps({"error":"invalid apikey"}),
                    status=200,
                    mimetype='application/json'
                )
                return response

        @app.route('/stage/redalyc/cites/checkpoint',methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_checkpoint_cites_redalyc():
            """

            :return:        json with data 
            """
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                count = self.db['stage_cites_redalyc'].find({}).sort([('_id', -1)]).limit(1) #fixed this, is the last id not the number of entries
                count = list(count)
                response = app.response_class(
                    response=json.dumps({"checkpoint":count[0]['_id']}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({"error":"invalid apikey"}),
                    status=200,
                    mimetype='application/json'
                )
                return response

    def start(self):
        '''
        Method to start server
        '''
        app.run(host=self.ip, port=self.port, debug=self.debug)
    

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    server=PDBServer(dbname="colav",ip=socket.gethostbyname(socket.gethostname()),port=8080)
    server.start()
