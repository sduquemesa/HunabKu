from flask import (
    Flask,
    json,
    request
)

from pymongo import MongoClient

app = Flask(__name__, template_folder="templates")


class DBServer:
    def __init__(self, ip='0.0.0.0',port=5000,debug=True):
        self.ip = ip
        self.port = port
        self.debug = debug

        # Create the application endpoints
        @app.route('/data',methods = ['GET'])
        def data():
            """
            This function just responds to the browser ULR
            localhost_ip:5000/data

            :return:        json with data 
            """
            init=request.args.get('init')
            end=request.args.get('end')
            apikey=request.args.get('apikey')
            data = {"init":init,"end":end}
            response = app.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json'
            )
            return response    

    def start(self):
        app.run(host=self.ip, port=self.port, debug=self.debug)
    

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    server=DBServer()
    server.start()
