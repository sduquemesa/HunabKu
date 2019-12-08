from flask import (
    Flask,
    json,
    request
)

from pymongo import MongoClient
import socket
from pandas import DataFrame

app = Flask(__name__, template_folder='templates')


class PDBServer:
    '''
    Class to serve papers information store in a mongodb database throught an API using flask.
    
    example:
    http://0.0.0.0:5000/data/redalyc?init=1&end&apikey=pl0ok9ij8uh7yg
    '''
    def __init__(self,dbname,dbapikey='colavudea',dburi='mongodb://localhost:27017/', ip='0.0.0.0',port=5000,debug=True):
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
        self.dbapikey = dbapikey

    def create_endpoints(self,collection):
        dbapikey = self.dbapikey

        print('Creating endpoints for')
        # Create the application endpoints dinamically
        def endpoint_creator(func):
            l, g = locals().copy(), globals().copy()
            g['func']=func
            exec('def {}_{}():\n    return func'.format(func.__name__,collection),g,l)
            wrapper = eval('{}_{}'.format(func.__name__,collection),g,l)
            return wrapper

        #@app.route('/data/{}'.format(collection),methods = ['GET'])
        def data_endpoint():
            '''
            '''
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['data_{}'.format(collection)].find({'_id': {'$gte': int(init),'$lte':int(end)}})
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
                    response=json.dumps({'error':'invalid apikey'}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
        data_endpoint.__name__ = data_endpoint.__name__+'_'+collection 
        app.add_url_rule('/data/{}'.format(collection),view_func=data_endpoint,methods = ['GET'])
                
        #@app.route('/stage/{}/submit'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_submit_endpoint():
            '''
            '''
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                self.db['stage_{}'.format(collection)].insert(json.loads(data))
                response = app.response_class(
                    response=json.dumps({}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({'error':'invalid apikey'}),
                    status=200,
                    mimetype='application/json'
                )
                return response
        stage_submit_endpoint.__name__ = stage_submit_endpoint.__name__+'_'+collection 
        app.add_url_rule('/stage/{}/submit'.format(collection),view_func=stage_submit_endpoint,methods = ['GET'])

        #@app.route('/stage/{}/read'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_read_endpoint():
            '''
            '''
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['stage_{}'.format(collection)].find({'_id': {'$gte': int(init),'$lte':int(end)}})
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
                    response=json.dumps({'error':'invalid apikey'}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
        stage_read_endpoint.__name__ = stage_read_endpoint.__name__+'_'+collection 
        app.add_url_rule('/stage/{}/read'.format(collection),view_func=stage_read_endpoint,methods = ['GET'])
            
        #@app.route('/stage/{}/cites/read'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_cites_read_endpoint():
            '''
            '''
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['stage_cites_{}'.format(collection)].find({'_id': {'$gte': int(init),'$lte':int(end)}})
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
                    response=json.dumps({'error':'invalid apikey'}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
    
        stage_cites_read_endpoint.__name__ = stage_cites_read_endpoint.__name__+'_'+collection 
        app.add_url_rule('/stage/{}/cites/read'.format(collection),view_func=stage_cites_read_endpoint,methods = ['GET'])

        #@app.route('/stage/{}/cites/submit'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_cites_submit_endpoint():
            '''

            '''
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                self.db['stage_cites_{}'.format(collection)].insert(json.loads(data))
                response = app.response_class(
                    response=json.dumps({}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({'error':'invalid apikey'}),
                    status=200,
                    mimetype='application/json'
                )
                return response

        stage_cites_submit_endpoint.__name__ = stage_cites_submit_endpoint.__name__+'_'+collection 
        app.add_url_rule('/stage/{}/cites/submit'.format(collection),view_func=stage_cites_submit_endpoint,methods = ['GET'])

        #@app.route('/stage/{}/checkpoint'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_checkpoint_endpoint():
            '''
            '''
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                count = self.db['stage_{}'.format(collection)].find({}).sort([('_id', -1)]).limit(1) #fixed this, is the last id not the number of entries
                count = list(count)
                if len(count) != 0:
                    response = app.response_class(
                        response=json.dumps({'checkpoint':count[0]['_id']}),
                        status=200,
                        mimetype='application/json'
                    )
                else:
                    response = app.response_class(
                        response=json.dumps({'checkpoint':0}),
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

        stage_checkpoint_endpoint.__name__ = stage_checkpoint_endpoint.__name__+'_'+collection 
        app.add_url_rule('/stage/{}/checkpoint'.format(collection),view_func=stage_checkpoint_endpoint,methods = ['GET'])

        #@app.route('/stage/{}/cites/checkpoint'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_checkpoint_cites_endpoint():
            """

            :return:        json with data 
            """
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                count = self.db['stage_cites_{}'.format(collection)].find({}).sort([('_id', -1)]).limit(1) #fixed this, is the last id not the number of entries
                count = list(count)
                if len(count) != 0:
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
                    response=json.dumps({'error':'invalid apikey'}),
                    status=200,
                    mimetype='application/json'
                )
                return response

        stage_checkpoint_cites_endpoint.__name__ = stage_checkpoint_cites_endpoint.__name__+'_'+collection 
        app.add_url_rule('/stage/{}/cites/checkpoint'.format(collection),view_func=stage_checkpoint_cites_endpoint,methods = ['GET'])

    def start(self):
        '''
        Method to start server
        '''
        app.run(host=self.ip, port=self.port, debug=self.debug)
