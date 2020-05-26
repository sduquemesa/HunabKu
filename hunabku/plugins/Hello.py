from hunabku.HunabkuBase import HunakuPluginBase, endpoint

class Hello(HunakuPluginBase):
    def __init__(self,hunabku):
        super().__init__(hunabku)

    @endpoint('/hello',methods=['GET'])
    def hello(self):
        """
        @api {get} /user/:id Request User information
        @apiName GetUser
        @apiGroup User

        @apiParam {Number} id Users unique ID.

        @apiSuccess {String} firstname Firstname of the User.
        @apiSuccess {String} lastname  Lastname of the User.
        """
        if self.valid_apikey():
            response = self.app.response_class(
                response=self.json.dumps({'hello':'world'}),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.apikey_error()
