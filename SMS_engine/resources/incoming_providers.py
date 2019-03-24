#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse, fields, marshal_with
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource
from media_engine.lib.incoming_provider import add_incoming_provider, get_incoming_provider, \
    add_incoming_provider_param, get_incoming_provider_params,\
    delete_provider_param, delete_provider, update_incoming_provider_param, update_incoming_provider


create_provider_parser = reqparse.RequestParser()
create_provider_parser.add_argument('name', type=unicode, required=True, help='INCOMING-PROVIDER-NAME-REQ')
create_provider_parser.add_argument('api_name', type=unicode, required=True, help='INCOMING-PROVIDER-API-NAME-REQ')
create_provider_parser.add_argument('http_push_method', type=unicode, required=True, help='INCOMING-PROVIDER-HTTP-PUSH-METHOD')
create_provider_parser.add_argument('country_id', type=unicode, required=True, help='INCOMING-PROVIDER-COUNTRYID-REQ')
create_provider_parser.add_argument('http_url', type=unicode, required=True, help='INCOMING-PROVIDER-HTTP-URL-REQ')

update_provider_parser = reqparse.RequestParser()
update_provider_parser.add_argument('provider_id', type=unicode, required=True, help='INCOMING-PROVIDER-NAME-REQ')
update_provider_parser.add_argument('name', type=unicode, required=True, help='INCOMING-PROVIDER-NAME-REQ')
update_provider_parser.add_argument('api_name', type=unicode, required=True, help='INCOMING-PROVIDER-API-NAME-REQ')
update_provider_parser.add_argument('http_push_method', type=unicode, required=True, help='INCOMING-PROVIDER-HTTP-PUSH-METHOD')
update_provider_parser.add_argument('country_id', type=unicode, required=True, help='INCOMING-PROVIDER-COUNTRYID-REQ')
update_provider_parser.add_argument('http_url', type=unicode, required=True, help='INCOMING-PROVIDER-HTTP-URL-REQ')


get_incoming_provider_search = reqparse.RequestParser()
get_incoming_provider_search.add_argument('service_provider_id', type=unicode, required=True, help='INCOMING-PROVIDER-ID-REQ')

create_provider_param_parser = reqparse.RequestParser()
create_provider_param_parser.add_argument('incoming_provider_id', type=unicode, required=True, help='INCOMING-PROVIDER-PARAMS-ID-REQ')
create_provider_param_parser.add_argument('param_name', type=unicode, required=True, help='INCOMING-PROVIDER-PARAM-NAME')
create_provider_param_parser.add_argument('sm_param_name', type=unicode, required=True, help='INCOMING-PROVIDER-PARAM-SMNAME')

update_provider_param_parser = reqparse.RequestParser()
update_provider_param_parser.add_argument('provider_param_id', type=unicode, required=True, help='UPDATE-PROVIDER-PARAM')
update_provider_param_parser.add_argument('param_name', type=unicode, required=True, help='UPDATE-PROVIDER-PARAM-NAME')
update_provider_param_parser.add_argument('sm_param_name', type=unicode, required=True, help='UPDATE-PROVIDER-PARAM-SMNAME')

get_incoming_provider_param = reqparse.RequestParser()
get_incoming_provider_param.add_argument('incoming_provider_id', type=unicode, required=True, help='INCOMING-PROVIDER-PARAM-ID-REQ')

delete_provider_param_parser = reqparse.RequestParser()
delete_provider_param_parser.add_argument('provider_param_id', type=unicode, required=True, help='DELETE-PROVIDER-PARAM')

delete_provider_parser = reqparse.RequestParser()
delete_provider_parser.add_argument('provider_id', type=unicode, required=True, help='DELETE-PROVIDER-PROVIDERID-REQ')

log = get_logger()
crash_log = get_logger('crash')

provider_response_format = dict(
    id=fields.String,
    name=fields.String,
    api_name=fields.String,
    http_url=fields.String,
)

provider_param_response_format = dict(
    id=fields.String,
    name=fields.String,
    sm_name=fields.String,
)

delete_provider_param_format = dict(
    status=fields.Boolean,
)

class IncomingProviders(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(provider_response_format)
    def post(self):
        """
        @api {post} /v1/incoming_provider/ Add new Provider
        @apiVersion 1.0.0

        @apiName Add Provider
        @apiGroup Providers

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} name Provider Name
        @apiParam {String} api_name API Name
        @apiParam {String} http_push_method HTTP POST Method
        @apiParam {String} country_id Country Id
        @apiParam {String} http_url HTTP URL


        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "http_url": "null",
          "id": "752f49f8-4d65-452d-8ac9-dc68e8e3c97a",
          "api_name": "mywordapi",
          "name": "myword"
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
            provider = add_incoming_provider(**params)
            m_session.commit()
            log.debug('user account created'.format(provider.id))
            return dict(
                id=provider.id,
                name=provider.name,
                api_name=provider.api_name,
                http_url=provider.http_url,
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
        @api {post} /v1/incoming_provider/ Get Provider Detail
        @apiVersion 1.0.0

        @apiName Get Incoming Provider
        @apiGroup Incoming Providers

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} service_provider_id Service Provider id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK

        {
          "http_url": "<class 'flask_restful.fields.String'>",
          "id": "11208131-5d13-4ffb-a57a-773b537bd115",
          "api_name": "silverstreet",
          "name": "Silver Street"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-NOT-FOUND
        }
        """

        params = get_incoming_provider_search.parse_args()
        log.debug('params : {}'.format(params))

        try:
            get_incoming_providers = get_incoming_provider(**params)
            m_session.commit()
            return dict(
                id=get_incoming_providers.id,
                name=get_incoming_providers.name,
                api_name=get_incoming_providers.api_name,
                http_url=fields.String,
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

    @marshal_with(delete_provider_param_format)
    def delete(self):
        """
        @api {post} /v1/incoming_provider/ Delete Provider Detail
        @apiVersion 1.0.0

        @apiName Delete Incoming Provider
        @apiGroup Incoming Providers

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} provider_id Provider id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "status": true
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-NOT-FOUND
        }
        """
        params = delete_provider_parser.parse_args()
        try:
            status = delete_provider(**params)
            m_session.commit()
            return dict(status=status)
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
        @api {post} /v1/incoming_provider/ Update Provider Detail
        @apiVersion 1.0.0

        @apiName Delete Incoming Provider
        @apiGroup Incoming Providers

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} provider_param_id Provider Param id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
          "api_name": "ishwar",
          "http_url": "https://thiswhat.com",
          "id": "ccc20def-6b58-4af0-ac29-70e951d37d77",
          "name": "ishwar_gk"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-NOT-FOUND
        }
        """


        params = update_provider_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            provider_param = update_incoming_provider(**params)
            m_session.commit()
            return dict(
                id=provider_param.id,
                name=provider_param.name,
                api_name=provider_param.api_name,
                http_url=provider_param.http_url,
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


class IncomingProviderParams(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(provider_param_response_format)
    def post(self):
        """
        @api {post} /v1/incoming_provider_param/ Add Provider Params Detail
        @apiVersion 1.0.0

        @apiName Add Incoming Provider Params
        @apiGroup Incoming Providers

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} incoming_provider_id Provider id
        @apiParam {String} param_name Param Name
        @apiParam {String}  sm_param_name Param Value


        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
       {
          "sm_name": "code",
          "name": "short",
          "id": "ce5e0a72-74c8-4a5a-8d55-f5de7f59594e"
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            Exception: PROVIDER-NOT-FOUND
        }
        """
        params = create_provider_param_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            provider_param = add_incoming_provider_param(**params)
            m_session.commit()
            return dict(
                id=provider_param.incoming_provider_id,
                name=provider_param.param_name,
                sm_name=provider_param.sm_param_name,
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

    @marshal_with(provider_param_response_format)
    def get(self):

        """
            @api {post} /v1/incoming_provider_param/ Get Provider Params
            @apiVersion 1.0.0

            @apiName Get Incoming Provider Params
            @apiGroup Incoming Providers

            @apiHeader {String} apiKey Api key of onehop-api
            @apiHeader {String} Content-Type content type

            @apiParam {String} incoming_provider_id Provider id

            @apiSuccessExample e.g. Success-Response
            HTTP/1.1 200 OK
            [
              {
                "id": "58603f6a-b5aa-46a9-b6b0-35a3912020bd",
                "name": "mobile",
                "sm_name": "number"
              },
              {
                "id": "71064d1b-8804-45e2-99de-72505b5eaaaf",
                "name": "tesoo",
                "sm_name": "testooo"
              },
              {
                "id": "a4283ffc-fb12-4c1c-bb64-0c0d7babc211",
                "name": "mobile",
                "sm_name": "number"
              }
            ]

            @apiErrorExample Bad Request
            HTTP/1.1 400 Bad Request
            {
                Exception: PROVIDER-NOT-FOUND
            }
            """

        params = get_incoming_provider_param.parse_args()

        try:
            params_obj = get_incoming_provider_params(**params)
            m_session.commit()
            return [dict(
                id=a.id,
                name=a.param_name,
                sm_name=a.sm_param_name,
            ) for a in params_obj]

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


    @marshal_with(delete_provider_param_format)
    def delete(self):
        """
            @api {post} /v1/incoming_provider_param/ Delete Provider Params
            @apiVersion 1.0.0

            @apiName Delete Incoming Provider Params
            @apiGroup Incoming Providers

            @apiHeader {String} apiKey Api key of onehop-api
            @apiHeader {String} Content-Type content type

            @apiParam {String} provider_param_id Provider Param id

            @apiSuccessExample e.g. Success-Response
            HTTP/1.1 200 OK
            {
              "status": true
            }

            @apiErrorExample Bad Request
            HTTP/1.1 400 Bad Request
            {
                Exception: PROVIDER-PARAM-NOT-FOUND
            }
            """
        params = delete_provider_param_parser.parse_args()
        try:
            status = delete_provider_param(**params)
            m_session.commit()
            return dict(status=status)
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

    @marshal_with(provider_param_response_format)
    def put(self):

        """
            @api {post} /v1/incoming_provider_param/ Update Provider Params
            @apiVersion 1.0.0

            @apiName Update Incoming Provider Params
            @apiGroup Incoming Providers

            @apiHeader {String} apiKey Api key of onehop-api
            @apiHeader {String} Content-Type content type

            @apiParam {String} provider_param_id Provider Param id
            @apiParam {String} param_name Providere Param Name
            @apiParam {String} sm_param_name SM Param Name

            @apiSuccessExample e.g. Success-Response
            HTTP/1.1 200 OK
            {
              "id": "71064d1b-8804-45e2-99de-72505b5eaaaf",
              "name": "tesoo",
              "sm_name": "testooo"
            }

            @apiErrorExample Bad Request
            HTTP/1.1 400 Bad Request
            {
                Exception: PROVIDER-PARAM-NOT-FOUND
            }
            """

        params = update_provider_param_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            provider_param = update_incoming_provider_param(**params)
            m_session.commit()
            return dict(
                id=provider_param.id,
                name=provider_param.param_name,
                sm_name=provider_param.sm_param_name,
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