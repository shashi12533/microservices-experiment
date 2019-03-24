from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.validators import authenticate_account
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.models import m_session
from media_engine.lib.errors import NotFoundError
from media_engine.lib.customer_details import get_unused_balance_for_customer_id
import json

log = get_logger()
crash_log = get_logger('crash')



get_unused_balance__parser = reqparse.RequestParser()
get_unused_balance__parser.add_argument('customer_ids', type=str,action='append',required=True, help='Please provide a valid list')






class CustomerDetails(Resource):

    method_decorators = [authenticate_account]
    def post(self):
        """
               @api {post} /v1/customer_detail/ Add new customer
               @apiVersion 1.0.0

               @apiName Add New Customer
               @apiGroup List Labels

               @apiHeader {String} apiKey Api key of onehop-api
               @apiHeader {String} Content-Type content type

               @apiparam {List} customer_ids Customer IDs
               for eg.
               {"customer_ids" : ["ab186850-9b28-45ec-9dd1-b8444368fb20","25505f5b-7982-4900-9d3e-d09df92ed9e6","b4cf5170-250d-48d2-8465-d8ffac5c77e2"]}

               @apiSuccessExample e.g. Success-Response
               HTTP/1.1 200 OK
               {
                  "ab186850-9b28-45ec-9dd1-b8444368fb20":
                  [
                    ["EUR",120  ],[ "GBP", 140 ],["INR", 135],["USD", 300]
                  ],
                  "25505f5b-7982-4900-9d3e-d09df92ed9e6":
                  [
                    ["INR", 47]
                  ],
                  "b4cf5170-250d-48d2-8465-d8ffac5c77e2":
                  [
                    ["EUR",115],["INR",15]
                  ]
                }


               @apiErrorExample Bad Request
               HTTP/1.1 400 Bad Request
               {
                   "message": "API-DB-ERR"
               }
        """

        params = get_unused_balance__parser .parse_args()
        log.debug('params : {}'.format(params))
        try:
            unused_balance = get_unused_balance_for_customer_id(**params)
            return unused_balance

        except ValueError as val_err:
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except NotFoundError as nf_err:
            log.error(nf_err)
            m_session.rollback()
            abort(400, message=nf_err.message)
        except SQLAlchemyError as sa_err:
            log.error(sa_err)
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")

    def get(self):
        params = get_status__parser.parse_args()
        log.debug('params : {}'.format(params))
        print 'PARAMS: ', params
        try:
            status = get_customer_status(**params)
            return status



        except ValueError as val_err:
            m_session.rollback()
            abort(400, message=val_err.message)
        except KeyError as key_err:
            log.error(key_err)
            m_session.rollback()
            abort(400, message=key_err.message)
        except NotFoundError as nf_err:
            log.error(nf_err)
            m_session.rollback()
            abort(400, message=nf_err.message)
        except SQLAlchemyError as sa_err:
            log.error(sa_err)
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")










