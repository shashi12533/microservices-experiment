from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.validators import authenticate_account
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.models import m_session
from media_engine.lib.errors import NotFoundError
from media_engine.lib.get_status import get_customer_status


log = get_logger()
crash_log = get_logger('crash')

get_status__parser = reqparse.RequestParser()
get_status__parser.add_argument('customer_ids', type=str, action='append',required=True, help='Please provide a valid list')
get_status__parser.add_argument('from_date', type=str,required=True, help='Please provide from date')
get_status__parser.add_argument('to_date', type=str,required=True, help='Please provide to date')


class GetStatus(Resource):

    method_decorators = [authenticate_account]
    def post(self):
        """
               @api {post} /v1/get_status Add get status of customer
               @apiVersion 1.0.0

               @apiName Get Customer Status
               @apiGroup Customer Status

               @apiHeader {String} apiKey Api key of onehop-api
               @apiHeader {String} Content-Type content type

               @apiparam {List} customer_ids Customer IDs
               @apiparam String  from_date From Date
               @apiparam {List} to_date To_Date


               @apiSuccessExample e.g. Success-Response
               HTTP/1.1 200 OK
               [
                  {
                    "status": "inactive",
                    "customer_id": "25505f5b-7982-4900-9d3e-d09df92ed9e6"
                  },
                  {
                    "status": "inactive",
                    "customer_id": "b4cf5170-250d-48d2-8465-d8ffac5c77e2"
                  },
                  {
                    "status": "inactive",
                    "customer_id": "3354de1b-eabe-44f3-b251-5e6527c4387c"
                  }
                ]
               @apiErrorExample Bad Request
               HTTP/1.1 400 Bad Request
               {
                   "message": "API-DB-ERR"
               }
        """
        params = get_status__parser.parse_args()
        print 'Params: ',params
        log.debug('params : {}'.format(params))
        try:
            res = get_customer_status(**params)
            return res

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









