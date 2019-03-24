from media_engine.config import get_config
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.lib.validators import customer_authenticate
from flask_restful import reqparse
import json
from media_engine.helper import get_logger
from flask import request
from media_engine.lib.retry_sms import repush_by_id, repush_by_account_id


config=get_config()
logger = get_logger()
## repush the failed message again

class RetrySms(Resource):
    method_decorators = [customer_authenticate]

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument('sms_list', type=list, required=True, help='REQ-SMS-IDs-LIST', location='json')
        self.request_parser.add_argument('account_list', type=list, required=True, help='REQ-ACCOUNT-IDs-LIST', location='json')

    def post(self, **kwargs):
        """
        @api {post} http://api.onehop.co/v1/repush_incoming_sms/ Send Bulk sms_ids
        @apiName Send bulk SMS IDs
        @apiVersion 1.1.0
        @apiGroup Send SMS

        @apiHeader {String} apiKey Account's Apikey

        @apiParam {json} sms_info List of sms in json format
        @apiParamExample {json} Request-Example:
        {
            "account_list": ["10000001","10000002"]
         }
        or
        {
            "sms_list":["02256e81-d674-46d1-a7b8-d850a760c879","02256e81-d674-46d1-a7b8-d850a760c879"]
        }

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        "\"Messages pushed successfully\""


        @apiErrorExample No Apikey
        HTTP/1.1 401 Unauthorized
        {
            "message": "REQ-API-KEY"
        }

        @apiErrorExample Invalid Apikey
        HTTP/1.1 401 Unauthorized
        {
            "message": "INVALID-API-KEY"
        }

        @apiExample {python} Example - python
        import requests
        import json
        url = "http://api.onehop.co/v1/repushsms/"
        json = {"sms_id_list":
                    [
               "bb0733c6-8a45-48b9-b8f4-8f06081d46ab",

               "22f83535-1e2e-4944-97df-94ddf3bd5a0c",
                "id": "8664b578-548c-4730-b96b-665be8dcc497",
              ]
        headers = {
           'apikey': "sm89229d1f340e464cb04810509d9f763f",
           'content-type': "application/json",
           }
        response = requests.post(url, json=json, headers=headers)

        print(json.loads(response.text))

        @apiExample {curl} Example - curl
        curl -X POST -H "apiKey: sm82cd17ac1bbe43698a75f2fb0697ff6d" -H "Content-Type: application/json" -d '{"sms_id_list":[
              {
                "id": "bb0733c6-8a45-48b9-b8f4-8f06081d46ab",
              },
              {
                "id": "22f83535-1e2e-4944-97df-94ddf3bd5a0c",
              },
              {
                "id": "8664b578-548c-4730-b96b-665be8dcc497",
              }
            ]}' "http://api.onehop.co/v1/repushsms"
        """
        logger.info('repush input : {}'.format(request.data))
        sms_data = json.loads(request.data)
        if sms_data is not None and len(sms_data) > 0:
            data_found = False
            if 'sms_list' in sms_data and type(sms_data['sms_list']) == list and len(sms_data['sms_list']) > 0:
                data_found = True
                repush_by_id(sms_data['sms_list'])

            if 'account_list' in sms_data and type(sms_data['account_list']) == list and len(sms_data['account_list']) > 0:
                data_found = True
                repush_by_account_id(sms_data['account_list'])

            if data_found == True:
                return json.dumps('Messages pushed successfully')
            else:
                return json.dumps('Invalid input')
        else:
            return json.dumps('Empty input')
