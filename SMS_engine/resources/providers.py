#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.lib.provider import add_provider, update_provider, add_params,\
    get_params, delete_provider_params, update_provider_param, delete_provider, get_provider, add_provider_config, \
    update_provider_config, delete_provider_config, get_provider_config

log = get_logger()
crash_log = get_logger('crash')

create_provider_parser = reqparse.RequestParser()
create_provider_parser.add_argument('provider_name', type=unicode, required=True, help='PROVIDER-REQ-NAME')
create_provider_parser.add_argument('api_url', type=unicode, required=True, help='PROVIDER-REQ-APIURL')
create_provider_parser.add_argument('country_code', type=unicode, required=True, help='PROVIDER-REQ-COUNTRY-CODE')
create_provider_parser.add_argument('module', type=unicode, required=True, help='PROVIDER-REQ-MODULE-NAME')
create_provider_parser.add_argument('pack_type', type=unicode, required=False, help='PROVIDER-REQ-PACKAGE-TYPE')
create_provider_parser.add_argument('is_mms_enabled', type=bool, required=False, help='PROVIDER-REQ-ISMMS-ENABLED')
create_provider_parser.add_argument('address', type=unicode, required=False, help='PROVIDER-REQ-ADDRESS')
create_provider_parser.add_argument('contact', type=unicode, required=False, help='PROVIDER-REQ-CONTACT')
create_provider_parser.add_argument('api_port', type=unicode, required=False, help='PROVIDER-REQ-API-PORT')
create_provider_parser.add_argument('send_sms_function', type=unicode, required=False,
                                    help='PROVIDER-REQ-SEND-SMS-FUNCTION')
create_provider_parser.add_argument('is_default', type=unicode, required=False, help='PROVIDER-REQ-IS-DEFAULT')
create_provider_parser.add_argument('dummy_status', type=unicode, required=False, help='PROVIDER-REQ-DUMMY-STATUS')
create_provider_parser.add_argument('route_tag', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TAG')
create_provider_parser.add_argument('balance_check_url', type=unicode, required=False,
                                    help='PROVIDER-REQ-BALANCE-CHECK-URL')
create_provider_parser.add_argument('mms_api_url', type=unicode, required=False, help='PROVIDER-REQ-MMS-API-URL')
create_provider_parser.add_argument('route_type', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TYPE')
create_provider_parser.add_argument('pack_type', type=unicode, required=False, help='PROVIDER-REQ-PACKAGE-TYPE')
create_provider_parser.add_argument('pack_type', type=unicode, required=False, help='PROVIDER-REQ-PACKAGE-TYPE')

update_provider_parser = reqparse.RequestParser()
update_provider_parser.add_argument('id', type=unicode, required=True, help='')
update_provider_parser.add_argument('provider_name', type=unicode, required=True, help='PROVIDER-REQ-NAME')
update_provider_parser.add_argument('api_url', type=unicode, required=False, help='PROVIDER-REQ-APIURL')
update_provider_parser.add_argument('country_code', type=unicode, required=False, help='PROVIDER-REQ-COUNTRY-CODE')
update_provider_parser.add_argument('module', type=unicode, required=False, help='PROVIDER-REQ-MODULE-NAME')
update_provider_parser.add_argument('pack_type', type=unicode, required=False, help='PROVIDER-REQ-PACKAGE-TYPE')
update_provider_parser.add_argument('is_mms_enabled', type=bool, required=False, help='PROVIDER-REQ-ISMMS-ENABLED')
update_provider_parser.add_argument('address', type=unicode, required=False, help='PROVIDER-REQ-ADDRESS')
update_provider_parser.add_argument('contact', type=unicode, required=False, help='PROVIDER-REQ-CONTACT')
update_provider_parser.add_argument('api_port', type=unicode, required=False, help='PROVIDER-REQ-API-PORT')
update_provider_parser.add_argument('send_sms_function', type=unicode, required=False,
                                    help='PROVIDER-REQ-SEND-SMS-FUNCTION')
update_provider_parser.add_argument('is_default', type=unicode, required=False, help='PROVIDER-REQ-IS-DEFAULT')
update_provider_parser.add_argument('dummy_status', type=unicode, required=False, help='PROVIDER-REQ-DUMMY-STATUS')
update_provider_parser.add_argument('route_tag', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TAG')
update_provider_parser.add_argument('balance_check_url', type=unicode, required=False,
                                    help='PROVIDER-REQ-BALANCE-CHECK-URL')
update_provider_parser.add_argument('mms_api_url', type=unicode, required=False, help='PROVIDER-REQ-MMS-API-URL')
update_provider_parser.add_argument('route_type', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TYPE')

add_provider_param_parser = reqparse.RequestParser()
add_provider_param_parser.add_argument('service_provider_id', type=unicode, required=True,
                                       help='PROVIDER-PARAM-PROVIDERID')
add_provider_param_parser.add_argument('param_name', type=unicode, required=True, help='PROVIDER-PARAM-PARAMNAME')
add_provider_param_parser.add_argument('param_value', type=unicode, required=True, help='PROVIDER-PARAM-VALUE')
add_provider_param_parser.add_argument('run_time_value', type=unicode, required=True,
                                       help='PROVIDER-PARAM-RUN-TIME-VALUE')
add_provider_param_parser.add_argument('encoding', type=unicode, required=True, help='PROVIDER-PARAM-ENCODING')
add_provider_param_parser.add_argument('in_query_string', type=unicode, required=True,
                                       help='PROVIDER-PARAM-IN-QUERY-STRING')
add_provider_param_parser.add_argument('is_mms_param', type=unicode, required=True, help='PROVIDER-PARAM-ISMMS-PARAM')

get_provider_param_format = reqparse.RequestParser()
get_provider_param_format.add_argument('service_provider_id', type=unicode, required=True,
                                       help='GET-PROVIDER-ID-REQUIRED')

get_provider_parser = reqparse.RequestParser()
get_provider_parser.add_argument('service_provider_id', type=unicode, required=True,
                                       help='GET-PROVIDER-ID-REQUIRED')


delete_provider_param_parser = reqparse.RequestParser()
delete_provider_param_parser.add_argument('provider_param_id', type=unicode, required=True, help='PROVIDER-PARAM-ID-REQ')

delete_provider_parser = reqparse.RequestParser()
delete_provider_parser.add_argument('service_provider_id', type=unicode, required=True, help='PROVIDER-PARAM-ID-REQ')


update_provider_param_parser = reqparse.RequestParser()
update_provider_param_parser.add_argument('id', type=unicode, required=True, help='PROVIDER-PARAM-ID-REQ')
update_provider_param_parser.add_argument('service_provider_id', type=unicode, required=True,
                                       help='PROVIDER-PARAM-PROVIDERID')
update_provider_param_parser.add_argument('param_name', type=unicode, required=True, help='PROVIDER-PARAM-PARAMNAME')
update_provider_param_parser.add_argument('param_value', type=unicode, required=True, help='PROVIDER-PARAM-VALUE')
update_provider_param_parser.add_argument('run_time_value', type=unicode, required=True,
                                       help='PROVIDER-PARAM-RUN-TIME-VALUE')
update_provider_param_parser.add_argument('encoding', type=unicode, required=True, help='PROVIDER-PARAM-ENCODING')
update_provider_param_parser.add_argument('in_query_string', type=unicode, required=True,
                                       help='PROVIDER-PARAM-IN-QUERY-STRING')
update_provider_param_parser.add_argument('is_mms_param', type=unicode, required=True, help='PROVIDER-PARAM-ISMMS-PARAM')



create_provider_config_parser = reqparse.RequestParser()
create_provider_config_parser.add_argument('name', type=unicode, required=True, help='PROVIDER-REQ-NAME')
create_provider_config_parser.add_argument('api_url', type=unicode, required=True, help='PROVIDER-REQ-APIURL')
create_provider_config_parser.add_argument('country_code', type=unicode, required=True, help='PROVIDER-REQ-COUNTRY-CODE')
create_provider_config_parser.add_argument('module', type=unicode, required=True, help='PROVIDER-REQ-MODULE-NAME')
create_provider_config_parser.add_argument('address', type=unicode, required=False, help='PROVIDER-REQ-ADDRESS')
create_provider_config_parser.add_argument('contact', type=unicode, required=False, help='PROVIDER-REQ-CONTACT')
create_provider_config_parser.add_argument('api_port', type=unicode, required=False, help='PROVIDER-REQ-API-PORT')
create_provider_config_parser.add_argument('send_sms_function', type=unicode, required=False,
                                    help='PROVIDER-REQ-SEND-SMS-FUNCTION')
create_provider_config_parser.add_argument('dummy_status', type=unicode, required=False, help='PROVIDER-REQ-DUMMY-STATUS')
create_provider_config_parser.add_argument('route_tag', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TAG')
create_provider_config_parser.add_argument('balance_check_url', type=unicode, required=False,
                                    help='PROVIDER-REQ-BALANCE-CHECK-URL')
create_provider_config_parser.add_argument('mms_api_url', type=unicode, required=False, help='PROVIDER-REQ-MMS-API-URL')
create_provider_config_parser.add_argument('route_type', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TYPE')

update_provider_parser = reqparse.RequestParser()
update_provider_parser.add_argument('id', type=unicode, required=True, help='')
update_provider_parser.add_argument('name', type=unicode, required=True, help='PROVIDER-REQ-NAME')
update_provider_parser.add_argument('api_url', type=unicode, required=False, help='PROVIDER-REQ-APIURL')
update_provider_parser.add_argument('country_code', type=unicode, required=False, help='PROVIDER-REQ-COUNTRY-CODE')
update_provider_parser.add_argument('module', type=unicode, required=False, help='PROVIDER-REQ-MODULE-NAME')
update_provider_parser.add_argument('address', type=unicode, required=False, help='PROVIDER-REQ-ADDRESS')
update_provider_parser.add_argument('contact', type=unicode, required=False, help='PROVIDER-REQ-CONTACT')
update_provider_parser.add_argument('api_port', type=unicode, required=False, help='PROVIDER-REQ-API-PORT')
update_provider_parser.add_argument('send_sms_function', type=unicode, required=False,
                                    help='PROVIDER-REQ-SEND-SMS-FUNCTION')
update_provider_parser.add_argument('dummy_status', type=unicode, required=False, help='PROVIDER-REQ-DUMMY-STATUS')
update_provider_parser.add_argument('route_tag', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TAG')
update_provider_parser.add_argument('balance_check_url', type=unicode, required=False,
                                    help='PROVIDER-REQ-BALANCE-CHECK-URL')
update_provider_parser.add_argument('mms_api_url', type=unicode, required=False, help='PROVIDER-REQ-MMS-API-URL')
update_provider_parser.add_argument('route_type', type=unicode, required=False, help='PROVIDER-REQ-ROUTE-TYPE')



provider_response_format = dict(
    provider_id=fields.Integer,
    provider_name=fields.String,
    api_url=fields.String,
    api_port=fields.String,
    country_code=fields.String,
    module=fields.String,
    balance_check_url=fields.String,
    is_mms_enabled=fields.Boolean,
    mms_api_url=fields.String,
)

provider_delete_format = dict(
    provider_id=fields.Integer
)

provider_param_format = dict(
    provider_id=fields.Integer,
    param_id=fields.Integer
)

delete_provider_param_return_pattern = dict(
    status=fields.Boolean,
)

delete_provider_return_pattern = dict(
    status=fields.Boolean,
)


get_provider_param_return_format = dict(
    id=fields.Integer,
    service_provider_id=fields.Integer,
    param_name=fields.String,
    param_value=fields.String,
    run_time_value=fields.Integer,
    encoding=fields.Integer,
    in_query_string=fields.Integer,
    is_mms_param=fields.Integer
)

get_provider_param_return_format_list = dict(
    id=fields.Integer,
    params=fields.List(fields.Nested(get_provider_param_return_format))
)


def transform_param(record=None):
    return dict(
        id=fields.Integer,
        service_provider_id=fields.Integer,
        param_name=fields.String,
        param_value=fields.String,
        run_time_value=fields.Integer,
        encoding=fields.Integer,
        in_query_string=fields.Integer,
        is_mms_param=fields.Integer
    )


class Providers(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(provider_response_format)
    def post(self):
        """
        @api {post} /v1/providers Add new Account
        @apiVersion 1.0.0

        @apiName Add Provider
        @apiGroup Provider

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} provider_name Provider id
        @apiParam {String} api_url API URL
        @apiParam {String} country_code Country Code
        @apiParam {String} send_sms_function Send SMS Function
        @apiParam {String} module Module
        @apiParam {String} is_mms_enabled Is MMS Enabled

        @apiSuccessExample e.g. Success-Response

        HTTP/1.1 200 OK
        {
            "customer_id": "12345",
            "is_api_access": true,
            "is_email_enabled": true,
            "is_mms_enabled": false,
            "is_office_hours_opt_out": false,
            "is_test_account": true,
            "is_verified": true
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            "message": "error message string"
        }
        """


        params = create_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            provider = add_provider(**params)
            m_session.commit()
            log.debug('user account created'.format(provider.id))
            return dict(
                provider_id=fields.Integer,
                provider_name=fields.String,
                api_url=fields.String,
                api_port=fields.String,
                country_code=fields.Integer,
                module=fields.String,
                balance_check_url=fields.String,
                is_mms_enabled=fields.Boolean,
                mms_api_url=fields.String,
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

    @marshal_with(provider_response_format)
    def get(self):
        """
        @api {post} /v1/provider/ Get Provider's Detail
        @apiVersion 1.0.0

        @apiName get Provider
        @apiGroup Provider

        @apiParam {String} service_provider_id Service Provider Id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "api_port": "5678",
          "api_url": "https://my.smpp.com.ua/xml/",
          "balance_check_url": "tyuio",
          "country_code": "RO",
          "is_mms_enabled": true,
          "mms_api_url": "r",
          "module": "smsclub",
          "provider_id": 8588817,
          "provider_name": "Sms Club"
        }



        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-DOES-NOT-EXISTS
        }

        """
        params = get_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            get_provider_response = get_provider(**params)
            m_session.commit()

            return dict(
                provider_id=get_provider_response.id,
                provider_name=get_provider_response.name,
                api_url=get_provider_response.api_url,
                api_port=get_provider_response.api_port,
                country_code=get_provider_response.country_code,
                module=get_provider_response.module,
                balance_check_url=get_provider_response.balance_check_url,
                is_mms_enabled=get_provider_response.is_mms_enabled,
                mms_api_url=get_provider_response.mms_api_url,
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

    @marshal_with(delete_provider_return_pattern)
    def delete(self):
        """
        @api {post} /v1/provider/ Delete Provider's Detail
        @apiVersion 1.0.0

        @apiName delete Provider
        @apiGroup Provider

        @apiParam {String} service_provider_id Service Provider Id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "status": true
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-DOES-NOT-EXISTS
        }
        """
        params = delete_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            status = delete_provider(**params)
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

    @marshal_with(provider_response_format)
    def put(self):
        """
        @api {post} /v1/provider/ Update Provider's Detail
        @apiVersion 1.0.0

        @apiName Update Provider
        @apiGroup Provider


        @apiParam {String} id Provider id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "provider_id": 28,
          "api_url": "https://api.silverstreet.com/send.php?",
          "module": "dm",
          "is_mms_enabled": false,
          "mms_api_url": null,
          "api_port": "0",
          "balance_check_url": null,
          "country_code": "ES",
          "provider_name": "Gms"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-DOES-NOT-EXISTS
        }
        """
        params = update_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            params = update_provider_parser.parse_args()
            provider_obj = update_provider(**params)
            m_session.commit()

            return dict(
                provider_id=provider_obj.id,
                provider_name=provider_obj.name,
                api_url=provider_obj.api_url,
                api_port=provider_obj.api_port,
                country_code=provider_obj.country_code,
                module=provider_obj.module,
                balance_check_url=provider_obj.balance_check_url,
                is_mms_enabled=provider_obj.is_mms_enabled,
                mms_api_url=provider_obj.mms_api_url,
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


class ProviderParams(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(provider_param_format)
    def post(self):
        """
        @api {post} /v1/provider_params/ Add Provider Params
        @apiVersion 1.0.0

        @apiName Add Provider Param
        @apiGroup Provider Param

        @apiParam {String} service_provider_id Service Provider Id
        @apiParam {String} param_name Param Name
        @apiParam {String} param_value Param Value
        @apiParam {String} run_time_value Run Time Value
        @apiParam {String} encoding Encoding
        @apiParam {String} in_query_string In Query String
        @apiParam {String} is_mms_param Is MMS PARAM

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "param_id": 111,
          "provider_id": 8588817
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
          "message": {
            "service_provider_id": "PROVIDER-PARAM-PROVIDERID"
          }
        }

        """
        params = add_provider_param_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            add_param = add_params(**params)
            m_session.commit()
            return dict(
                provider_id=add_param.service_provider_id,
                param_id=add_param.id
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

    @marshal_with(get_provider_param_return_format)
    def get(self):

        """
            @api {post} /v1/provider_params/ Get Provider Params
            @apiVersion 1.0.0

            @apiName Get Provider Param
            @apiGroup Provider Param

            @apiParam {String} service_provider_id Service Provider Id

            @apiSuccessExample e.g. Success-Response
            HTTP/1.1 200 OK
            [
              {
                "encoding": 1,
                "id": 109,
                "in_query_string": 1,
                "is_mms_param": 0,
                "param_name": "usr",
                "param_value": "ishwar",
                "run_time_value": 0,
                "service_provider_id": 8588817
              },
              {
                "encoding": 1,
                "id": 110,
                "in_query_string": 1,
                "is_mms_param": 0,
                "param_name": "ishwar12",
                "param_value": "ishwar_1",
                "run_time_value": 1,
                "service_provider_id": 8588817
              },
              {
                "encoding": 1,
                "id": 111,
                "in_query_string": 1,
                "is_mms_param": 0,
                "param_name": "usr",
                "param_value": "ishwar",
                "run_time_value": 0,
                "service_provider_id": 8588817
              }
            ]

            @apiErrorExample Bad Request
            HTTP/1.1 400 Bad Request
            {
              "message": {
                "service_provider_id": "GET-PROVIDER-ID-REQUIRED"
              }
            }

            """

        params = get_provider_param_format.parse_args()
        log.debug('params : {}'.format(params))
        try:
            get_param = get_params(**params)
            m_session.commit()

            return [dict(
                id=a.id,
                service_provider_id=a.service_provider_id,
                param_name=a.param_name,
                param_value=a.param_value,
                run_time_value=a.run_time_value,
                encoding=a.encoding,
                in_query_string=a.in_query_string,
                is_mms_param=a.is_mms_param
            ) for a in get_param]
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

    @marshal_with(delete_provider_param_return_pattern)
    def delete(self):
        """
        @api {post} /v1/provider_params/ Delete Provider Params
        @apiVersion 1.0.0

        @apiName Delete Provider Param
        @apiGroup Provider Param

        @apiParam {String} provider_param_id Service Provider Param Id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "status": true
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
          "message": {
            "service_provider_id": "PROVIDER-PARAM-NOT-FOUND"
          }
        }
        """

        params = delete_provider_param_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            status = delete_provider_params(**params)
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

    @marshal_with(get_provider_param_return_format)
    def put(self):

        """
            @api {post} /v1/provider_params/ Update Provider Params
            @apiVersion 1.0.0

            @apiName Update Provider Param
            @apiGroup Provider Param

            @apiParam {String} id Service Provider Param Id
            @apiParam {String} service_provider_id Service Provider Id
            @apiParam {String} param_name Param Name
            @apiParam {String} param_value Param Value
            @apiParam {String} run_time_value run time value
            @apiParam {String} encoding encoding
            @apiParam {String} in_query_string in query string
            @apiParam {String} is_mms_param is MMS Param

            @apiSuccessExample e.g. Success-Response
            HTTP/1.1 200 OK
            {
              "encoding": 1,
              "id": 110,
              "in_query_string": 1,
              "is_mms_param": 0,
              "param_name": "ishwar",
              "param_value": "ishwar_123",
              "run_time_value": 1,
              "service_provider_id": 8588817
            }

            @apiErrorExample Bad Request
            HTTP/1.1 400 Bad Request
            {
              "message": {
                "service_provider_id": "PROVIDER-PARAM-NOT-FOUND"
              }
            }
            """

        params = update_provider_param_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            provider_param = update_provider_param(**params)
            m_session.commit()
            return dict(
                id=provider_param.id,
                service_provider_id=provider_param.service_provider_id,
                param_name=provider_param.param_name,
                param_value=provider_param.param_value,
                run_time_value=provider_param.run_time_value,
                encoding=provider_param.encoding,
                in_query_string=provider_param.in_query_string,
                is_mms_param=provider_param.is_mms_param,
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


class ProvidersConfig(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(provider_response_format)
    def post(self):
        """
        @api {post} /v1/providers Add new Account
        @apiVersion 1.0.0

        @apiName Add Provider
        @apiGroup Provider

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} provider_name Provider id
        @apiParam {String} api_url API URL
        @apiParam {String} country_code Country Code
        @apiParam {String} send_sms_function Send SMS Function
        @apiParam {String} module Module
        @apiParam {String} is_mms_enabled Is MMS Enabled

        @apiSuccessExample e.g. Success-Response

        HTTP/1.1 200 OK
        {
            "customer_id": "12345",
            "is_api_access": true,
            "is_email_enabled": true,
            "is_mms_enabled": false,
            "is_office_hours_opt_out": false,
            "is_test_account": true,
            "is_verified": true
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            "message": "error message string"
        }
        """

        params = create_provider_config_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            provider = add_provider_config(**params)
            m_session.commit()
            log.debug('user account created'.format(provider.id))
            return dict(
                provider_id=fields.Integer,
                provider_name=fields.String,
                api_url=fields.String,
                api_port=fields.String,
                country_code=fields.Integer,
                module=fields.String,
                balance_check_url=fields.String,
                is_mms_enabled=fields.Boolean,
                mms_api_url=fields.String,
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

    @marshal_with(provider_response_format)
    def get(self):
        """
        @api {post} /v1/provider/ Get Provider's Detail
        @apiVersion 1.0.0

        @apiName get Provider
        @apiGroup Provider

        @apiParam {String} service_provider_id Service Provider Id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "api_port": "5678",
          "api_url": "https://my.smpp.com.ua/xml/",
          "balance_check_url": "tyuio",
          "country_code": "RO",
          "is_mms_enabled": true,
          "mms_api_url": "r",
          "module": "smsclub",
          "provider_id": 8588817,
          "provider_name": "Sms Club"
        }



        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-DOES-NOT-EXISTS
        }

        """
        params = get_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            get_provider_response = get_provider(**params)
            m_session.commit()

            return dict(
                provider_id=get_provider_response.id,
                provider_name=get_provider_response.name,
                api_url=get_provider_response.api_url,
                api_port=get_provider_response.api_port,
                country_code=get_provider_response.country_code,
                module=get_provider_response.module,
                balance_check_url=get_provider_response.balance_check_url,
                is_mms_enabled=get_provider_response.is_mms_enabled,
                mms_api_url=get_provider_response.mms_api_url,
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

    @marshal_with(delete_provider_return_pattern)
    def delete(self):
        """
        @api {post} /v1/provider/ Delete Provider's Detail
        @apiVersion 1.0.0

        @apiName delete Provider
        @apiGroup Provider

        @apiParam {String} service_provider_id Service Provider Id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "status": true
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-DOES-NOT-EXISTS
        }
        """
        params = delete_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            status = delete_provider(**params)
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

    @marshal_with(provider_response_format)
    def put(self):
        """
        @api {post} /v1/provider/ Update Provider's Detail
        @apiVersion 1.0.0

        @apiName Update Provider
        @apiGroup Provider


        @apiParam {String} id Provider id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "provider_id": 28,
          "api_url": "https://api.silverstreet.com/send.php?",
          "module": "dm",
          "is_mms_enabled": false,
          "mms_api_url": null,
          "api_port": "0",
          "balance_check_url": null,
          "country_code": "ES",
          "provider_name": "Gms"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-DOES-NOT-EXISTS
        }
        """
        params = update_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            params = update_provider_parser.parse_args()
            provider_obj = update_provider(**params)
            m_session.commit()

            return dict(
                provider_id=provider_obj.id,
                provider_name=provider_obj.name,
                api_url=provider_obj.api_url,
                api_port=provider_obj.api_port,
                country_code=provider_obj.country_code,
                module=provider_obj.module,
                balance_check_url=provider_obj.balance_check_url,
                is_mms_enabled=provider_obj.is_mms_enabled,
                mms_api_url=provider_obj.mms_api_url,
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

