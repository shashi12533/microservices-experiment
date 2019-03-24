#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.apikey import generate_api_key
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

log = get_logger()
crash_log = get_logger('crash')


api_key_parser = reqparse.RequestParser()
api_key_parser.add_argument('customer_id', type=unicode, required=True, help='API-KEY-REQ-CUSTOMER-ID')


class Apikey(Resource):
    method_decorators = [authenticate_account]

    def post(self):
        """
        @api {post} /v1/api_key/generate/ Generate new apiKey
        @apiVersion 1.0.0
        @apiName generate_api_key
        @apiGroup Accounts

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id customer id

        @apiSuccess {String}  message
        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 201 OK
        {
            "account_id": 1,
            "api_key": "smafbfeae6e4604af6a2a1af5b92571227"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {"message": "error message string"}

        """
        params = api_key_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            api_key_obj = generate_api_key(**params)
            m_session.commit()
            return dict(
                account_id=api_key_obj.account_id,
                api_key=api_key_obj.api_key
            )
        except ValueError as val_err:
            log.error(val_err)
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except NotFoundError as nf_err:
            log.error(nf_err)
            m_session.rollback()
            abort(404, message=nf_err.message)
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")
