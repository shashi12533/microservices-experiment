#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_paginator import EmptyPage

from media_engine.helper import get_logger
from media_engine.lib.errors import NotFoundError
from media_engine.lib.sms_history import get_sms_status
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.lib.validators import customer_authenticate, required_param

logger = get_logger()
crash_log = get_logger('crash')

_response_format = dict(
    sms_id=fields.String,
    status=fields.String,
    delivered_on=fields.String,
)


class SmsStatus(Resource):

    method_decorators = [customer_authenticate]

    def __init__(self):
        self.request_parser = reqparse.RequestParser()
        self.request_parser.add_argument('apiKey', type=required_param, required=False, help='REQ-API-KEY')
        self.request_parser.add_argument('sms_id_list', type=list, required=True, help='REQ-SMS-ID-LIST', location='json')

    @marshal_with(_response_format)
    def post(self, account_id):
        """
        @api {post} /v1/sms/status SMS Status
        @apiVersion 1.0.0
        @apiName sms status
        @apiGroup SMS Status
        @apiHeader {String} apiKey Api key of onehop-api

        @apiparam account_id Account ID
        @apiParam {json} sms_id_list List of sms ids
        @apiParamExample {json} Request-Example:
        {
        "account_id":"1234567",
        "sms_id_list": ["bf612db8-91ff-446a-a92f-2238732eb37b", "576ca0f9-63dc-4261-863e-bff2a8d0d4ca", "aaa3bfd7-caa7-4e17-afdc-eb574a564622"]
        }

        @apiExample {curl} Example - curl
        curl -X POST -H "apiKey: sm82cd17ac1bbe43698a75f2fb0697ff6d" -H "Content-Type: application/json" -d '{"sms_id_list": ["bf612db8-91ff-446a-a92f-2238732eb37b", "576ca0f9-63dc-4261-863e-bff2a8d0d4ca", "aaa3bfd7-caa7-4e17-afdc-eb574a564622", "4533ee40-25f2-4d93-aada-f27decbc763f"]}' "http://api.onehop.co/v1/sms/status"
        @apiSuccessExample e.g. Success-Response

        HTTP/1.1 200 OK

        [
            {
                "sms_id": "bf612db8-91ff-446a-a92f-2238732eb37b",
                "status": "delivered",
                "delivered_on": "2016-10-04 11:30:00"
            },
            {
                "sms_id": "576ca0f9-63dc-4261-863e-bff2a8d0d4ca",
                "status": "undelivered",
                "delivered_on": "2016-10-04 11:30:01"
            },
            {
                "sms_id": "aaa3bfd7-caa7-4e17-afdc-eb574a564622",
                "status": "failed : INVALID-MOBILE-NUMBER",
                "delivered_on": "2016-10-04 11:30:02"
            },
            {
                "sms_id": "4533ee40-25f2-4d93-aada-f27decbc763f",
                "status": "failed : LABEL-NOT-FOUND",
                "delivered_on": "2016-10-04 11:30:02"
            },

        ]
        """

        params = self.request_parser.parse_args()
        params['account_id'] = account_id
        params.pop('apiKey', None)
        logger.info('params : {}'.format(params))

        try:
            sms_status_list = get_sms_status(**params)
            m_session.commit()
            return sms_status_list
        except ValueError as val_err:
            logger.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            logger.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except NotFoundError as nf_err:
            logger.error(nf_err)
            m_session.rollback()
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")
        except EmptyPage as emp_page:
            logger.error(emp_page)
            m_session.rollback()
            abort(400, message="BAD-PAGE")

