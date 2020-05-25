
from flask import (
    Flask,
    json,
    request
)
from bson import ObjectId
from functools import wraps

class HunakuJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


_endpoints=[]

def endpoint(path, methods):
    def wrapper(func):
        global _endpoints
        print('------ Adding endpoint '+path+' with methods'+str(methods))
        _endpoints.append({'path':path,'methods':methods,'func':func})
        @wraps(func)
        def _impl(self, *method_args, **method_kwargs):
            response = func(self)
            return response
        return _impl
    return wrapper

class HunakuPluginBase():
    def __init__(self,hunakub):
        self.dburi        = hunakub.dburi
        self.dbclient     = hunakub.dbclient
        self.ip = hunakub.ip
        self.port = hunakub.port
        self.info_level = hunakub.info_level
        self.apikey = hunakub.apikey
        self.app = hunakub.app
        self.request = request
        self.json = json
        self.logger = hunakub.logger

        self.json._dumps = self.json.dumps
        self.json._dump = self.json.dump
        #added support to our json encoder
        def json_dumps(obj, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=HunakuJsonEncoder, indent=None, separators=None, default=None, sort_keys=False):
            return json._dumps(**locals())
        def json_dump(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=HunakuJsonEncoder, indent=None, separators=None, default=None, sort_keys=False):
            return json._dump(**locals()) 
        #custimized encoder use by default
        self.json.dumps =  json_dumps
        self.json.dump =  json_dump        


    def send_apikey_error(self):
        response = self.app.response_class(
                response=self.json.dumps({'error':'invalid apikey'}),
                status=200,
                mimetype='application/json'
        )
        return response

    def valid_apikey(self):
        apikey = self.request.args.get('apikey')
        if self.apikey == apikey:
            return True
        else:
            return False

    def register_endpoints(self):
        for _endpoint in _endpoints:
            path = _endpoint['path']
            func = _endpoint['func']
            methods = _endpoint['methods']
            self.app.add_url_rule(path,view_func=getattr(self, func.__name__),methods = methods)







        
    
