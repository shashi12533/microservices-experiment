
from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.lib.country import add_country,get_country,update_country,delete_country




log = get_logger()
crash_log = get_logger('crash')

country_response_format = dict(
    char_code=fields.String,
    country_name=fields.String,
    country_code=fields.Integer,
    mobile_number_length=fields.Integer,
    country_code_length=fields.Integer,
    is_top_country=fields.Boolean,
    created_on=fields.String,
    modified_on=fields.String,
    deleted_on=fields.String
)


add_country_parser = reqparse.RequestParser()

add_country_parser.add_argument('char_code', type=unicode, required=True, help='')
add_country_parser.add_argument('country_name', type=unicode, help='')
add_country_parser.add_argument('country_code', type=unicode, required=True,help='')
add_country_parser.add_argument('mobile_number_length', type=unicode, help='')
add_country_parser.add_argument('country_code_length', type=unicode,required=True, help='')
add_country_parser.add_argument('is_top_country', type=unicode,required=True , help='')

get_country_parser = reqparse.RequestParser()
get_country_parser.add_argument('country_char_code', type=unicode, required=True,
                                       help='GET-CHAR-CODE-REQUIRED')

update_country_parser = reqparse.RequestParser()
update_country_parser.add_argument('country_char_code', type=unicode, required=True, help='')
update_country_parser.add_argument('name', type=unicode, help='')
update_country_parser.add_argument('code', type=unicode, help='')
update_country_parser.add_argument('mobile_number_length', type=unicode, help='')
update_country_parser.add_argument('country_code_length', type=unicode, help='')
update_country_parser.add_argument('is_top_country', type=unicode, help='')


delete_country_parser = reqparse.RequestParser()
delete_country_parser.add_argument('country_char_code', type=unicode, required=True, help='COUNTRY-CHAR-CODE-REQ')


class Countries(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(country_response_format)
    def post(self):
        """
               @api {post} /v1/countries/ Add new Country
               @apiVersion 1.0.0

               @apiName Add Country
               @apiGroup Countries

               @apiHeader {String} apiKey Api key of onehop-api
               @apiHeader {String} Content-Type content type

               @apiParam {String} char_code Country Char Code
               @apiParam {String} country_name Country Name
               @apiParam {String} country_code Country Code
               @apiParam {String} mobile_number_length Mobile Number Length
               @apiParam {String} country_code_length Country Code Length
               @apiParam {String} is_top_country Is Top Country

               @apiSuccessExample e.g. Success-Response
               HTTP/1.1 200 OK
               {
                 "char_code": "TY",
                 "country_code": 34,
                 "country_code_length": 2,
                 "country_name": "India",
                 "created_on": "2016-11-24 16:17:07",
                 "deleted_on": null,
                 "is_top_country": true,
                 "mobile_number_length": 12,
                 "modified_on": "2016-11-24 16:17:07"
               }

               @apiErrorExample Bad Request
               HTTP/1.1 400 Bad Request
               {
                   "message": "API-DB-ERR"
               }

               """

        params = add_country_parser.parse_args()
        log.debug('params : {}'.format(params))

        try:
            country=add_country(**params)
            m_session.commit()
            return dict(
                char_code=country.char_code,
                country_name=country.name,
                country_code=country.code,
                mobile_number_length=country.mobile_number_length,
                country_code_length=country.country_code_length,
                is_top_country=country.is_top_country,
                created_on=country.created_on,
                modified_on=country.modified_on,
                deleted_on=country.deleted_on
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

    # to get a country
    @marshal_with(country_response_format)
    def get(self):
        """
           @api {get} /v1/countries/ Get Country Details
           @apiVersion 1.0.0

           @apiName get Country
           @apiGroup Country

           @apiParam {String} country_char_code Country Char Code

           @apiSuccessExample e.g. Success-Response
          {
          "char_code": "ZW",
          "country_code": 270,
          "country_code_length": 77,
          "country_name": "Zim",
          "created_on": "2016-10-21 15:05:09",
          "deleted_on": "1",
          "is_top_country": false,
          "mobile_number_length": 10,
          "modified_on": "2016-11-24 16:05:52"
        }

           @apiErrorExample Bad Request
           HTTP/1.1 400 Bad Request
           {
               Exception: COUNTRY--NOT-EXIST
           }

               """
        params = get_country_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            get_country_response = get_country(**params)
            m_session.commit()

            return dict(
                char_code=get_country_response.char_code,
                country_name=get_country_response.name,
                country_code=get_country_response.code,
                mobile_number_length=get_country_response.mobile_number_length,
                country_code_length=get_country_response.country_code_length,
                is_top_country=get_country_response.is_top_country,
                created_on=get_country_response.created_on,
                modified_on=get_country_response.modified_on,
                deleted_on=get_country_response.deleted_on
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






    @marshal_with(country_response_format)
    def put(self):

        """
        @api {put} /v1/country/ Update Country Detail
        @apiVersion 1.0.0

        @apiName Update Provider
        @apiGroup Country

        @apiParam {String} char_code Country Char Code
        @apiParam {String} country_name Country Name
        @apiParam {String} country_code Country Code
        @apiParam {String} mobile_number_length Mobile Number Length
        @apiParam {String} country_code_length Country Code Length
        @apiParam {String} is_top_country Is Top Country

        @apiSuccessExample e.g. Success-Response
        {
          "char_code": "ZW",
          "country_code": 263,
          "country_code_length": 2,
          "country_name": "Zim",
          "created_on": "2016-10-21 15:05:09",
          "deleted_on": "1",
          "is_top_country": false,
          "mobile_number_length": 10,
          "modified_on": "2016-11-24 16:27:40"
        }


        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: COUNTRY-NOT-EXIST
        }
            """

        params = update_country_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            country_obj = update_country(**params)
            m_session.commit()

            return dict(
                char_code=country_obj.char_code,
                country_name=country_obj.name,
                country_code=country_obj.code,
                mobile_number_length=country_obj.mobile_number_length,
                country_code_length=country_obj.country_code_length,
                is_top_country=country_obj.is_top_country,
                created_on=country_obj.created_on,
                modified_on=country_obj.modified_on,
                deleted_on=country_obj.deleted_on
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


    def delete(self):
        """
       @api {delete} /v1/country/ Delete Country
       @apiVersion 1.0.0

       @apiName Delete Country
       @apiGroup Country

       @apiParam {String} char_code Country Char Code

       @apiSuccessExample e.g. Success-Response

        HTTP/1.1 200 OK
        {
          "status": true
        }


       @apiErrorExample Bad Request
       HTTP/1.1 400 Bad Request
       {
           Exception: COUNTRY-DOES-NOT-EXISTS
       }
    """



        params = delete_country_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            status = delete_country(**params)
            m_session.commit()
            return dict(
                status=status
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




