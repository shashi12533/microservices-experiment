#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.labels import list_labels
from media_engine.lib.validators import customer_authenticate
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

log = get_logger()
crash_log = get_logger('crash')


class CustomerLabelList(Resource):
    method_decorators = [customer_authenticate]

    def get(self, account_id):
        """
        @api {get} http://api.onehop.co/v1/labels/ List labels for an Account
        @apiVersion 1.1.0
        @apiName List labels for customer
        @apiGroup List Labels

        @apiHeader {String} apiKey Account's Apikey

        @apiparam {String} account_id Account ID

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
            "label_list": [
                "my-label",
                "my-label-1"
            ]
        }

        @apiErrorExample
        {
          "message": "Error"
        }

        @apiExample {curl} Example - python
        import requests
        url = "http://api.onehop.co/v1/labels/"
        headers = {
            'apikey': "sme1caf1bd2c78471ebcebf6aa354b7973",
        }
        response = requests.request("GET", url, headers=headers)
        print(response.text)

        @apiExample {curl} Example - curl
        curl -X GET -H "apiKey: sme1caf1bd2c78471ebcebf6aa354b7973" "http://api.onehop.co/v1/labels/"
        """
        try:
            labels_list = list_labels(account_id=account_id)
            # TODO : marshals with, try, except remaining
            return dict(labelsList=labels_list)
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
            abort(500, message="API-ERR-DB")
