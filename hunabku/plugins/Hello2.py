from hunabku.HunabkuBase import HunakuPluginBase, endpoint

class Hello2(HunakuPluginBase):
    def __init__(self,hunabku):
        super().__init__(hunabku)

    @endpoint('/v0/hello2',methods=['GET'])
    def hello2(self):
        """
        @api {get} /hello/:id Other Hello Request
        @apiName Hello2
        @apiGroup Hello2

        @apiParam {Number} id Users unique ID.

        @apiSuccess {String} firstname Firstname of the User.
        @apiSuccess {String} lastname  Lastname of the User.
        @apiVersion 0.0.1
        """        
        if self.valid_apikey():
            response = self.app.response_class(
                response=self.json.dumps({'hello2':'world2'}),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.apikey_error()

    @endpoint('/bye',methods=['GET'])
    def bye(self):
        """
        @api {get} /bye/:id Request Bye Information
        @apiName Hello2
        @apiGroup Hello2

        @apiParam {Number} id Users unique ID.

        @apiSuccess {String} firstname Firstname of the User.
        @apiSuccess {String} lastname  Lastname of the User.
        """        
        if self.valid_apikey():
            response = self.app.response_class(
                response=self.json.dumps({'bye':'bye'}),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.apikey_error()
