from hunabku.HunabkuBase import HunabkuPluginBase, endpoint

class InspirehepLHCDocsApi(HunabkuPluginBase):

    def __init__(self, hunabku):
        super().__init__(hunabku)
        self.db = self.dbclient['inspirehep']
        self.collection = self.db['lhc']


    def get_documents(self,idx=None,max_results=100,page=1):

        if idx:
            cursor=self.collection.find({"id":str(idx)})
        else:
            cursor=self.collection.find()

        total=cursor.count()
        if not page:
            page=1
        else:
            try:
                page=int(page)
            except:
                print("Could not convert end page to int")
                return None

        if not max_results:
            max_results=100
        else:
            try:
                max_results=int(max_results)
            except:
                print("Could not convert end max to int")
                return None

        if max_results>500:
            max_results=500

        cursor=cursor.skip(max_results*(page-1)).limit(max_results)

        documents = list(cursor)

        return {"data":documents,"count":len(documents),"page":page,"total_results":total}

    @endpoint('/api/inspirehep/documents', methods=['GET'])
    def api_documents(self):
        """
        @api {get} /api/faculties Faculties
        @apiName api
        @apiGroup CoLav api
        @apiDescription Responds with information about a faculty

        @apiParam {String} apikey Credential for authentication
        @apiParam {Object} id The inspirehep literature id of the document requested
        @apiParam {Int} max Maximum results per page
        @apiParam {Int} page Number of the page

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        @apiError (Error 204) msg  The HTTP 204 No Content.
        @apiError (Error 200) msg  The HTTP 200 OK.
        """
        if not self.valid_apikey():
            return self.apikey_error()

        idx = self.request.args.get('id')
        max_results=self.request.args.get('max')
        page=self.request.args.get('page')
        papers=self.get_documents(None,max_results,page)
        if papers:
            response = self.app.response_class(
                response=self.json.dumps(papers),
                status=200,
                mimetype='application/json'
            )
        else:
            response = self.app.response_class(
            response=self.json.dumps({"status":"Request returned empty"}),
            status=204,
            mimetype='application/json'
            )

        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    @endpoint('/api/inspirehep/single/<doc_id>', methods=['GET'])
    def api_single_document(self, doc_id):
        """
        @api {get} /api/faculties Faculties
        @apiName api
        @apiGroup CoLav api
        @apiDescription Responds with information about a faculty

        @apiError (Error 401) msg  The HTTP 401 Unauthorized invalid authentication apikey for the target resource.
        @apiError (Error 204) msg  The HTTP 204 No Content.
        @apiError (Error 200) msg  The HTTP 200 OK.
        """
        if not self.valid_apikey():
            return self.apikey_error()

        idx = self.request.args.get('id')
        documents = self.get_documents(idx,None,None)
        document =  documents.data
        if document:
            response = self.app.response_class(
                response=self.json.dumps(document),
                status=200,
                mimetype='application/json'
            )
        else:
            response = self.app.response_class(
            response=self.json.dumps({"status":"Request returned empty"}),
            status=204,
            mimetype='application/json'
            )

        response.headers.add("Access-Control-Allow-Origin", "*")
        return response