#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from flask import request
from flask_restful import abort, reqparse
from sqlalchemy.exc import SQLAlchemyError

from media_engine.core.incoming import store_incoming
from media_engine.helper import get_logger
from media_engine.lib import errors
from media_engine.lib.incoming import get_incoming_config_of_product, save_incoming_config_of_product
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

logger = get_logger()
crash_logger = get_logger('crash')


class BaseResource(Resource):
    def __init__(self, *args, **kwargs):
        self.args = request.args
        self.form = request.form
        self.json = request.json or {}
        self.data = self.args.to_dict()
        self.data.update(dict(request.form.to_dict(), **self.json))
        return super(BaseResource, self).__init__(*args, **kwargs)


class IncomingSMSHandler(BaseResource):

    def get(self, provider_name):
        """
          @api {get} /v1/incoming/<string:provider_name> Handles Incoming SMS
          @apiVersion 1.0.0
          @apiName incoming_sms
          @apiGroup Receivers

          @apiSuccess {String}  message
          @apiSuccessExample e.g. Success-Response
          HTTP/1.1 201 OK

          {
            "message": "queued"
          }

          @apiErrorExample Bad Request
            HTTP/1.1 400 Bad Request
            {
              "message": "error message string"
            }

        """
        return self.handle(provider_name)

    def post(self, provider_name):
        """
          @api {post} /v1/incoming/<string:provider_name> Handles Incoming SMS
          @apiVersion 1.0.0
          @apiName incoming_sms
          @apiGroup Receivers
          @apiSuccess {String}  message
          @apiSuccessExample e.g. Success-Response
          HTTP/1.1 201 OK

          {
            "message": "queued"
          }

          @apiErrorExample Bad Request
          HTTP/1.1 400 Bad Request
          {
            "message": "error message string"
          }

        """
        return self.handle(provider_name)

    def handle(self, provider_name):
        params = self.data
        logger.debug('incoming provider_name : {}'.format(provider_name))
        logger.debug('params : {}'.format(params))

        try:
            response = store_incoming(provider_name, params)
            m_session.commit()
            return transform_response(provider_name, response)
        except ValueError as val_err:
            logger.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            crash_logger.exception(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except errors.InvalidMobileNumberError as mob:
            logger.error("Invalid mobile number = {}".format(mob))
            m_session.rollback()
            abort(400, message="INCOMING-INVALID-MOBILENUMBER")
        except SQLAlchemyError as sa_err:
            crash_logger.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")
        except Exception as exc:
            crash_logger.exception(exc)
            abort(400, message=exc.message)


def transform_response(provider_name, response):
    logger.info("transform_response. provider_name={}, response={}".format(provider_name, response))

    response_map = {
        'smsglobal': "OK",
        'silverstreet': "OK",
        'gupshup': "",
        'telerivet': "200",
        'nexmo': "200",
        'openmarket': "200",
        'aerial': "200",
        'smsportal': "True",
        'smscentral': "0",
        'twilio': '<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        'messagebird': 'OK'
    }

    api_response = response_map.get(provider_name, json.dumps(response))
    logger.info("Final response = {}".format(api_response))

    return api_response


def transform_incoming_config(obj=None):
    return dict(
        product_id=obj.incoming_product_id,
        account_id=obj.account_id,
        keyword=obj.keyword,
        short_code=obj.short_code,
        push_to_url=obj.push_to_url,
        sub_keyword=obj.sub_keyword,
        http_method = obj.http_method,
        country_id=obj.country_id,
    )


class IncomingConfig(BaseResource):

    def get(self, customer_id=None, product_id=None):
        """
        @api {get} /v1/customer/{customer_id}/product/{product_id}/incoming/ Get Incoming configuration
        @apiName Get Incoming Configuration
        @apiVersion 1.0.0
        @apiGroup Incoming

        @apiHeader {String} apiKey Api key of onehop-api

        @apiparam {String} customer_id Customer ID
        @apiparam {String} product_id  Product ID

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
          "http_method": "GET"
          "product_id": "aerstsus-aryssysi-shsjs",
          "keyword": nul,
          "short_code": 123344o,
          "push_to_url": null,
          "country_id": "HR",
          "sub_keyword": null
        }


        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            "message" : "Error"
        }

        """
        try:
            params = dict(customer_id=customer_id, product_id=product_id)
            incoming_config = get_incoming_config_of_product(**params)
            m_session.commit()
            return transform_incoming_config(incoming_config)
        except ValueError as val_err:
            logger.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            logger.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except errors.NotFoundError as nf_err:
            logger.error(nf_err)
            m_session.rollback()
            return dict(
                product_id=product_id,
                keyword=None,
                short_code=None,
                push_to_url=None,
                sub_keyword=None,
                http_method=None,
                country_id=None,
            )
        except SQLAlchemyError as sa_err:
            crash_logger.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")

    def post(self, customer_id=None, product_id=None):
        """
        @api {post} /v1/customer/{customer_id}/product/{product_id}/incoming/ Save Incoming configuration
        @apiName Post Incoming Configuration
        @apiVersion 1.0.0
        @apiGroup Incoming

        @apiHeader {String} apiKey Api key of onehop-api
        @apiParam {String} customer_id Customer Id
        @apiParam {String} product_id Product Id
        @apiParam {String} keyword Keyword
        @apiParam {String} short_code Short Code
        @apiParam {String} push_to_url Incoming Push URL
        @apiParam {String} sub_keyword Sub Keyword
        @apiParam {String} http_method Http Method
        @apiParam {String} country_id Country Id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
            product_id=obj.incoming_product_id,
            account_id=obj.account_id,
            keyword=obj.keyword,
            short_code=obj.short_code,
            push_to_url=obj.push_to_url,
            sub_keyword=obj.sub_keyword,
            http_method = obj.http_method,
            country_id=obj.country_id,
        }

        """
        parser = reqparse.RequestParser()
        parser.add_argument('customer_id', type=unicode, required=True, help='ACCOUNT-REQ-CUSTOMER-ID')
        parser.add_argument('is_api_access', type=bool, required=False,
                                         help='ACCOUNT-REQ-CUSTOMER-IS-API-ACCESS')
        parser.add_argument('is_email_enabled', type=bool, required=False,
                                         help='ACCOUNT-REQ-IS-EMAIL-ENABLED')

        params = parser.parse_args()
        try:
            incoming_config = save_incoming_config_of_product(**params)
            m_session.commit()
            return transform_incoming_config(incoming_config)
        except ValueError as val_err:
            logger.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            logger.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except errors.NotFoundError as nf_err:
            logger.error(nf_err)
            m_session.rollback()
            return dict(
                product_id=product_id,
                keyword=None,
                short_code=None,
                push_to_url=None,
                sub_keyword=None,
                http_method=None,
                country_id=None,
            )
        except SQLAlchemyError as sa_err:
            crash_logger.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")
