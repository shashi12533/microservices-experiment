#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_restful import abort, reqparse, fields, marshal_with,inputs
from sqlalchemy.exc import SQLAlchemyError

from media_engine.helper import get_logger
from media_engine.lib.accounting import create_account, update_account, delete_account,get_account_flag_details
from media_engine.lib.errors import NotFoundError
from media_engine.lib.validators import authenticate_account
from media_engine.models import m_session
from media_engine.resources.base_resource import BaseResource as Resource

log = get_logger()
crash_log = get_logger('crash')


create_account_parser = reqparse.RequestParser()
create_account_parser.add_argument('customer_id', type=unicode, required=True, help='ACCOUNT-REQ-CUSTOMER-ID')

delete_account_parser = reqparse.RequestParser()
delete_account_parser.add_argument('customer_id', type=unicode, required=True, help='ACCOUNT-REQ-CUSTOMER-ID')

save_account_parser = reqparse.RequestParser()
save_account_parser.add_argument('customer_id', type=unicode, required=True, help='ACCOUNT-REQ-CUSTOMER-ID')
save_account_parser.add_argument('is_api_access', type=inputs.boolean, required=False, help='ACCOUNT-REQ-CUSTOMER-IS-API-ACCESS')
save_account_parser.add_argument('is_email_enabled', type=inputs.boolean, required=False, help='ACCOUNT-REQ-IS-EMAIL-ENABLED')
save_account_parser.add_argument('is_test_account', type=inputs.boolean, required=False, help='ACCOUNT-REQ-IS-TEST-ACCOUNT')
save_account_parser.add_argument('is_mms_enabled', type=inputs.boolean, required=False, help='ACCOUNT-REQ-IS-MMS-ENABLED')
save_account_parser.add_argument('is_office_hours_opt_out', type=inputs.boolean, required=False,
                                 help='ACCOUNT-REQ-IS-OFFICE-HOURS-OPT-OUT')
save_account_parser.add_argument('is_verified', type=inputs.boolean, required=False, help='ACCOUNT-REQ-IS-VERIFIED')



get_account_parser=reqparse.RequestParser()
get_account_parser.add_argument('customer_id', type=unicode, required=True, help='ACCOUNT-REQ-CUSTOMER-ID')


account_response_format = dict(
    account_id=fields.Integer,
    customer_id=fields.String,
    is_api_access=fields.Boolean,
    is_email_enabled=fields.Boolean,
    is_mms_enabled=fields.Boolean,
    is_office_hours_opt_out=fields.Boolean,
    is_test_account=fields.Boolean,
    is_verified=fields.Boolean,
)

account_delete_format = dict(
    status=fields.Boolean,
)


class Account(Resource):
    method_decorators = [authenticate_account]

    @marshal_with(account_response_format)
    def post(self):
        """
        @api {post} /v1/accounts/ Add new Account
        @apiVersion 1.0.0

        @apiName Add Account
        @apiGroup Accounts

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id Customer id

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
        params = create_account_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            account = create_account(**params)
            m_session.commit()
            log.debug('user account created'.format(account.id))
            return dict(
                account_id=account.id,
                customer_id=account.customer_id,
                is_api_access=account.is_api_access,
                is_office_hours_opt_out=account.is_office_hours_opt_out,
                is_email_enabled=account.is_email_enabled,
                is_test_account=account.is_test_account,
                is_verified=account.is_verified,
                is_mms_enabled=account.is_mms_enabled,
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

    @marshal_with(account_response_format)
    def put(self):
        """
        @api {put} /v1/accounts/ Update account
        @apiVersion 1.0.0

        @apiName Update Account
        @apiGroup Accounts

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id Customer id
        @apiParam {Boolean} is_api_access Has api access if True, else False
        @apiParam {Boolean} is_email_enabled Email enabled if True, else False
        @apiParam {Boolean} is_test_account Testing account if True, else False
        @apiParam {Boolean} is_mms_enabled MMS enabled if True, else False
        @apiParam {Boolean} is_office_hours_opt_out Opt out of office hours if True, else False
        @apiParam {Boolean} is_verified verified if True, else False

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
        params = save_account_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            account = update_account(**params)
            m_session.commit()
            return dict(
                account_id=account.id,
                customer_id=account.customer_id,
                is_api_access=account.is_api_access,
                is_email_enabled=account.is_email_enabled,
                is_mms_enabled=account.is_mms_enabled,
                is_office_hours_opt_out=account.is_office_hours_opt_out,
                is_test_account=account.is_test_account,
                is_verified=account.is_verified,
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

    @marshal_with(account_delete_format)
    def delete(self):
        """
        @api {delete} /v1/accounts/ Delete an Account
        @apiVersion 1.0.0

        @apiName Delete Account
        @apiGroup Accounts

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id Customer id

        @apiSuccessExample e.g. Success-Response
        HTTP/1.1 200 OK
        {
            "status": true
        }

        @apiErrorExample Bad Request
        HTTP/1.1 400 Bad Request
        {
            "message": "error message string"
        }
        """
        params = delete_account_parser.parse_args()
        try:
            status = delete_account(**params)
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

    @marshal_with(account_response_format)
    def get(self):
        """
        @api {get} /v1/accounts/ Get account Flag Details
        @apiVersion 1.0.0

        @apiName Get Account Flag Info
        @apiGroup Accounts

        @apiHeader {String} apiKey Api key of onehop-api
        @apiHeader {String} Content-Type content type

        @apiParam {String} customer_id Customer id

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
        params = get_account_parser.parse_args()
        log.debug('params : {}'.format(params))
        try:
            account = get_account_flag_details(**params)
            m_session.commit()
            return dict(
                account_id=account.id,
                customer_id=account.customer_id,
                is_api_access=account.is_api_access,
                is_email_enabled=account.is_email_enabled,
                is_mms_enabled=account.is_mms_enabled,
                is_office_hours_opt_out=account.is_office_hours_opt_out,
                is_test_account=account.is_test_account,
                is_verified=account.is_verified,
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
