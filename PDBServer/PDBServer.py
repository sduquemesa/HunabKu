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
        
    def create_gsquery_endpoints(self):

        def gsquery_read_endpoint():
            apikey=request.args.get('apikey')

            collection=request.args.get('collection')
            
            if self.dbapikey == apikey:
                cursor = self.db['gsquery'].find({'collection':collection,'downloaded':0})
                data=[]
                for i in cursor:
                    data.append(i)
                print(data)
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
        app.add_url_rule('/gsquery/read',view_func=gsquery_read_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/gsquery/read'))

        def gsquery_submit_endpoint():
            #init=request.args.get('init')
            #end=request.args.get('end')
            data = request.args.get('data')
            apikey=request.args.get('apikey')
            if self.dbapikey == apikey:
                self.db['gsquery'].insert(json.loads(data))
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
        app.add_url_rule('/gsquery/submit',view_func=gsquery_submit_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/gsquery/submit'))

        def gsquery_update_endpoint():
            #init=request.args.get('init')
            #end=request.args.get('end')
            id=request.args.get('id')
            data = request.args.get('data')
            apikey=request.args.get('apikey')
            if self.dbapikey == apikey:
                self.db['gsquery'].update_one({"_id":ObjectId(id)},{"$set":json.loads(data)})
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
        app.add_url_rule('/gsquery/update',view_func=gsquery_update_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/gsquery/update'))

    def create_cache_endpoints(self):
        print('Creating endpoints for caches')
        def cites_cache_submit():
            '''
            endpoint to submit cites links
            '''
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if self.dbapikey == apikey:
                self.db['cache_cites'].insert(json.loads(data))
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
            tag = request.args.get('tag')
            apikey=request.args.get('apikey')
            if self.dbapikey == apikey:
                cursor = self.db['cache_cites'].find({'tag':tag,'downloaded':0})
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
            apikey = request.args.get('apikey')
            if self.dbapikey == apikey:
                cursor = self.db['cache_cites'].update_one({'_id':ObjectId(json.loads(_id))},{"$set":{'downloaded':1}})
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

        def checkpoint_cites_endpoint():
            """
            return remaning links to download for citations for a given tag, tag is an identifier for a set of data
            :return:        json with data 
            """
            apikey = request.args.get('apikey')
            tag = request.args.get('tag')
            
            if self.dbapikey == apikey:
                cursor = self.db['cache_cites'].find({'tag':tag,'downloaded':0,'empty':0}) #to get only cites not downloaded and not set like empty page
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

        checkpoint_cites_endpoint.__name__ = checkpoint_cites_endpoint.__name__
        app.add_url_rule('/cache/cites/checkpoint',view_func=checkpoint_cites_endpoint,methods = ['GET'])
        print('-    endpoint = /cache/cites/checkpoint')



    def create_data_endpoint(self,collection):
        dbapikey = self.dbapikey
        def data_submit_endpoint():
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                self.db['data_{}'.format(collection)].insert(json.loads(data))
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
        data_submit_endpoint.__name__ = data_submit_endpoint.__name__+'_'+collection 
        app.add_url_rule('/data/{}/submit'.format(collection),view_func=data_submit_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/data/{}/submit'.format(collection)))

        def data_read_endpoint():
            '''

            '''
            ids=json.loads(request.args.get('ids'))
            #print(ids)
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                #oids=[ObjectId(iid) for iid in ids]
                cursor = self.db['data_{}'.format(collection)].find({'_id': {'$in': ids}})
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
        data_read_endpoint.__name__ = data_read_endpoint.__name__+'_'+collection 
        app.add_url_rule('/data/{}/read'.format(collection),view_func=data_read_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/data/{}/read'.format(collection)))

    def create_cites_endpoints(self):
        def stage_cites_submit_endpoint():
            '''

            '''
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if self.dbapikey == apikey:
                self.db['stage_cites'].insert(json.loads(data))
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

        stage_cites_submit_endpoint.__name__ = stage_cites_submit_endpoint.__name__ 
        app.add_url_rule('/stage/cites/submit',view_func=stage_cites_submit_endpoint,methods = ['GET'])
        print('-    endpoint = /stage/cites/submit')

    def create_lookup_endpoints(self):
        def stage_submit_endpoint():
            '''
            '''
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if self.dbapikey == apikey:
                jdata=json.loads(data)
                jdata["_id"]=ObjectId(jdata["_id"])
                self.db['stage'].insert(jdata)
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
        stage_submit_endpoint.__name__ = stage_submit_endpoint.__name__ 
        app.add_url_rule('/stage/submit',view_func=stage_submit_endpoint,methods = ['GET'])
        print('-    endpoint = /stage/submit')

        def stage_checkpoint_endpoint():
            '''
            Return values to restore the process execution

            '''
            apikey = request.args.get('apikey')
            tag = request.args.get('tag')
            
            if self.dbapikey == apikey:
                ckeckpoint = True # False if any error or all was dowloaded
                error=False 
                msg=""
                ckp_ids = [] #_id(s) for checkpoint 

                # reading collection data
                #npapers = self.db['data_{}'.format(collection)].count() #number of papers in data collection
                try:
                    data_ids=set([str(reg["_id"]) for reg in self.db['data_{}'.format(tag)].find({},{"_id":1})]) 
                except:
                    data_ids=[]
                npapers=len(data_ids)
                if npapers == 0:
                    error = True
                    ckeckpoint = False
                    msg="No elements found in data_"+tag
                    response = app.response_class(
                        response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
                        status=200,
                        mimetype='application/json'
                    )
                    return response

                try:
                    stage_ids = set([str(reg["_id"]) for reg in self.db['stage'].find({'tag':tag},{'_id':1})])
                except:
                    stage_ids=[]

                if len(stage_ids) == npapers: # all the papers were downloaded
                    ckeckpoint = False
                    msg = "All papers already downloaded for data_"+tag
                    response = app.response_class(
                        response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
                        status=200,
                        mimetype='application/json'
                    )
                    return response


                if len(stage_ids)==0:
                    ckp_ids = list(data_ids)
                    msg = 'stage with tag='+tag+' is empty'
                    response = app.response_class(
                        response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
                        status=200,
                        mimetype='application/json'
                    )
                    return response

                ckp_ids=list(data_ids-data_ids.intersection(stage_ids))
                msg = 'missing values for stage with tag='+tag
                response = app.response_class(
                    response=json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
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

        stage_checkpoint_endpoint.__name__ = stage_checkpoint_endpoint.__name__
        app.add_url_rule('/stage/checkpoint',view_func=stage_checkpoint_endpoint,methods = ['GET'])
        print('-    endpoint = /stage/checkpoint')

        def data_endpoint():
            '''
            this is a special endpoint for checkout in GSLookUp class, see data/submit/read
            '''
            ids=json.loads(request.args.get('ids').replace("'","\""))
            oids=[ObjectId(iid) for iid in ids]
            apikey=request.args.get('apikey')
            tag=request.args.get('tag')
            #db=request.args.get('db')
            #self.db = self.dbclient[db]

            
            if self.dbapikey == apikey:
                cursor = self.db['data_{}'.format(tag)].find({'_id': {'$in': oids}})
                data=[]
                for i in cursor:
                    data.append(i)
                response = app.response_class(
                    response=json.dumps(JSONEncoder().encode(data)),
                    status=200,
                    mimetype='application/json'
                )
                if not data:
                    print("data esta vacio")
                return response    
            else:
                response = app.response_class(
                    response=json.dumps({'error':'invalid apikey'}),
                    status=200,
                    mimetype='application/json'
                )
                return response    
        data_endpoint.__name__ = data_endpoint.__name__ 
        app.add_url_rule('/data/',view_func=data_endpoint,methods = ['GET'])
        print('-    endpoint = /data/')
                


    def create_endpoints(self,collection):
        dbapikey = self.dbapikey

        print('Creating endpoints for {}'.format(collection))
        
        #self.create_data_endpoint(collection)
        

        #@app.route('/stage/{}/submit'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def stage_submit_endpoint():
            '''
            '''
            data = request.args.get('data')
            apikey = request.args.get('apikey')
            if dbapikey == apikey:
                jdata=json.loads(data)
                jdata["_id"]=ObjectId(jdata["_id"])
                self.db['stage_{}'.format(collection)].insert(jdata)
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
        stage_read_endpoint.__name__ = stage_read_endpoint.__name__+'_'+collection 
        app.add_url_rule('/stage/{}/read'.format(collection),view_func=stage_read_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/stage/{}/read'.format(collection)))
            
        #@app.route('/stage/{}/cites/read'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)
        def data_cites_read_endpoint():
            '''
            '''
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            if dbapikey == apikey:
                cursor = self.db['data_cites_{}'.format(collection)].find({'_id': {'$gte': int(init),'$lte':int(end)}})
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
    
        data_cites_read_endpoint.__name__ = data_cites_read_endpoint.__name__+'_'+collection 
        app.add_url_rule('/data/{}/cites/read'.format(collection),view_func=data_cites_read_endpoint,methods = ['GET'])
        print('-    endpoint = {}'.format('/data/{}/cites/read'.format(collection)))

        #@app.route('/stage/{}/cites/submit'.format(collection),methods = ['GET']) #Get method is faster than Post (the html body is not sent)



    def start(self):
        '''
        Method to start server
        '''
        app.run(host=self.ip, port=self.port, debug=self.debug)
