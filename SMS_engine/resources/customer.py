#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.credits import get_all_credits
from media_engine.lib.accounting import get_product_name
from media_engine.lib.labels import list_labels_for_product
from media_engine.lib.validators import customer_authenticate
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

log = get_logger()
crash_log = get_logger('crash')


def transform_credit_obj(account_id, credit_obj):
    ret_dict = dict(
        product_id=credit_obj.product_id,
        currency_code=credit_obj.currency_code,
        added_credits=credit_obj.balance+credit_obj.used_balance,
        consumed_credits=credit_obj.used_balance,
        remaining_credits=credit_obj.balance,
    )

    try:
        labels = list_labels_for_product(
            account_id=account_id,
            product_id=credit_obj.product_id)
    except:
        labels = []

    try:
        product_name = get_product_name(product_id=credit_obj.product_id)
    except:
        product_name = ''

    ret_dict['labels'] = labels
    ret_dict['product_name'] = product_name
    return ret_dict


class CustomerCredits(Resource):
    method_decorators = [customer_authenticate]

    def get(self, account_id):
        """
        @api {get} /v1/credits/ Get Credits Information
        @apiVersion 1.1.0
        @apiName Get Credits Information for an Account
        @apiGroup Credits

        @apiHeader {String} apiKey Account's Apikey

        @apiparam  {String} account_id Account ID

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
         "credits": [
           {
             "added_credits": 472.97,
             "consumed_credits": 0,
             "currency_code": "EUR",
             "labels": [
               "label14one"
             ],
             "product_id": "6a9f3d33-0d29-4c16-b1b0-fedaaf010b10",
             "product_name": "Nexmo Portugal Regular",
             "remaining_credits": 472.97
           },
           {
             "added_credits": 25.2,
             "consumed_credits": 0,
             "currency_code": "USD",
             "labels": [
               "label2Hello"
             ],
             "product_id": "a07d8d58-276a-4dd9-a15e-ec50cd65b5d4",
             "product_name": "Monty Mobile US Premium",
             "remaining_credits": 25.2
           }
         ]
       }


        @apiExample {python} Example - python:
        import requests
        url = "http://api.onehop.co/v1/credits/"
        headers = {
            'apikey': "sme1caf1bd2c78471ebcebf6aa354b7973", # your api key
        }
        response = requests.request("GET", url, headers=headers)
        print(response.text)

        @apiExample {curl} Example - curl:
        curl -X GET -H "apiKey: sme1caf1bd2c78471ebcebf6aa354b7973" "http://api.onehop.co/v1/credits/"
        """
        try:
            credit_objs = get_all_credits(account_id=account_id)
            credits_list = [transform_credit_obj(account_id, x) for x in credit_objs]

            return dict(credits=credits_list)
        except ValueError as val_err:
            log.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            print sa_err
            abort(500, message="API-ERR-DB")


class CustomerApikey(Resource):
    method_decorators = [customer_authenticate]

    def get(self, account_id):
        """
        @api {get} /v1/api_key/validate/ Validate apikey
        @apiVersion 1.1.0
        @apiName Validate apiKey
        @apiGroup Accounts

        @apiHeader {String} apiKey Account's Apikey

        No Parameters are required while making request.

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

       {
         "status": "success"
       }

       @apierrorExample
       {
          "message": "Error Message",
          "status": "Error"
       }

        @apiExample {python} Example - python:
        import requests
        url = "http://api.onehop.co/v1/api_key/validate/"
        headers = {
            'apikey': "sme1caf1bd2c78471ebcebf6aa354b7973", # your api key
        }
        response = requests.request("GET", url, headers=headers)
        print(response.text)

        @apiExample {curl} Example - curl:
        curl -X GET -H "apiKey: sme1caf1bd2c78471ebcebf6aa354b7973" "http://api.onehop.co/v1/api_key/validate/"
        """
        return dict(status='success')