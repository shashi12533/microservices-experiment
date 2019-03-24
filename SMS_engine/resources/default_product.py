from flask_restful import abort, reqparse, fields, marshal_with, inputs
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.validators import authenticate_account
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.models import m_session
from media_engine.lib.errors import NotFoundError
from media_engine.lib.default_product import save_default_product, get_default_product

log = get_logger()
crash_log = get_logger('crash')

default_product_response_format = dict(
    id=fields.String,
    product_id=fields.String,
    subtype=fields.String,
    country_code=fields.String,
    is_active=fields.Boolean
)

add_default_product_parser = reqparse.RequestParser()
# below are params for request
add_default_product_parser.add_argument('product_id', type=unicode, required=True,
                                        help='Please Enter a valid product id')
add_default_product_parser.add_argument('subtype', type=unicode, required=True, help='Please Enter a valid subtype')
add_default_product_parser.add_argument('country_code', type=unicode, required=True,
                                        help='Please Enter a valid country code')
add_default_product_parser.add_argument('is_active', type=inputs.boolean, help='')
add_default_product_parser.add_argument('customer_id', type=unicode, required=True,
                                        help='Please Enter a valid customer id')

get_default_product_parser = reqparse.RequestParser()
get_default_product_parser.add_argument('product_id', type=unicode, required=True,
                                        help='Please Enter a valid product id')
get_default_product_parser.add_argument('subtype', type=unicode, required=True, help='Please Enter a valid subtype')
get_default_product_parser.add_argument('country_code', type=unicode, required=True,
                                        help='Please Enter a valid country code')
get_default_product_parser.add_argument('customer_id', type=unicode, required=True,
                                        help='Please Enter a valid customer id')


class DefaultProduct(Resource):
    """
        @api {post} /v1/default_product Add new default product
        @apiVersion 1.0.0

        @apiName Add Default product
        @apiGroup DefaultProduct

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type


        @apiParam {String} product_id Product ID
        @apiParam {String} customer_id Customer ID
        @apiParam {String} subtype Subtype
        @apiParam {String} country_code Country Code

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "subtype": "short",
          "is_active": true,
          "product_id": "abc",
          "country_code": "IN",
          "id": "5e527d59-80f2-4679-a369-9d34469d73af"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            "message": "Error"
        }
        """
    method_decorators = [authenticate_account]

    @marshal_with(default_product_response_format)
    def post(self):
        params = add_default_product_parser.parse_args()

        log.debug('params : {}'.format(params))
        print 'PARAMS: ', params

        try:
            default_product = save_default_product(**params)
            m_session.commit()
            return dict(
                product_id=default_product.product_id,
                country_code=default_product.country_code,
                subtype=default_product.subtype,
                is_active=default_product.is_active,
                id=default_product.id
            )

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

    @marshal_with(default_product_response_format)
    def get(self):
        """
           @api {get} /v1/countries/ Get Default Product Details
           @apiVersion 1.0.0

           @apiName get Default Product
           @apiGroup DefaultProduct

            @apiParam {String} product_id Product ID
            @apiParam {String} customer_id Customer ID
            @apiParam {String} subtype Subtype
            @apiParam {String} country_code Country Code

           @apiSuccessExample e.g. Success-Response
           {
              "subtype": "short",
              "is_active": true,
              "product_id": "abc",
              "country_code": "US",
              "id": "b1218c20-40d5-49cc-bcbc-97cf70e86d73"
            }

           @apiErrorExample Bad Request
           HTTP/1.1 400 Bad Request
           {
               Exception: DEFAULT--PRODUCT--NOT-EXIST
           }

        """
        params = get_default_product_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            default_product = get_default_product(**params)
            m_session.commit()

            return dict(
                product_id=default_product.product_id,
                country_code=default_product.country_code,
                subtype=default_product.subtype,
                is_active=default_product.is_active,
                id=default_product.id
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
            abort(400, message=nf_err.message)
        except SQLAlchemyError as sa_err:
            crash_log.exception(sa_err)
            m_session.rollback()
            abort(500, message="API-ERR-DB")
        except Exception as e:
            log.error(e)
            abort(500, message=e.message)
