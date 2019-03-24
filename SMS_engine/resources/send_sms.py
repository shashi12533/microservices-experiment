#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from flask import request
from flask_restful import reqparse, abort

from media_engine.helper import get_logger
from media_engine.lib.errors import SmsWorkerError
from media_engine.lib.sms import send_sms, send_sms_bulk
from media_engine.lib.validators import (
    customer_authenticate, validate_source, validate_encoding, required_param, validate_label)
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

log = get_logger()
crash_log = get_logger('crash')


class SendSms(Resource):

    method_decorators = [customer_authenticate]

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument('label', type=validate_label, required=False, help='REQ-LABEL')
        self.request_parser.add_argument('sms_text', type=required_param, required=True, help='REQ-SMS-TEXT')
        self.request_parser.add_argument('sender_id', type=required_param, required=True, help='REQ-SENDER-ID')
        self.request_parser.add_argument('mobile_number', type=required_param, required=True, help='REQ-MOBILE-NUMBER')
        self.request_parser.add_argument('source', type=validate_source, required=False, help='REQ-SOURCE')
        self.request_parser.add_argument('encoding', type=validate_encoding, required=False)
        self.request_parser.add_argument('apiKey', type=required_param, required=False, help='REQ-API-KEY')

    def _get_or_post(self, account_id=None):

        """
        @api {get} /v1/sendSMS/ Send SMS
        @apiVersion 1.1.0
        @apiName Send SMS
        @apiGroup Send SMS

        @apiHeader {String} apiKey Account's Apikey

        @apiparam  {String} label Label
        @apiparam  {String} account_id Account ID
        @apiparam  {String} sms text SMS Text
        @apiparam  {String} sender id  Sender ID
        @apiparam  {String} mobile number mobile number
        @apiparam  {String} source Source
        @apiparam  {String} encoding Encoding

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "status": "submitted",
          "message": "queued",
          "id": "ffe834ea-3761-4fc2-a51e-9345bc94af6a"
        }

        @apiErrorExample
        {
            "message": "ERROR"
        }

        """
        try:
            params = self.request_parser.parse_args()
        except Exception as e:
            try:
                method = request.form
                log.debug("method: {}".format(method))
                log.debug("params before json.loads: {}".format(method.items()))
                params = json.loads(method.items()[0][0])
                params['mobile_number'] = params.pop('mobilenumber')
                params['sms_text'] = params.pop('smsText')
                params['sender_id'] = params.pop('senderId')
                params['source'] = int(params['source'])


            except:
                raise e

        params['account_id'] = account_id
        try:
            params.pop('apiKey')
        except:
            pass

        log.debug('params : {}'.format(params))

        try:
            result = send_sms(**params)
            m_session.commit()
            return result
        except ValueError as val_err:
            log.error(val_err)
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            abort(400, message=key_err.message)
        except SmsWorkerError as sms_err:
            crash_log.error(sms_err)
            abort(500, message=sms_err.message)

    def get(self, account_id=None):
        """
        @api {get} http://api.onehop.co/v1/sms/send/ Send SMS by get
        @apiName Send SMS by GET call
        @apiVersion 1.1.0
        @apiGroup Send SMS

        @apiHeader {String} apiKey Account's Apikey

        @apiparam  {String} label Label
        @apiparam  {String} account_id Account ID
        @apiparam  {String} sms text SMS Text
        @apiparam  {String} sender id  Sender ID
        @apiparam  {String} mobile number mobile number
        @apiparam  {String} source Source
        @apiparam  {String} encoding Encoding

        @apiParamExample {json} Request-Example:
        {
            "label": "marketing",
            "sms_text": "Your SMS text",
            "sender_id": 11200012,
            "mobile_number": "9891989898",
            "source": 1001,
            "encoding": "plaintext"
            "account_id" : ""
        }

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
            "status": "submitted",
            "message": "queued",
            'id': "4e770fca-8c68-44e3-901e-9c13e3149945"
        }

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
        url = "http://api.onehop.co/v1/sms/send/"
        payload = "mobile_number=9552772600&sms_text=helloWorld&label=labelmarket&sender_id=market"
        headers = {
           'apiKey': "sm89229d1f340e464cb04810509d9f763f",
           'content-type': "application/x-www-form-urlencoded"
        }
        response = requests.request("GET", url, headers=headers, params=payload)
        print(response.text)

        @apiExample {curl} Example - curl
        curl -X GET -H "apiKey: sm89229d1f340e464cb04810509d9f763f" -H "Content-Type: application/x-www-form-urlencoded" "http://api.onehop.co/v1/sms/send/?mobile_number=9552772600&sms_text=helloWorld&label=labelmarket&sender_id=market"
        """
        return self._get_or_post(account_id=account_id)

    def post(self, account_id=None):
        """
        @api {post} http://api.onehop.co/v1/sms/send/ Send SMS by post
        @apiName Send SMS by POST call
        @apiVersion 1.1.0
        @apiGroup Send SMS

        @apiHeader {String} apiKey Account's Apikey

        @apiParam {String} label Label
        @apiParam {String} sms_text SMS Text
        @apiParam {String} sender_id Sender Id
        @apiParam {String} mobile_number Mobile Number
        @apiParam {Number} [source] Source [default: 1001]
        @apiParam {String} [encoding] Encoding [default: 'plaintext', choices: 'plaintext', 'unicode']

        @apiParamExample {json} Request-Example:
        {
            "label": "marketing",
            "sms_text": "Your SMS text",
            "sender_id": 11200012,
            "mobile_number": "9891989898",
            "source": 1001,
            "encoding": "plaintext"
        }

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
            "status": "submitted",
            "message": "queued",
            "id": "4e770fca-8c68-44e3-901e-9c13e3149945"
        }

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
        url = "http://api.onehop.co/v1/sms/send/"
        payload = "mobile_number=9552772600&sms_text=helloWorld&label=labelMarket&sender_id=market"
        headers = {
           'apiKey': "sm89229d1f340e464cb04810509d9f763f",
           'content-type': "application/x-www-form-urlencoded",
           }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)

        @apiExample {curl} Example - curl
curl -X POST -H "apiKey: sm89229d1f340e464cb04810509d9f763f" -H "Content-Type: application/x-www-form-urlencoded" -d 'mobile_number=9552772600&sms_text=helloWorld&label=labelmarket&sender_id=market' "http://api.onehop.co/v1/sms/send/"
        """
        return self._get_or_post(account_id=account_id)


class SendSmsBulk(Resource):

    method_decorators = [customer_authenticate]

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument('apiKey', type=required_param, required=False, help='REQ-API-KEY')
        self.request_parser.add_argument('sms_list', type=list, required=True, help='REQ-SMS-LIST', location='json')

    def post(self, account_id=None):
        """
        @api {post} http://api.onehop.co/v1/sms/send/bulk Send Bulk SMS
        @apiName Send bulk SMS
        @apiVersion 1.1.0
        @apiGroup Send SMS

        @apiHeader {String} apiKey Account's Apikey

        @apiParam {json} sms_info List of sms in json format
        @apiParamExample {json} Request-Example:
        {"sms_list":
            [
                {"mobile_number": "8486284673",
                 "sms_text": "hello",
                 "sender_id": "ameya",
                 "label": "aerialink"
                },
                {"mobile_number": "8486284673",
                 "sms_text": "hello",
                 "sender_id": "ameya",
                 "label": "nexmo_us"
                },
                {"mobile_number": "7149305641",
                 "sms_text": "hello",
                 "sender_id": "ameya",
                 "label": "nexmo_us"
                }
            ]
        }

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        [
              {
                "id": "bb0733c6-8a45-48b9-b8f4-8f06081d46ab",
                "message": "queued",
                "status": "submitted"
              },
              {
                "id": "22f83535-1e2e-4944-97df-94ddf3bd5a0c",
                "message": "queued",
                "status": "submitted"
              },
              {
                "id": "8664b578-548c-4730-b96b-665be8dcc497",
                "message": "queued",
                "status": "submitted"
              }
        ]

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
        url = "http://api.onehop.co/v1/sms/send/bulk"
        json = {"sms_list":
                    [
                    {"mobile_number": "8486284673",
                     "sms_text": "hello",
                     "sender_id": "ameya",
                     "label": "aerialink"
                    },
                    {"mobile_number": "8486284673",
                     "sms_text": "hello",
                     "sender_id": "ameya",
                     "label": "nexmo_us"
                    },
                    {"mobile_number": "7149305641",
                     "sms_text": "hello",
                     "sender_id": "ameya",
                     "label": "nexmo_us"
                    }
                    ]}
        headers = {
           'apikey': "sm89229d1f340e464cb04810509d9f763f",
           'content-type': "application/json",
           }
        response = requests.post(url, json=json, headers=headers)

        print(json.loads(response.text))

        @apiExample {curl} Example - curl
        curl -X POST -H "apiKey: sm82cd17ac1bbe43698a75f2fb0697ff6d" -H "Content-Type: application/json" -d '{"sms_list":[{"mobile_number": "8486284673","sms_text": "hello","sender_id": "ameya","label": "aerialink"},{"mobile_number":"8486284673","sms_text": "hello","sender_id": "ameya", "label": "nexmo_us"},{"mobile_number": "7149305641", "sms_text":"hello",
"sender_id": "ameya","label": "nexmo_us"}]}' "http://api.onehop.co/v1/sms/send/bulk"
        """
        try:
            params = self.request_parser.parse_args()
        except Exception as e:
            try:
                method = request.form
                log.debug("method: {}".format(method))
                log.debug("params before json.loads: {}".format(method.items()))
                params = json.loads(method.items()[0][0])
                params['sms_info'] = params.pop('sms_info')
            except:
                raise e

        params['account_id'] = account_id
        params.pop('apiKey', None)
        log.debug('params : {}'.format(params))

        try:
            result = send_sms_bulk(**params)
            m_session.commit()
            return result
        except ValueError as val_err:
            log.error(val_err)
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            abort(400, message=key_err.message)
        except SmsWorkerError as sms_err:
            crash_log.error(sms_err)
            abort(500, message=sms_err.message)


class PushDeliveryReports(Resource):
    """For API DOC purpose"""

    def get(self, account_id=None):
        """
        @api {post} /registered/url/ Push Delivery Reports of SMS
        @apiName Push Delivery Reports
        @apiDescription Below parameters will be pushed to your registered URL, in JSON format
        @apiVersion 1.0.0
        @apiGroup Push

        @apiParam {String} sms_id SMS Identifier
        @apiParam {String} delivery_status Delivery Status of SMS
        @apiParam {String} timestamp Timestamp of delivery
        @apiParam {String} mobile_number Mobile Number to which this SMS was sent
        @apiParam {String} label Label used to send this SMS

        @apiParamExample {json} Request-Example:
        {
            "id": "4e770fca-8c68-44e3-901e-9c13e3149945",
            "delivery_status": "success",
            "timestamp": "2011-07-14T19:43:37+0100",
            "mobile_number": "9891989898",
            "label": "marketing"
        }
        """
        pass

class PushIncoming(Resource):
    """For API DOC purpose"""

    def get(self, account_id=None):
        """
        @api {post} /registered/url/ Push Incoming SMS
        @apiName Push Incoming SMS
        @apiDescription Below parameters will be pushed to your registered URL, in JSON format
        @apiVersion 1.0.0
        @apiGroup Push

        @apiParam {String} id SMS Identifier
        @apiParam {String} sent_from Number from which this SMS was sent
        @apiParam {Number} sent_to Number to which SMS was sent
        @apiParam {String} msg SMS Text
        @apiParam {String} timestamp Timestamp when SMS was received

        @apiParamExample {json} Request-Example:
        {
            "id": "fcd70fca-8c68-44e3-901e-9c13e3149945",
            "sent_from": "9891989898",
            "sent_to": "124128",
            "msg": "Hello World",
            "timestamp": "2014-09-11T11:21:34+0100",
        }
        """
        pass
