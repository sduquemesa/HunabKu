
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


_endpoints={}

def endpoint(path, methods):
    def wrapper(func):
        global _endpoints
        print('------ Adding endpoint '+path+' with methods'+str(methods))
        class_name, func_name = func.__qualname__.split('.')
        _endpoints[class_name]={'path':path,'methods':methods,'func_name':func_name}
        #print(_endpoints)
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
        
        _dumps = self.json.dumps
        _dump = self.json.dump
        #added support to our json encoder
        def json_dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=HunakuJsonEncoder, indent=None, separators=None, default=None, sort_keys=False):
            return _dumps(obj=obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii,
                          check_circular=check_circular, allow_nan=allow_nan, cls=cls, 
                          indent=indent, separators=separators, default=default, sort_keys=sort_keys)
        def json_dump(obj, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=HunakuJsonEncoder, indent=None, separators=None, default=None, sort_keys=False):
            return _dump(obj=obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii,
                          check_circular=check_circular, allow_nan=allow_nan, cls=cls, 
                          indent=indent, separators=separators, default=default, sort_keys=sort_keys)
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
        global _endpoints
        endpoint_data = _endpoints[type(self).__name__]
        path = endpoint_data['path']
        func_name = endpoint_data['func_name']
        methods = endpoint_data['methods']
        func = getattr(self,func_name)
        self.app.add_url_rule(path,view_func=func,methods = methods)







        
    
