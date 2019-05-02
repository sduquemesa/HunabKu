from hunabku.HunabkuBase import HunabkuPluginBase, endpoint
from bson import ObjectId

class MoaiGSProfile(HunabkuPluginBase):
    def __init__(self, hunabku):
        super().__init__(hunabku)

    @endpoint('/moai/gs/profile/checkpoint', methods=['GET'])
    def profile_checkpoint(self):
        """
        @api {get} /moai/gs/profile/checkpoint GSProfile checkpoint
        @apiName GSProfile
        @apiGroup Moai GSProfile
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
        if self.valid_apikey():
            db = self.request.args.get('db')
            self.db = self.dbclient[db]
            stage        = self.db['stage']
            profiles     = self.db['profiles']
            ckeckpoint = True  # False if any error or all was dowloaded
            error = False
            msg = ""
            ckp_ids = []  # _id(s) for checkpoint

            # reading collection data
            try:
                profiles_c = stage.find({'profiles':{'$ne':{}}},{'_id':0,'profiles':1})
                profiles_p = profiles.find({},{'_id':1})

                profiles_stage = list(profiles_c)
                profiles_stage_ids = []
                for profile in profiles_stage:
                    for user in profile['profiles']:
                        profiles_stage_ids.append(profile['profiles'][user])
                
                profiles_stage_ids = set(profiles_stage_ids)

                profiles_collection = list(profiles_p)
                profiles_ids = []
                for profile in profiles_collection:
                    profiles_ids.append(profile['_id'])
                profiles_ids = set(profiles_ids)
                ckp_ids = list(profiles_stage_ids - profiles_ids)                

            except BaseException:
                ckp_ids = []

            msg = 'ids for profiles in database ' + db + ' collection stage still not downloaded'
            response = self.app.response_class(
                response=self.json.dumps(
                    {'checkpoint': ckeckpoint, 'ids': ckp_ids, 'error': error, 'msg': msg}),
                status=200,
                mimetype='application/json'
            )
            return response

        else:
            return self.apikey_error()
