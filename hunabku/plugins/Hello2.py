from hunabku.HunabkuBase import HunakuPluginBase, endpoint

class Hello2(HunakuPluginBase):
    def __init__(self,hunabku):
        super().__init__(hunabku)

    @endpoint('/hello',methods=['GET'])
    def hello2(self):
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
        if self.valid_apikey():
            response = self.app.response_class(
                response=self.json.dumps({'bye':'bye'}),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.apikey_error()
