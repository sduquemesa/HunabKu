from flask import (
    Flask,
    json,
    request
)

from pymongo import MongoClient
import socket
from pandas import DataFrame

from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


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
    def create_cache_endpoints(self):
        print('Creating endpoints for caches')
        def cites_cache_submit():
            '''
            endpoint to submit cites links
            '''
            data = request.args.get('data')
            collection = request.args.get('collection')
            print(collection)
            apikey=request.args.get('apikey')
            if self.dbapikey == apikey:
                cursor = self.db['cache_cites_{}'.format(collection)].insert(json.loads(data))
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
        app.add_url_rule('/cache/cites/submit',view_func=cites_cache_submit,methods = ['GET'])
        print('-    endpoint = {}'.format('/cache/cites/submit'))
        
        def cites_cache_read():
            '''
            endpoint to read cites links from cache
            '''
            collection = request.args.get('collection')
            apikey=request.args.get('apikey')
            if self.dbapikey == apikey:
                cursor = self.db['cache_cites_{}'.format(collection)].find({'downloaded':0})
                data=[]
                for i in cursor:
                    data.append(i)
                response = app.response_class(
                    response=json.dumps(JSONEncoder().encode(data)),
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
        app.add_url_rule('/cache/cites/read',view_func=cites_cache_read,methods = ['GET'])
        print('-    endpoint = {}'.format('/cache/cites/read'))
        
        def cites_cache_update():
            '''
            endpoint to update cites links from cache
            '''
            _id = request.args.get('_id') #object id
            collection = request.args.get('collection')
            apikey=request.args.get('apikey')
            if self.dbapikey == apikey:
                cursor = self.db['cache_cites_{}'.format(collection)].update_one({'_id':ObjectId(json.loads(_id))},{"$set":{'downloaded':1}})
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
        app.add_url_rule('/cache/cites/update',view_func=cites_cache_update,methods = ['GET'])
        print('-    endpoint = {}'.format('/cache/cites/update'))

    def create_endpoints(self,collection):
        dbapikey = self.dbapikey

        print('Creating endpoints for {}'.format(collection))

        def data_endpoint():
            '''
            '''
            ids=request.args.get('ids')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['data_{}'.format(collection)].find({'_id': {'$in': json.loads(ids)}})
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
        data_endpoint.__name__ = data_endpoint.__name__+'_'+collection 
        app.add_url_rule('/data/{}'.format(collection),view_func=data_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/data/{}'.format(collection)))
                
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
        print('-    endpoint = {}'.format('/stage/{}/submit'.format(collection)))

        #@app.route('/stage/{}/read'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_read_endpoint():
            '''
            '''
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                if int(end) == -1:
                    cursor = self.db['stage_{}'.format(collection)].find()
                else:
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
        print('-    endpoint = {}'.format('/stage/{}/read'.format(collection)))
            
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
        print('-    endpoint = {}'.format('/stage/{}/cites/read'.format(collection)))

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
        print('-    endpoint = {}'.format('/stage/{}/cites/submit'.format(collection)))

        #@app.route('/stage/{}/checkpoint'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_checkpoint_endpoint():
            '''
            Return values to restore the process execution

            '''
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                ckeckpoint = True # False if any error or all was dowloaded
                error=False 
                mgs=""
                ckp_ids = [] #_id(s) for checkpoint 

                # reading collection data
                npapers = self.db['data_{}'.format(collection)].count() #number of papers in data collection 
                if npapers == 0:
                    error = True
                    ckeckpoint = False
                    mgs="Not elements found in data_"+collection
                    response = app.response_class(
                        response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'mgs':mgs}),
                        status=200,
                        mimetype='application/json'
                    )
                    return response

                ids = self.db['stage_{}'.format(collection)].find({},{'_id':1})
                ids_df = DataFrame.from_records(ids)

                if len(ids_df.values) == npapers: # all the papers was downloaded
                    ckeckpoint = False
                    mgs = "All papers already downloaded for data_"+collection
                    response = app.response_class(
                        response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'mgs':mgs}),
                        status=200,
                        mimetype='application/json'
                    )
                    return response


                if ids_df.empty:
                    ckp_ids = [i for i in range(npapers)]
                    mgs = 'stage_'+collection+' is empty'
                    response = app.response_class(
                        response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'mgs':mgs}),
                        status=200,
                        mimetype='application/json'
                    )
                    return response

                values=ids_df['_id'].values
                ckp_ids=sorted(set(range(0, npapers)) - set(values))  
                mgs = 'missing values for stage_'+collection
                response = app.response_class(
                    response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'mgs':mgs}),
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
        print('-    endpoint = {}'.format('/stage/{}/checkpoint'.format(collection)))

        #@app.route('/stage/{}/cites/checkpoint'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_checkpoint_cites_endpoint():
            """
            return remaning links to download for citations
            :return:        json with data 
            """
            apikey = request.args.get('apikey')
            if self.dbapikey == apikey:
                cursor = self.db['cache_cites_{}'.format(collection)].find({'downloaded':0})
                data=[]
                for i in cursor:
                    data.append(i)
                response = app.response_class(
                    response=json.dumps(JSONEncoder().encode(data)),
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
        print('-    endpoint = {}'.format('/stage/{}/cites/checkpoint'.format(collection)))

    def start(self):
        '''
        Method to start server
        '''
        app.run(host=self.ip, port=self.port, debug=self.debug)
