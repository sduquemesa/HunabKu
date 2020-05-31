from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId


class MoaiGSCites(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/cites/cache/checkpoint', methods=['GET'])
    def checkpoint_cites_endpoint(self):
        """
        @api {get} /moai/gs/cites/cache/checkpoint GSCites checkpoint
        @apiName GSCites
        @apiGroup Moai GSCites
        @apiDescription Allow to know the cuerrent status of the collection cache_cites for the given db
                        Return the registers for cites not dowloaded yet.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {String[]}  Resgisters from cache with urls to download.

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        
        if self.valid_apikey():
            cursor = self.db['cache_cites'].find({'downloaded':0,'empty':0}) 
            data=[]
            for i in cursor:
                data.append(i)
            response = self.app.response_class(
                response = self.json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.apikey_error()    


    @endpoint('/moai/gs/cites/cache/ids', methods=['GET'])
    def cites_cache_ids(self): #this is the checkpoint for cache not for cites itself
        """
        @api {get} /moai/gs/cites/cache/ids retrieve cache ids
        @apiName GSCites
        @apiGroup Moai GSCites
        @apiDescription Allow to download the register ids from collection cache_cites

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} ids  Paper ids to retrieve
        @apiParam {String} apikey  Credential for authentication


        @apiSuccess {Object}  json  all the register ids from cache_cites collection in a json dump

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        db = self.request.args.get('db')
        self.db = self.dbclient[db]

        if self.valid_apikey():
            cursor = self.db['cache_cites'].find({},{'_id':1})
            data=[]
            for i in cursor:
                data.append(i)
            response = self.app.response_class(
                response = self.json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.apikey_error()

