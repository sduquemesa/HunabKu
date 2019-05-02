from flask import (
    Flask,
    json,
    request
)

from pymongo import MongoClient

from pandas import DataFrame

app = Flask(__name__, template_folder="templates")


class PDBServer:
    '''
    Class to serve papers information store in a mongodb database throught an API using flask.
    
    example:
    http://0.0.0.0:5000/v1/data?init=1&end&apikey=pl0ok9ij8uh7yg
    '''
    def __init__(self,dbname,dbcollection,dbapikey="colavudea",dburi='mongodb://localhost:27017/', ip='0.0.0.0',port=5000,debug=True):
        '''
        Contructor to initialize configuration options.
        
        Args:
            ip (str): ip to start the server 
            port (int): port for the server
            debug (bool): enable/disable debug mode with extra messages output.
        '''
        self.dbname       = dbname
        self.dbcollection = dbcollection
        self.dbclient     = MongoClient(dburi)
        self.db           = self.dbclient[self.dbname]
        self.ip = ip
        self.port = port
        self.debug = debug

        # Create the application endpoints
        @app.route('/data',methods = ['GET'])
        def data():
            """
            This function just responds to the browser ULR
            localhost_ip:5000/data

            :return:        json with data 
            """
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db[self.dbcollection].find({"_id": {"$gte": int(init),"$lte":int(end)}})
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

    def start(self):
        '''
        Method to start server
        '''
        app.run(host=self.ip, port=self.port, debug=self.debug)
    

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    server=PDBServer(dbname="RedalycMetadatosArticulos",dbcollection="data")
    server.start()
