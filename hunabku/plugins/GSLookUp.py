from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId

class GSLookUp(HunabkuPluginBase):
    def __init__(self,hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/stage/submit',methods=['PUT'])
    def stage_submit(self):
        """
        @api {put} /moai/gs/stage/submit Submit Paper
        @apiName GSLookUp
        @apiGroup GSLookUp
        @apiDescription Allows to submit papers to the collection stage in the given databse db.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {Object} data Json with paper data
        @apiParam {String} apikey  Credential for authentication
        

        @apiSuccess {String}  msg  GSLookUp paper inserted in stage 
        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        data = self.request.args.get('data')
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            jdata=self.json.loads(data)
            jdata["_id"]=ObjectId(jdata["_id"])
            self.db['stage'].insert(jdata)
            response = self.app.response_class(
                response=self.json.dumps({'msg':'GSLookUp Paper inserted in stage'}),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.apikey_error()

    @endpoint('/moai/gs/stage/checkpoint',methods=['GET'])
    def stage_checkpoint(self):
        """
        @api {get} /moai/gs/stage/checkpoint Checkpoint
        @apiName GSLookUp
        @apiGroup GSLookUp
        @apiDescription Allow to know the cuerrent status of the collection data for the given dataset in db
                        Return the ids of papers not dowloaded yet comparing the ids from data and stage collections using set.

        @apiParam {String} db  Database to use in mongodb
        @apiParam {String} apikey  Credential for authentication
        

        @apiSuccess {Bool}  checkpoint  if true then there are more ids to download
        @apiSuccess {String[]}  ids if true then there are more ids to download
        @apiSuccess {Bool}  error  if true then there is an error to handle the ids ex: not collection data to get ids
        @apiSuccess {String} msg Message with the explanation of the error in case error tag is true.
         
        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        """
        db = self.request.args.get('db')
        self.db = self.dbclient[db]
        if self.valid_apikey():
            ckeckpoint = True # False if any error or all was dowloaded
            error=False 
            msg=""
            ckp_ids = [] #_id(s) for checkpoint 

            # reading collection data
            try:
                data_ids=set([str(reg["_id"]) for reg in self.db['data'].find({},{"_id":1})]) 
            except:
                data_ids=[]
            npapers=len(data_ids)
            if npapers == 0:
                error = True
                ckeckpoint = False
                msg="No elements found in database "+db+' collection data'
                response = self.app.response_class(
                    response = self.json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
                    status=200,
                    mimetype='application/json'
                )
                return response

            try:
                stage_ids = set([str(reg["_id"]) for reg in self.db['stage'].find({},{'_id':1})])
            except:
                stage_ids=[]

            if len(stage_ids) == npapers: # all the papers were downloaded
                ckeckpoint = False
                msg = "All papers already downloaded for database "+db+' collection data'
                response = self.app.response_class(
                    response = self.json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
                    status=200,
                    mimetype='application/json'
                )
                return response


            if len(stage_ids)==0:
                ckp_ids = list(data_ids)
                msg = 'stage in database '+db+' is empty'
                response = self.app.response_class(
                    response = self.json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
                    status=200,
                    mimetype='application/json'
                )
                return response

            ckp_ids=list(data_ids-data_ids.intersection(stage_ids))
            msg = 'missing values for stage with database '+db+' collection data'
            response = self.app.response_class(
                response = self.json.dumps({'checkpoint':ckeckpoint,'ids':ckp_ids,'error':error,'msg':msg}),
                status=200,
                mimetype='application/json'
            )
            return response

        else:
            return self.apikey_error()
