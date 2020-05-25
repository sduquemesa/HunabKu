from hunabku.HunabkuBase import HunakuPluginBase, endpoint

class Hello(HunakuPluginBase):
    def __init__(self,hunabku):
        super().__init__(hunabku)

    @endpoint('/hello',methods=['GET'])
    def hello(self):
        if self.valid_apikey():
            response = self.app.response_class(
                response=self.json.dumps({'hello':'world'}),
                status=200,
                mimetype='application/json'
            )
            return response    
        else:
            return self.send_apikey_error()
